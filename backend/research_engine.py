"""
research_engine.py — Core asynchronous research agent.

Optimised for speed + volume:
  - Single-pass extraction (multiple RAG retrievals, 1 LLM call per round)
  - High scrape concurrency with retry
  - Time watchdog — guarantees completion within limit
  - No gap analysis by default (saves LLM calls for broader scraping)

Pipeline (state machine):
  DECOMPOSE  → break user query into sub-queries
  SEARCH     → DuckDuckGo concurrent search
  SCRAPE     → Trafilatura extraction + ChromaDB ingestion
  EXTRACT    → RAG retrieval + single LLM fact extraction
  SYNTHESISE → Final LLM report compilation
  DONE / ERROR
"""

from __future__ import annotations

import asyncio
import datetime
import hashlib
import json
import logging
import random
import re
import time as time_module
import uuid
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable

import trafilatura
from ddgs import DDGS
from openai import AsyncOpenAI
from openai import (
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    RateLimitError,
    InternalServerError,
)

from config import Settings
from rag_memory import RAGMemory
from output_formatter import post_process_report, add_key_quotes_section, extract_key_quotes

log = logging.getLogger(__name__)

# ── State machine ─────────────────────────────────────────────────────────────

class AgentState(Enum):
    IDLE = auto()
    DECOMPOSE = auto()
    SEARCH = auto()
    SCRAPE = auto()
    EXTRACT = auto()
    SYNTHESISE = auto()
    DONE = auto()
    ERROR = auto()

# ── Result container ──────────────────────────────────────────────────────────

@dataclass
class ResearchResult:
    topic: str
    markdown: str
    sources: list[str] = field(default_factory=list)
    total_chunks: int = 0
    depth_used: int = 0
    session_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])

# ── Engine ────────────────────────────────────────────────────────────────────

class ResearchEngine:
    def __init__(
        self,
        settings: Settings,
        on_log: Callable[[str], None],
        on_state: Callable[[AgentState], None],
        stop_event: asyncio.Event,
    ) -> None:
        self.settings = settings
        self._log = on_log
        self._state_cb = on_state
        self._stop = stop_event

        self._llm = AsyncOpenAI(
            base_url=settings.base_url,
            api_key=settings.api_key or "none",
            max_retries=3,
            timeout=120.0,
            default_headers={
                "HTTP-Referer": "https://github.com/anomalyco/deep_research",
                "X-OpenRouter-Title": "Deep Research",
            },
        )
        self._sources: dict[str, str] = {}
        self._source_index: dict[str, int] = {}

        # Time tracking
        self._start_time: float = 0.0
        self._time_limit_seconds: float = float(settings.time_limit_minutes * 60)

        # Polite-scrape headers
        self._scrape_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }

    # ── Time watchdog ─────────────────────────────────────────────────────────────

    def _time_remaining(self) -> float:
        return max(0.0, self._time_limit_seconds - (time_module.time() - self._start_time))

    def _time_expired(self) -> bool:
        return self._time_remaining() <= 5.0  # 5s buffer

    def _log_remaining(self, label: str) -> None:
        rem = self._time_remaining()
        self._log(f"[TIME] {label} — {rem:.0f}s remaining")

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _transition(self, state: AgentState) -> None:
        self._state_cb(state)
        self._log(f"\n{'─'*60}\n[{state.name}]\n{'─'*60}")

    def _cite(self, url: str) -> str:
        if url not in self._source_index:
            n = len(self._source_index) + 1
            self._source_index[url] = n
        return f"[{self._source_index[url]}]"

    def _aborted(self) -> bool:
        return self._stop.is_set()

    async def _llm_complete(self, system: str, user: str, temperature: float = 0.3) -> str:
        max_attempts = 3
        last_error: Exception | None = None

        for attempt in range(1, max_attempts + 1):
            try:
                response = await self._llm.chat.completions.create(
                    model=self.settings.model,
                    temperature=temperature,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                )
                return response.choices[0].message.content or ""
            except AuthenticationError as exc:
                self._log(f"[LLM] Authentication failed — check your API key: {exc}")
                raise
            except RateLimitError as exc:
                wait = 2 ** attempt + random.uniform(0, 1)
                self._log(f"[LLM] Rate limited (attempt {attempt}/{max_attempts}), waiting {wait:.1f}s: {exc}")
                last_error = exc
            except APITimeoutError as exc:
                self._log(f"[LLM] Timeout (attempt {attempt}/{max_attempts}): {exc}")
                last_error = exc
            except APIConnectionError as exc:
                self._log(f"[LLM] Connection error (attempt {attempt}/{max_attempts}): {exc}")
                last_error = exc
            except InternalServerError as exc:
                self._log(f"[LLM] Server error (attempt {attempt}/{max_attempts}): {exc}")
                last_error = exc
            except Exception as exc:
                self._log(f"[LLM] Unexpected error (attempt {attempt}/{max_attempts}): {exc}")
                last_error = exc

            if attempt < max_attempts:
                delay = 2 ** attempt + random.uniform(0, 1)
                await asyncio.sleep(delay)

        raise RuntimeError(f"LLM call failed after {max_attempts} attempts") from last_error

    # ── Phase 1: Query decomposition ──────────────────────────────────────────

    async def _decompose(self, topic: str) -> list[str]:
        self._transition(AgentState.DECOMPOSE)
        system = (
            "You are a research planning assistant. "
            "Given a research topic, produce exactly 6 highly specific, "
            "distinct web search queries that together will comprehensively cover the topic "
            "from diverse angles appropriate to the topic (e.g. historical, technical, practical, "
            "controversial, future outlook, comparative — choose the ones that fit). "
            "Do NOT force an angle that does not apply to the topic. "
            "Every query MUST explicitly contain the core subject of the research topic. "
            "Return ONLY a JSON array of strings — no commentary, no markdown fences."
        )
        user = f"Research topic: {topic}"
        raw = await self._llm_complete(system, user, temperature=0.2)
        try:
            clean = re.sub(r"```[a-z]*|```", "", raw).strip()
            queries = json.loads(clean)
            if isinstance(queries, list) and all(isinstance(q, str) for q in queries):
                # Validate queries: each must contain at least one word from the topic
                topic_words = set(topic.lower().split())
                valid = []
                for q in queries[:6]:
                    q_lower = q.lower()
                    # Keep query if it shares at least one significant word with topic
                    q_words = set(q_lower.split())
                    overlap = topic_words & q_words
                    if overlap or not topic_words:
                        valid.append(q)
                    else:
                        self._log(f"[DECOMPOSE] Dropping irrelevant query: {q}")
                if not valid:
                    valid = [topic]
                self._log(f"[DECOMPOSE] Generated {len(valid)} sub-queries")
                for i, q in enumerate(valid, 1):
                    self._log(f"  {i}. {q}")
                return valid
        except Exception as exc:
            self._log(f"[DECOMPOSE] JSON parse failed ({exc}), falling back to topic")
        return [topic]

    # ── Phase 2: Search + Scrape ──────────────────────────────────────────────

    def _ddg_search(self, query: str, n: int, topic_keywords: set[str] | None = None) -> list[dict]:
        max_attempts = 2
        for attempt in range(max_attempts):
            try:
                with DDGS() as ddgs:
                    results = list(ddgs.text(query, max_results=n))
                items = []
                for r in results:
                    if not r:
                        continue
                    url = r.get("href") or r.get("url", "")
                    if not url.startswith("http"):
                        continue
                    
                    title = r.get("title") or ""
                    body = r.get("body") or ""
                    
                    # Relevance check: skip results whose title/snippet lack any topic keyword
                    if topic_keywords:
                        combined = f"{title} {body}".lower()
                        if not any(kw in combined for kw in topic_keywords):
                            self._log(f"[SEARCH] Skipping irrelevant result: {url[:70]}")
                            continue
                    items.append({"url": url, "title": title, "body": body})
                return items
            except Exception as exc:
                self._log(f"[SEARCH] DDG error for '{query[:50]}' (attempt {attempt+1}/{max_attempts}): {exc}")
                if attempt == max_attempts - 1:
                    return []
                time_module.sleep(1.0 * (attempt + 1))
        return []

    def _searxng_search(self, query: str, n: int) -> list[dict]:
        """Search via SearXNG JSON API (self-hosted meta-search engine)."""
        base_url = self.settings.searxng_url.rstrip("/")
        if not base_url:
            return []
        try:
            params = urllib.parse.urlencode({"format": "json", "q": query, "language": "en-US", "categories": "general"})
            url = f"{base_url}/search?{params}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
            results = []
            for r in data.get("results", []):
                link = r.get("url", "")
                if not link.startswith("http"):
                    continue
                results.append({
                    "url": link,
                    "title": r.get("title", ""),
                    "body": r.get("content", ""),
                })
            self._log(f"[SEARCH] SearXNG returned {len(results)} results for '{query[:50]}'")
            return results[:n]
        except Exception as exc:
            self._log(f"[SEARCH] SearXNG error for '{query[:50]}': {exc}")
            return []

    async def _search_all(self, queries: list[str], topic_keywords: set[str] | None = None) -> dict[str, list[dict]]:
        self._transition(AgentState.SEARCH)
        loop = asyncio.get_event_loop()
        has_searxng = bool(self.settings.searxng_url.strip())

        query_results: dict[str, list[dict]] = {}
        for i, q in enumerate(queries):
            if i > 0:
                await asyncio.sleep(random.uniform(1.0, 3.0))

            # Step 1: try DuckDuckGo
            batch = await loop.run_in_executor(None, self._ddg_search, q, self.settings.search_results, topic_keywords)

            # Step 2: if DDG returned too few results, fall back to SearXNG
            if len(batch) < 2 and has_searxng:
                self._log(f"[SEARCH] DDG returned only {len(batch)} result(s) for '{q[:50]}', trying SearXNG…")
                searxng_results = await loop.run_in_executor(None, self._searxng_search, q, self.settings.search_results)
                # Merge: keep DDG results first, add SearXNG results that aren't duplicates
                seen = {item["url"] for item in batch}
                for item in searxng_results:
                    if item["url"] not in seen:
                        batch.append(item)
                        seen.add(item["url"])

            # Deduplicate and limit domain repeats
            seen_urls: set[str] = set()
            domain_count: dict[str, int] = {}
            items: list[dict] = []
            for item in batch:
                u = item["url"]
                if u in seen_urls:
                    continue
                seen_urls.add(u)
                domain = u.split("/")[2] if "//" in u else u
                domain_count[domain] = domain_count.get(domain, 0) + 1
                if domain_count[domain] <= 3:
                    items.append(item)
            query_results[q] = items

        total_urls = sum(len(v) for v in query_results.values())
        if has_searxng:
            self._log(f"[SEARCH] {total_urls} unique URLs across {len(queries)} queries (DDG + SearXNG)")
        else:
            self._log(f"[SEARCH] {total_urls} unique URLs across {len(queries)} queries (DDG only)")
        return query_results

    async def _evaluate_search_results(
        self,
        query_results: dict[str, list[dict]],
        topic: str,
        max_per_query: int = 3,
    ) -> list[str]:
        """LLM evaluates search results and selects the most relevant URLs per query."""
        self._transition(AgentState.SEARCH)  # Reuse SEARCH state for evaluation phase
        
        if not query_results:
            return []
        
        # Build prompt with all search results
        results_summary = []
        for query, items in query_results.items():
            results_summary.append(f"\nQuery: {query}")
            for i, item in enumerate(items):
                results_summary.append(
                    f"  {i+1}. {item['title'][:100]}\n     URL: {item['url']}\n     Snippet: {item['body'][:200]}"
                )
        
        system = (
            "You are a research librarian. Given search results for multiple queries on a topic, "
            "select the most authoritative, relevant, and diverse URLs for deep scraping. "
            "Prioritize: primary sources, reputable publications, recent content, diverse perspectives. "
            "Avoid: paywalls (unless critical), duplicate content, low-quality aggregators, marketing fluff. "
            f"Return EXACTLY {max_per_query} URLs PER QUERY as a JSON object mapping query -> list of URL strings. "
            "No commentary, no markdown fences."
        )
        user = (
            f"Research topic: {topic}\n\n"
            f"Search results:\n{''.join(results_summary)}\n\n"
            f"Select top {max_per_query} URLs per query. Output format:\n"
            '{"query1": ["url1", "url2", ...], "query2": ["url1", "url2", ...], ...}'
        )
        
        raw = await self._llm_complete(system, user, temperature=0.2)
        
        try:
            clean = re.sub(r"```[a-z]*|```", "", raw).strip()
            selected = json.loads(clean)
            if not isinstance(selected, dict):
                raise ValueError("Expected JSON object")
            
            all_selected: list[str] = []
            for query, urls in selected.items():
                if isinstance(urls, list):
                    valid_urls = [u for u in urls if isinstance(u, str) and u.startswith("http")]
                    all_selected.extend(valid_urls[:max_per_query])
                    self._log(f"[EVALUATE] Query '{query[:50]}': selected {len(valid_urls)} URLs")
            
            # Deduplicate while preserving order
            seen: set[str] = set()
            unique_selected = [u for u in all_selected if not (u in seen or seen.add(u))]
            
            self._log(f"[EVALUATE] Total {len(unique_selected)} unique URLs selected for scraping")
            return unique_selected
            
        except Exception as exc:
            self._log(f"[EVALUATE] LLM selection failed ({exc}), falling back to heuristic")
            # Fallback: take first max_per_query from each query
            fallback: list[str] = []
            for items in query_results.values():
                fallback.extend(item["url"] for item in items[:max_per_query] if isinstance(item, dict))
            # Deduplicate
            seen: set[str] = set()
            return [u for u in fallback if not (u in seen or seen.add(u))]

    def _scrape_url(self, url: str) -> str | None:
        try:
            downloaded = trafilatura.fetch_url(url)
            if not downloaded:
                return None
            text = trafilatura.extract(
                downloaded,
                include_comments=False,
                include_tables=True,
                no_fallback=False,
                favor_precision=True,
            )
            return text
        except Exception as exc:
            self._log(f"[SCRAPE] Failed {url[:70]}: {exc}")
            return None

    async def _scrape_with_retry_internal(self, url: str, sem: asyncio.Semaphore, loop) -> str | None:
        async with sem:
            for attempt in range(2):
                if self._aborted():
                    return None
                text = await loop.run_in_executor(None, self._scrape_url, url)
                if text and len(text) > 150:
                    return text
                if attempt == 0:
                    await asyncio.sleep(1.0 + random.uniform(0, 0.5))
        return None

    async def _scrape_with_retry(self, url: str, sem: asyncio.Semaphore, loop) -> tuple[str, str | None]:
        async with sem:
            for attempt in range(2):
                if self._aborted():
                    return url, None
                self._log(f"[SCRAPING] {url[:80]}" + (" (retry)" if attempt > 0 else ""))
                text = await loop.run_in_executor(None, self._scrape_url, url)
                if text and len(text) > 150:
                    return url, text
                if attempt == 0:
                    await asyncio.sleep(1.0 + random.uniform(0, 0.5))
        return url, None

    async def _scrape_and_ingest(self, urls: list[str], rag: RAGMemory) -> None:
        self._transition(AgentState.SCRAPE)
        if not urls:
            return

        sem = asyncio.Semaphore(self.settings.concurrent_scrape)
        loop = asyncio.get_event_loop()

        tasks = [self._scrape_with_retry(u, sem, loop) for u in urls]
        results = await asyncio.gather(*tasks)

        ingested = 0
        for url, text in results:
            if text:
                rag.ingest(text, url)
                ingested += 1
            else:
                self._log(f"[SCRAPE] No content from {url[:70]}")

        self._log(f"[SCRAPE] Done. {ingested}/{len(urls)} pages ingested. "
                  f"ChromaDB holds {rag.count()} chunks.")

    # ── Phase 3: Single-pass extraction ───────────────────────────────────────

    async def _extract_facts(self, topic: str, rag: RAGMemory) -> str:
        self._transition(AgentState.EXTRACT)

        # Multiple retrieval queries for broad RAG coverage — FREE (no LLM calls)
        retrieval_queries = [
            f"key facts and statistics about {topic}",
            f"main arguments and perspectives on {topic}",
            f"historical background and context for {topic}",
            f"recent developments and current status of {topic}",
            f"criticisms, controversies, and limitations related to {topic}",
            f"expert opinions and future predictions about {topic}",
            f"technical specifications, implementations, or methodologies for {topic}",
            f"comparative analysis and market or industry alternatives for {topic}",
        ]

        # Run all retrievals (fast, no LLM cost)
        all_chunks = []
        for eq in retrieval_queries:
            if self._aborted():
                break
            chunks = rag.retrieve(eq, top_k=self.settings.top_k)
            all_chunks.extend(chunks)

        if not all_chunks:
            return ""

        # Deduplicate by text hash
        seen_hashes: set[str] = set()
        unique_chunks = []
        for c in all_chunks:
            h = hashlib.md5(c.text.encode()).hexdigest()
            if h not in seen_hashes:
                seen_hashes.add(h)
                unique_chunks.append(c)

        # Sort by relevance (distance) and keep best ones
        unique_chunks.sort(key=lambda c: c.distance)
        best = unique_chunks[:self.settings.top_k * 3]

        context = "\n\n---\n\n".join(
            f"[Source: {c.source_url}]\n{c.text}" for c in best
        )

        system = (
            "You are a rigorous research analyst. Extract key factual claims, data points, "
            "quotes, statistics, arguments, and insights that are RELEVANT to the research topic. "
            "Ignore content that is off-topic or unrelated. "
            "Organise your extraction by the following facets:\n"
            "1. Key facts & statistics\n"
            "2. Main arguments & perspectives\n"
            "3. Historical background & context\n"
            "4. Recent developments & current status\n"
            "5. Criticisms, controversies & limitations\n"
            "6. Expert opinions & future outlook\n"
            "7. Technical details & methodologies\n"
            "8. Comparative analysis & alternatives\n\n"
            "For EVERY claim, append the source URL in parentheses. "
            "Be comprehensive but stay on-topic. "
            "Use bullet points. Preserve exact numbers, dates, and names."
        )
        user = (
            f"Research topic: {topic}\n\n"
            f"Web source context:\n{context}"
        )

        facts = await self._llm_complete(system, user, temperature=0.1)
        self._log(f"[EXTRACT] Single-pass extraction complete ({len(best)} chunks, {len(facts)} chars)")
        return facts

    # ── Phase 4: Final synthesis ──────────────────────────────────────────────

    async def _synthesise(
        self,
        topic: str,
        extracted_facts: str,
        rag: RAGMemory,
        depth: int,
        rounds: int,
        session_id: str,
    ) -> str:
        self._transition(AgentState.SYNTHESISE)

        # Final broad context sweep — grab lots of chunks
        retrieval_queries = [
            topic,
            f"key findings about {topic}",
            f"important data and statistics about {topic}",
        ]
        all_chunks = []
        for q in retrieval_queries:
            chunks = rag.retrieve(q, top_k=min(25, rag.count()))
            all_chunks.extend(chunks)

        seen_hashes: set[str] = set()
        unique_final = []
        for c in all_chunks:
            h = hashlib.md5(c.text.encode()).hexdigest()
            if h not in seen_hashes:
                seen_hashes.add(h)
                unique_final.append(c)

        unique_final.sort(key=lambda c: c.distance)
        best_final = unique_final[:min(40, rag.count())]

        final_context = "\n\n---\n\n".join(
            f"[{self._cite(c.source_url)} Source: {c.source_url}]\n{c.text}"
            for c in best_final
        )

        ref_lines = "\n".join(
            f"[{n}] {url}" for url, n in sorted(self._source_index.items(), key=lambda x: x[1])
        )

        today = datetime.date.today().isoformat()
        system = (
            "You are a world-class research analyst producing a professional briefing document. "
            "Every claim MUST have an inline citation like [1], [2].\n\n"
            "## TONE & STYLE\n"
            "- Authoritative, neutral, evidence-driven. No fluff or marketing language.\n"
            "- Use precise facts, figures, and attributions. Every statement should answer: "
            "\"how do we know this?\"\n"
            "- Write in dense, substantive paragraphs. Prioritize analysis over description.\n"
            "- Tables are supplementary — use them only when a comparison or dataset is "
            "clearly more readable than prose. Maximum 2-3 tables in the entire report.\n"
            "- Use **bold** for key metrics, terms, and emphasis.\n"
            "- Use `code` for technical names, version numbers, commands.\n"
            "- Use **GitHub-style callouts** for critical insights (not for routine facts):\n"
            "  - `> [!NOTE]` — important context\n"
            "  - `> [!IMPORTANT]` — critical finding requiring attention\n"
            "  - `> [!WARNING]` — potential issues or risks\n"
            "  - `> [!CAUTION]` — negative examples or things to avoid\n"
            "- Use **confidence tags** as blockquotes on major findings:\n"
            "  - `> **Established** — ≥2 independent, credible sources agree`\n"
            "  - `> **Contested** — sources conflict or disagree`\n"
            "  - `> **Uncertain** — single source or low authority`\n"
            "- Use **blockquotes** for expert quotations:\n"
            "  `> \"<quote>\" — Expert Name, Title [N]`\n"
            "- Use **bullet lists** for enumerations, evidence lists, factor comparisons. "
            "Prefer bullets over tables for simple lists.\n\n"
            "## REPORT STRUCTURE\n\n"
            "The report MUST start with this frontmatter:\n"
            "---\n"
            "title: \"<topic>\"\n"
            "date: \"<today>\"\n"
            "depth: <N>\n"
            "rounds: <N>\n"
            "sources: <N>\n"
            "chunks: <N>\n"
            "---\n\n"
            "Then include these mandatory sections in order:\n\n"
            "### 1. Executive Summary\n"
            "4-6 paragraphs covering: what was investigated and why it matters, "
            "3-5 key metrics or statistics with citations, "
            "overview of major findings, bottom-line assessment.\n\n"
            "### 2. Thematic Sections (choose 5-8 sections)\n"
            "Choose section headings that best organize THIS specific topic. "
            "DO NOT use generic headings like \"Key Findings\", \"Comparative Analysis\", "
            "\"Case Studies\", \"Timeline\", \"Expert Perspectives\", \"Analysis\", "
            "\"Controversies\", \"Glossary\", or \"Weakest Evidence\" unless they "
            "naturally fit the material. Instead, pick headings that reflect the "
            "actual content. Examples:\n"
            "- For analytical topics: \"Current State of the Field\", "
            "\"Key Debates & Divergences\", \"Implications\", \"Open Questions\"\n"
            "- For technical topics: \"Architecture & Design\", "
            "\"Performance Characteristics\", \"Comparison of Approaches\"\n"
            "- For research topics: \"Clinical Evidence\", "
            "\"Mechanism of Action\", \"Safety Profile\", \"Limitations\"\n"
            "- For historical topics: \"Historical Context\", "
            "\"Key Figures\", \"Chronological Development\"\n\n"
            "Each thematic section must:\n"
            "1. Lead with a **bold claim sentence**\n"
            "2. Include 2-4 dense, factual evidence paragraphs with inline citations\n"
            "3. End with a confidence tag: `> **Established** — description`\n"
            "Use subheadings (###) for sub-topics within a section. "
            "Use `> [!IMPORTANT]` or `> [!NOTE]` callouts for the most critical insight "
            "per section. Tables are optional — prefer prose and bullet lists. "
            "Maximum 2-3 tables in the entire report.\n\n"
            "### 3. Conclusion & Recommendations\n"
            "Summary of the most important takeaway. "
            "3-5 actionable recommendations or directions. "
            "Explicit suggestions for further research.\n\n"
            "### 4. References\n"
            "Numbered list exactly as provided below.\n\n"
            "RULES:\n"
            "- Minimum 5000 words of dense, factual prose.\n"
            "- Every factual claim → inline citation [n].\n"
            "- Maximum 2-3 tables total. Prefer prose, bullets, and callouts over tables.\n"
            "- Do NOT fabricate sources — only cite URLs from the reference list.\n"
            "- Use **bold** for key terms, `code` for technical names.\n"
            "- Use callouts (`> [!NOTE]`, `> [!IMPORTANT]`) sparingly — only for genuinely "
            "critical insights.\n"
            "- Use confidence tags as blockquotes: `> **Established** — description`."
        )
        user = (
            f"Topic: {topic}\n"
            f"Date: {today}\n"
            f"Depth: {depth}\n"
            f"Rounds: {rounds}\n"
            f"Sources: {len(self._source_index)}\n"
            f"Vectors stored: {rag.count()}\n\n"
            "REPORT REQUIREMENTS:\n"
            "- Professional briefing document for an informed reader\n"
            "- Minimum 5000 words of dense, factual prose\n"
            "- Maximum 2-3 tables total; prefer paragraphs and bullet lists\n"
            "- Confidence tags (Established/Contested/Uncertain) on major findings\n"
            "- Callout blocks for critical insights only\n"
            "- Structure: Executive Summary → 5-8 topic-appropriate thematic sections → "
            "Conclusion → References\n\n"
            f"=== EXTRACTED FACTS ===\n{extracted_facts[:12000]}\n\n"
            f"=== RETRIEVED CONTEXT ===\n{final_context[:15000]}\n\n"
            f"=== REFERENCE LIST ===\n{ref_lines}"
        )
        self._log("[SYNTHESISE] Asking LLM to compile final report …")
        report = await self._llm_complete(system, user, temperature=0.3)

        quotes = extract_key_quotes(extracted_facts)

        report = post_process_report(
            raw_markdown=report,
            topic=topic,
            depth=depth,
            rounds=rounds,
            sources=list(self._source_index.keys()),
            chunks=rag.count(),
            session_id=session_id,
            date=today,
        )

        report = add_key_quotes_section(report, quotes)

        self._log("[SYNTHESISE] Report compiled and post-processed successfully.")
        return report

    # ── Main entry point ──────────────────────────────────────────────────────

    async def run(self, topic: str) -> ResearchResult:
        session_id = uuid.uuid4().hex[:12]
        result = ResearchResult(topic=topic, markdown="", session_id=session_id)

        rag: RAGMemory | None = None
        try:
            rag = RAGMemory(
                persist_dir=self.settings.chroma_path,
                session_id=session_id,
                chunk_size=self.settings.chunk_size,
                chunk_overlap=self.settings.chunk_overlap,
                on_log=self._log,
            )

            total_depth = 0
            all_extracted: list[str] = []
            self._start_time = time_module.time()

            num_rounds = max(1, self.settings.num_rounds)

            for round_num in range(1, num_rounds + 1):
                if self._aborted() or self._time_expired():
                    if self._time_expired() and round_num > 1:
                        self._log(f"[TIME] {self._time_remaining():.0f}s remaining — skipping remaining rounds")
                    break

                self._log(f"\n{'='*60}\n[ROUND {round_num}/{num_rounds}]\n{'='*60}")
                self._log_remaining(f"Start of round {round_num}")

                # ── Decompose ─────────────────────────────────────────────
                round_context = topic
                if round_num > 1 and all_extracted:
                    round_context = (
                        f"{topic}\n\n"
                        f"Previous rounds covered:\n{all_extracted[-1][:2000]}"
                    )
                sub_queries = await self._decompose(round_context)
                if self._aborted() or self._time_expired():
                    break

                # ── Search + Scrape ────────────────────────────────────────
                topic_keywords = set(w.lower() for w in topic.split() if len(w) > 2)
                query_results = await self._search_all(sub_queries, topic_keywords)
                if self._aborted() or self._time_expired():
                    break
                selected_urls = await self._evaluate_search_results(query_results, topic)
                if self._aborted() or self._time_expired():
                    break
                await self._scrape_and_ingest(selected_urls, rag)
                if self._aborted() or self._time_expired():
                    break

                # ── Single-pass Extract ────────────────────────────────────
                extracted = await self._extract_facts(topic, rag)
                if self._aborted() or self._time_expired():
                    break

                # Gap analysis: if max_depth > 0, run additional iterations
                # that search for missing information not covered yet.
                current_depth = 1
                while (current_depth <= self.settings.max_depth
                       and not self._aborted()
                       and not self._time_expired()):
                    if current_depth > 1:
                        gap_queries = await self._decompose(
                            f"{topic}\n\nWhat aspects are still missing or poorly covered?\n"
                            f"Current findings:\n{extracted[-3000:]}"
                        )
                        if self._aborted() or self._time_expired():
                            break
                        gap_query_results = await self._search_all(gap_queries, topic_keywords)
                        if self._aborted() or self._time_expired():
                            break
                        gap_selected_urls = await self._evaluate_search_results(gap_query_results, topic)
                        if self._aborted() or self._time_expired():
                            break
                        await self._scrape_and_ingest(gap_selected_urls, rag)
                        if self._aborted() or self._time_expired():
                            break
                        extracted = await self._extract_facts(topic, rag)
                    current_depth += 1

                total_depth += current_depth
                all_extracted.append(extracted)
                self._log_remaining(f"End of round {round_num}")

            result.depth_used = total_depth

            # ── Synthesise ─────────────────────────────────────────────────
            if self._time_remaining() > 15.0:
                combined_facts = "\n\n".join(
                    f"## Round {i+1} Findings\n\n{extract}"
                    for i, extract in enumerate(all_extracted)
                )

                result.markdown = await self._synthesise(
                    topic, combined_facts, rag, total_depth, num_rounds, session_id
                )
            else:
                self._log("[TIME] Too little time remaining for synthesis — generating brief summary")
                result.markdown = (
                    f"# Research: {topic}\n\n"
                    f"Research was interrupted due to time limit ({self.settings.time_limit_minutes} min).\n\n"
                    f"## Sources Collected\n\n"
                    + "\n".join(f"- {u}" for u in self._source_index.keys())
                )

            result.sources = list(self._source_index.keys())
            result.total_chunks = rag.count()

            self._transition(AgentState.DONE)
            elapsed = time_module.time() - self._start_time
            self._log(
                f"\n[DONE] Research complete in {elapsed:.0f}s.\n"
                f"  Sources: {len(result.sources)} URLs\n"
                f"  Chunks:  {result.total_chunks}\n"
                f"  Rounds:  {num_rounds}\n"
                f"  Depth:   {result.depth_used}"
            )

            return result

        except asyncio.CancelledError:
            self._log("[HALTED] Research cancelled by user.")
            self._transition(AgentState.ERROR)
            return result

        except Exception as exc:
            self._log(f"[ERROR] Fatal: {exc}")
            log.exception("ResearchEngine fatal error")
            self._transition(AgentState.ERROR)
            raise
        finally:
            if rag:
                try:
                    deleted = rag.delete_collection()
                    if deleted:
                        self._log("[CLEANUP] ChromaDB collection successfully removed.")
                    else:
                        self._log("[CLEANUP] WARNING: ChromaDB collection may not have been fully removed.")
                except Exception as exc:
                    self._log(f"[CLEANUP] Error during ChromaDB cleanup: {exc}")
