# Research plan: DDG, parallel, chromadb cleanup

**Session ID:** ses_1543aa507ffeGnPEiumdJTE6XV
**Created:** 6/9/2026, 3:14:58 PM
**Updated:** 6/9/2026, 3:24:30 PM

---

## User

there are two problems with this code . 

1) there is a error occuring during the research like use ddgs , duckduckgo is depreciated , like that . 
2) searches are random. i need you to let the ai search the websites and in the background parallely search the programs .
3) when a research is complete remove the respective chromadb or else it will be huge .

now i need you to make a plan for these three problems , and how you will apporach the solutions 

---

## Assistant (Plan · DeepSeek V4 Flash Free · 150.8s)

_Thinking:_

The user wants me to analyze a codebase and create a plan to address three problems. Let me first explore the codebase to understand the structure and then formulate a plan.

Let me start by exploring the project structure.

**Tool: task**

**Input:**
```json
{
  "description": "Explore codebase structure",
  "prompt": "Explore the codebase at /home/davis/projects/deep_research thoroughly. I need to understand:\n1. The overall project structure (directory tree, key files)\n2. The main entry points and how the app runs\n3. How searches/research are performed (search providers, scraping, etc.)\n4. How ChromaDB is used (if at all)\n5. The AI/LLM integration points\n6. Any existing error handling patterns\n\nPlease return:\n- A complete directory tree (top 3-4 levels)\n- List of all Python files and their purposes\n- Key imports and dependencies (from requirements.txt or similar)\n- How the research flow works end-to-end\n- Where ChromaDB is initialized, written to, and if it's ever cleaned up\n- What search providers are used (duckduckgo, etc.)\n- Any relevant configuration files",
  "subagent_type": "explore"
}
```

**Output:**
```
<task id="ses_1543a5f89fferB0qLWocY4k9L8" state="completed">
<task_result>
Now I have a complete picture. Here is the comprehensive analysis:

---

## Complete Codebase Analysis: Deep Research

### 1. Complete Directory Tree (Top 4 Levels)

```
/home/davis/projects/deep_research/
├── .gitignore
├── index.html                          # Vite entry HTML
├── launch.sh                           # Shell script to launch the Tauri binary
├── package.json                        # Node.js dependencies & scripts
├── package-lock.json
├── postcss.config.js
├── README.md
├── setup.sh                            # Arch/CachyOS one-click setup script
├── tailwind.config.ts
├── tsconfig.json
├── tsconfig.node.json
├── vite.config.ts                      # Vite dev server config (port 1420)
│
├── backend/                            # Python research engine
│   ├── __init__.py                     # Empty package marker
│   ├── config.py                       # Settings dataclass, presets, paths
│   ├── main.py                         # CLI entry point (JSON stdout protocol)
│   ├── output_formatter.py             # Report post-processing pipeline
│   ├── rag_memory.py                   # ChromaDB RAG wrapper
│   ├── research_engine.py              # Core async research agent (state machine)
│   ├── requirements.txt                # Python dependencies
│   ├── settings.json                   # (created at runtime, gitignored)
│   └── tests/
│       └── test_output_formatter.py    # Basic tests for output_formatter
│
├── src/                                # React frontend (TypeScript)
│   ├── main.tsx                        # React entry point
│   ├── App.tsx                         # Root component (tabs, state orchestration)
│   │
│   ├── components/
│   │   ├── history/
│   │   │   ├── HistoryList.tsx         # Saved reports list
│   │   │   ├── HistorySearch.tsx       # Search/filter within history
│   │   │   └── ReportCard.tsx          # Individual report card
│   │   │
│   │   ├── layout/
│   │   │   └── Sidebar.tsx            # App sidebar navigation
│   │   │
│   │   ├── research/
│   │   │   ├── LogPanel.tsx            # Scrollable log output
│   │   │   ├── ProgressPanel.tsx       # Stage-by-stage progress display
│   │   │   ├── ResearchForm.tsx        # Topic input + config form
│   │   │   ├── ReportViewer.tsx        # Markdown report rendered preview
│   │   │   └── StageNode.tsx           # Individual stage progress indicator
│   │   │
│   │   ├── settings/
│   │   │   ├── ModelSelector.tsx       # Model dropdown with fetch
│   │   │   ├── ProviderConfig.tsx      # Per-provider config form
│   │   │   └── SettingsPanel.tsx       # Full settings page
│   │   │
│   │   └── ui/                         # Reusable UI primitives
│   │       ├── badge.tsx
│   │       ├── button.tsx
│   │       ├── card.tsx
│   │       ├── input.tsx
│   │       ├── label.tsx
│   │       ├── scroll-area.tsx
│   │       ├── searchable-select.tsx
│   │       ├── select.tsx
│   │       └── separator.tsx
│   │
│   ├── hooks/
│   │   ├── useResearch.ts             # Core research lifecycle hook (event listener)
│   │   └── useTheme.ts                # Dark/light theme toggling
│   │
│   ├── lib/
│   │   ├── api.ts                      # Tauri `invoke` wrappers (all IPC calls)
│   │   ├── reportUtils.ts             # Frontmatter stripping, tag removal
│   │   ├── types.ts                   # Shared TypeScript types/interfaces
│   │   └── utils.ts                   # cn() utility (clsx + tailwind-merge)
│   │
│   ├── stores/
│   │   ├── settings.ts                # Zustand store: settings state
│   │   └── useHistory.ts              # Zustand store: report history
│   │
│   ├── styles/
│   │   └── globals.css                # Tailwind + CSS variables (dark/light)
│   │
│   └── types/
│       └── css.d.ts                   # CSS module type declarations
│
└── src-tauri/                          # Tauri (Rust) shell
    ├── Cargo.toml                      # Rust dependencies
    ├── Cargo.lock
    ├── build.rs
    ├── tauri.conf.json                 # App window, build, bundle config
    │
    ├── capabilities/
    │   └── default.json                # Tauri v2 permissions (events, core)
    │
    ├── gen/schemas/                    # Auto-generated Tauri schemas
    ├── icons/                          # App icons
    │
    └── src/
        ├── main.rs                     # Rust main (calls lib::run)
        ├── lib.rs                      # Tauri builder, state management, command registration
        ├── models.rs                   # Rust data structs (AppSettings, ProgressPayload, etc.)
        ├── settings.rs                 # Settings file I/O with XOR encryption
        │
        └── commands/
            ├── mod.rs                  # Module declarations
            ├── research.rs             # start_research, cancel_research, fetch_models
            ├── reports.rs              # list/delete/search/get report content
            └── settings.rs             # get_settings, save_settings, get_research_state
```

---

### 2. All Python Files and Their Purposes

| File | Purpose |
|------|---------|
| `/home/davis/projects/deep_research/backend/__init__.py` | Empty package init |
| `/home/davis/projects/deep_research/backend/main.py` | **CLI entry point.** Parses arguments, constructs `Settings`, instantiates `ResearchEngine`, runs async loop, emits JSON progress events to stdout, saves report markdown to `~/deep_research_reports/`. Also has an `--mcp` flag to run as an MCP server. |
| `/home/davis/projects/deep_research/backend/config.py` | **Configuration.** Defines `Settings` dataclass (LLM, RAG, loop params), provider presets (LM Studio, OpenRouter, OpenCode Proxy), path constants, and `load_settings()`/`save_settings()` from `settings.json`. |
| `/home/davis/projects/deep_research/backend/research_engine.py` | **Core research agent.** 707-line state machine with 6 phases: `DECOMPOSE -> SEARCH -> SCRAPE -> EXTRACT -> SYNTHESISE -> DONE`. Contains all pipeline logic: DuckDuckGo search, trafilatura scraping, LLM calls via OpenAI SDK, RAG retrieval, gap-fill depth loop, final report synthesis. |
| `/home/davis/projects/deep_research/backend/rag_memory.py` | **ChromaDB RAG wrapper.** Manages a persistent ChromaDB collection per session. Handles text chunking (`RecursiveCharacterTextSplitter`), embedding + storage, semantic retrieval, and collection cleanup. |
| `/home/davis/projects/deep_research/backend/output_formatter.py` | **Report post-processing.** Builds YAML frontmatter, generates table of contents, validates citations, formats tables, adds methodology/source quality/doc stats sections, extracts key quotes. |
| `/home/davis/projects/deep_research/backend/tests/test_output_formatter.py` | 3 basic unit tests for `extract_frontmatter`, `validate_citations`, and `build_frontmatter`. |

---

### 3. Key Imports and Dependencies

#### Python (`backend/requirements.txt`)
| Package | Version | Purpose |
|---------|---------|---------|
| `chromadb` | >=0.5.0 | Vector database for RAG (embeddings + semantic search) |
| `langchain-text-splitters` | >=0.3.0 | `RecursiveCharacterTextSplitter` for chunking |
| `openai` | >=1.0.0 | OpenAI-compatible LLM client (used for OpenRouter, LM Studio, etc.) |
| `duckduckgo_search` | >=7.0.0 | Web search via DuckDuckGo |
| `trafilatura` | >=1.6.0 | HTML-to-text extraction from web pages |
| `httpx` | >=0.27.0 | HTTP client (used by trafilatura and openai under the hood) |

#### Rust (`src-tauri/Cargo.toml`)
| Dependency | Purpose |
|------------|---------|
| `tauri` (v2) | Desktop app framework |
| `tauri-plugin-opener` | Open files/folders in OS |
| `serde` / `serde_json` | Serialization for IPC |
| `tokio` | Async runtime |
| `reqwest` | HTTP client for model fetching |
| `base64` | API key XOR encryption encoding |
| `open` | Opening files |

#### Frontend (Node.js - `package.json`)
| Package | Purpose |
|---------|---------|
| `@tauri-apps/api` (v2) | Tauri IPC (invoke, events) |
| `react` / `react-dom` (v19) | UI framework |
| `zustand` | State management (settings, history) |
| `react-markdown` + `remark-gfm` | Markdown rendering |
| `rehype-highlight` | Code syntax highlighting |
| `lucide-react` | Icons |
| `@radix-ui/*` | Accessible UI primitives (dialog, select, tabs, etc.) |
| `tailwind-merge` + `clsx` | CSS class merging |
| `@tauri-apps/plugin-opener` | Open file dialogs |

---

### 4. How the Research Flow Works (End-to-End)

```
User enters topic in React UI
         │
         ▼
React: invoke("start_research", { topic, settings })
         │
         ▼
Rust (research.rs):
  1. Finds `python3` from .venv / system PATH
  2. Finds `backend/main.py` (resource dir, cwd, symlink resolution)
  3. Spawns: python3 -u main.py <topic> --provider ... --model ... --depth ... --rounds ... --max-pages ... --time-limit ...
  4. Reads stdout JSON lines, re-emits as Tauri events ("research-event")
  5. Reads stderr as log events
  6. Handles cancellation (SIGKILL + wait)
         │
         ▼
Python (main.py):
  1. Parses CLI args → constructs Settings
  2. Creates ResearchEngine with callbacks: on_log, on_state
  3. Calls asyncio.run(engine.run(topic))
  4. Emits JSON lines to stdout:
       {"type":"log","message":"..."}
       {"type":"progress","stage":"decompose","pct":5,...}
       {"type":"result","data":{"path":"...","content":"..."}}
       {"type":"error","message":"..."}
         │
         ▼
Python (research_engine.py - state machine):

  ┌──────────────────────────────────────────────────────────────┐
  │ run(topic)                for each round (default: 2)        │
  │ ┌─────────────────────────────────────────────────────────┐  │
  │ │ DECOMPOSE                                               │  │
  │ │   LLM query → 6 sub-queries (JSON array)               │  │
  │ │   Validates each contains topic words                   │  │
  │ ├─────────────────────────────────────────────────────────┤  │
  │ │ SEARCH                                                  │  │
  │ │   For each sub-query: DuckDuckGo (DDGS.text)           │  │
  │ │   Concurrent via run_in_executor + asyncio.gather       │  │
  │ │   Dedup, domain diversity filter (≤3/domain)            │  │
  │ │   Relevance filter (topic keywords in title/body)       │  │
  │ ├─────────────────────────────────────────────────────────┤  │
  │ │ SCRAPE                                                  │  │
  │ │   For each URL: trafilatura.fetch_url + extract         │  │
  │ │   Semaphore-limited concurrency (default: 20)           │  │
  │ │   Retry once on failure                                 │  │
  │ │   Pass text to RAGMemory.ingest() → ChromaDB            │  │
  │ ├─────────────────────────────────────────────────────────┤  │
  │ │ EXTRACT (single-pass)                                   │  │
  │ │   8 retrieval queries → RAGMemory.retrieve()            │  │
  │ │   Dedup by MD5, sort by distance, keep top_k*3          │  │
  │ │   Single LLM call: extract facts by 8 facets            │  │
  │ ├─────────────────────────────────────────────────────────┤  │
  │ │ GAP-FILL (depth loop, default 3 iterations)             │  │
  │ │   Re-decompose with "what's missing?" prompt            │  │
  │ │   → Search → Scrape → Extract again                     │  │
  │ └─────────────────────────────────────────────────────────┘  │
  │                                                              │
  │ SYNTHESISE (if ≥15s remaining)                               │
  │   3 retrieval queries → best 40 chunks                       │
  │   LLM call with 5000+ word template:                        │
  │     Executive Summary → Key Findings → Data & Statistics →  │
  │     Comparative Analysis → Case Studies → Timeline →        │
  │     Expert Perspectives → Analysis → Controversies →        │
  │     Glossary → Weakest Evidence → Conclusion → References   │
  │   post_process_report() → frontmatter, TOC, tables, stats   │
  │   add_key_quotes_section()                                   │
  │                                                              │
  │ DONE: delete ChromaDB collection, return ResearchResult      │
  └──────────────────────────────────────────────────────────────┘
         │
         ▼
Python (main.py):
  1. Saves report to ~/deep_research_reports/<timestamp>_<topic>.md
  2. Emits {"type":"result","data":{"path":"...","content":"..."}}
         │
         ▼
Rust: Reads JSON from stdout → emits Tauri event "research-event"
         │
         ▼
React (useResearch.ts):
  1. Listens for "research-event" via @tauri-apps/api/event
  2. Updates stage progress, logs, status
  3. On "result": sets reportContent → shows ReportViewer
  4. On "error": shows error banner
  5. On "cancelled": shows cancelled state
```

---

### 5. ChromaDB: Initialization, Writes, Cleanup

**Initialization** is in `rag_memory.py`, class `RAGMemory.__init__()`:

```python
# Location: /home/davis/projects/deep_research/backend/rag_memory.py, line 77-87
self._client = chromadb.PersistentClient(
    path=persist_dir,                                      # Default: ~/.local/share/deep_research/chroma
    settings=ChromaSettings(anonymized_telemetry=False),
)
self._col = self._client.get_or_create_collection(
    name=safe_id,                                          # "dr_" + session_id[:40]
    metadata={"hnsw:space": "cosine"},
)
```

- **Persistence path:** `~/.local/share/deep_research/chroma` (configurable via `settings.chroma_path`)
- **Collection name:** `dr_<session_id[:40]>` (12-char hex session ID)
- **Default embedding:** ChromaDB's built-in `all-MiniLM-L6-v2` (no custom embedding function)
- **Distance metric:** Cosine

**Writes** happen in `RAGMemory.ingest()` (line 111-136):

```python
# Called from research_engine.py _scrape_and_ingest()
# For each successfully scraped URL:
#   1. MD5 hash of URL = doc_id (dedup check)
#   2. RecursiveCharacterTextSplitter (chunk_size=1200, overlap=150)
#   3. self._col.add(documents=chunks, metadatas=metas, ids=ids)
```

- **Default chunk size:** 1200 characters (configurable)
- **Default chunk overlap:** 150 characters (configurable)
- **Metadata per chunk:** `{"source_url": ..., "chunk_index": ...}`
- **Deduplication:** MD5 hash of URL, skip if already ingested in this session

**Reads/Retrieval** happen in `RAGMemory.retrieve()` (line 138-167):

```python
result = self._col.query(
    query_texts=[query],
    n_results=n_results,
    include=["documents", "metadatas", "distances"],
)
```

Returns `RetrievedChunk` objects with `text`, `source_url`, and `distance`.

**Cleanup** happens at the end of `research_engine.py` `run()` (line 691-694):

```python
try:
    rag.delete_collection()        # Drops the entire session collection
except Exception:
    pass
```

And in `RAGMemory.delete_collection()` (line 173-180):

```python
def delete_collection(self) -> None:
    safe_id = "dr_" + self.session_id[:40].replace(" ", "_")
    try:
        self._client.delete_collection(safe_id)
    except Exception as exc:
        self._log(f"[CHROMA] Could not delete collection: {exc}")
```

**Key observation:** Each research session creates a new ChromaDB collection (named by session ID). The collection is **always deleted** at the end of a successful run (the `except Exception: pass` means cleanup failures are silently ignored). However, if the process is killed or crashes before cleanup, orphaned collections may remain in `~/.local/share/deep_research/chroma/`. There is no global garbage collection or TTL-based cleanup mechanism.

---

### 6. Search Providers

| Provider | Implementation | Location |
|----------|---------------|----------|
| **DuckDuckGo** | `duckduckgo_search.DDGS.text()` — synchronous, called via `run_in_executor` for async | `research_engine.py`, method `_ddg_search()` (line 226) |
| **LLM Providers** (not search, but AI inference) | OpenAI-compatible API via `openai.AsyncOpenAI` | `research_engine.py`, `__init__()` (line 89) |

There is **no** Google, Bing, Brave, or other search engine integration. Only DuckDuckGo is used for web search.

The three LLM provider presets in `config.py`:

| Provider | Base URL | Default Model |
|----------|----------|---------------|
| LM Studio (local) | `http://localhost:1234/v1` | `local-model` |
| OpenRouter | `https://openrouter.ai/api/v1` | `openai/gpt-4o-mini` |
| OpenCode Proxy | `http://127.0.0.1:4010/v1` | `auto` |

---

### 7. AI/LLM Integration Points

All LLM calls go through `ResearchEngine._llm_complete()` (line 141-180):

```python
self._llm = AsyncOpenAI(
    base_url=settings.base_url,
    api_key=settings.api_key or "none",
    max_retries=3,
    timeout=120.0,
    default_headers={...},      # OpenRouter referer headers
)
```

**Retry logic:** Up to 3 attempts with exponential backoff (`2^attempt + random`). Catches specific OpenAI error types:
- `AuthenticationError` — raised immediately (no retry)
- `RateLimitError` — retried
- `APITimeoutError` — retried
- `APIConnectionError` — retried
- `InternalServerError` — retried
- Generic `Exception` — retried

**LLM calls by phase:**

| Phase | Temperature | System Prompt | Purpose |
|-------|------------|---------------|---------|
| DECOMPOSE | 0.2 | Research planning assistant | Generate 6 search sub-queries |
| EXTRACT | 0.1 | Rigorous research analyst | Extract facts by 8 facets from RAG context |
| SYNTHESISE | 0.3 | World-class research analyst | Compile final 5000+ word report with strict template |
| Gap-fill DECOMPOSE | 0.2 | Same as DECOMPOSE | Generate sub-queries for missing information |

**Model fetching:** `fetch_models` in Rust (`research.rs` line 97-146) queries `GET {base_url}/models`, parses `data[].id` array. Used by `ModelSelector.tsx` component.

---

### 8. Error Handling Patterns

**Python backend:**

| Pattern | Location | Example |
|---------|----------|---------|
| Try/except with error event emission | `main.py` line 175-177 | `except Exception as exc: emit("error", ...); sys.exit(1)` |
| Specific LLM error retry | `research_engine.py` line 156-180 | Catches 5 OpenAI error types, exponential backoff, `AuthenticationError` re-raised immediately |
| LLM call exhaustion | `research_engine.py` line 180 | `raise RuntimeError(f"LLM call failed after {max_attempts} attempts")` |
| Search failures silently handled | `research_engine.py` line 247-248 | `except Exception: self._log(...); return []` |
| Scrape failures per-URL | `research_engine.py` line 294-296 | `except Exception: self._log(...); return None` |
| JSON parse fallback | `research_engine.py` line 220-222 | `if JSON parse fails: return [topic]` |
| Time watchdog | `research_engine.py` line 116-124 | `_time_expired()` checks 5s buffer, skips synthesis if <15s |
| Abort checks throughout | `research_engine.py` (many lines) | `if self._aborted() or self._time_expired(): break` |
| Cancel via `asyncio.Event` | `research_engine.py` line 698-701 | `except asyncio.CancelledError: ... return result` |
| ChromaDB cleanup failure silenced | `research_engine.py` line 691-694 | `try: rag.delete_collection() except Exception: pass` |
| Logging + re-raise | `research_engine.py` line 703-707 | `except Exception: log.exception(...); raise` |

**Rust backend:**

| Pattern | Location | Example |
|---------|----------|---------|
| State guard checks | `research.rs` line 155-158 | `if research.running { return Err("Research already in progress") }` |
| Provider/model validation | `research.rs` line 175-183 | Returns descriptive `Err` strings for missing model/key |
| Backend directory not found | `research.rs` line 214-221 | Emits error event, marks stopped |
| Process spawn failure | `research.rs` line 226-240 | Emits error with path + fix instructions |
| Cancellation via SIGKILL | `research.rs` line 311-323 | `child.kill(); child.wait();` |
| Settings parsing fallback | `settings.rs` line 46-49 | `unwrap_or_else` → default on parse error |
| XOR encryption for API keys | `settings.rs` line 8-31 | Basic obfuscation (not security-grade) |

**Frontend/React:**

| Pattern | Location | Example |
|---------|----------|---------|
| Event listener error ignored | `useResearch.ts` line 109 | `catch { console.warn("...browser mode") }` |
| Settings validation before start | `app.tsx` line 59, `api.ts` line 48-57 | `validateSettings` checks model + key |
| Error/cancelled state rendering | `App.tsx` line 141-150 | Conditional error banners |
| API call errors caught | `useResearch.ts` line 125-128, `useHistory.ts` line 27-29 | `setState({ status: "error", errorMessage: String(err) })` |
| Cancel silently catches | `useResearch.ts` line 132 | `catch { /* ignore */ }` |

---

### 9. Configuration Files Summary

| File | Format | Purpose |
|------|--------|---------|
| `backend/config.py` | Python | Default settings, provider presets, paths |
| `backend/settings.json` | JSON (runtime, gitignored) | Persisted user settings (created by app) |
| `src-tauri/tauri.conf.json` | JSON | Tauri v2 app config (window size, bundle, CSP) |
| `src-tauri/capabilities/default.json` | JSON | Tauri v2 permissions (events, opener) |
| `src-tauri/src/settings.rs` | Rust | Settings file I/O with XOR encryption |
| `.gitignore` | Text | Ignores: node_modules, dist, .venv, settings.json |
| `vite.config.ts` | TypeScript | Vite dev server (port 1420, HMR) |
| `tsconfig.json` / `tsconfig.node.json` | JSON | TypeScript compiler options |
| `tailwind.config.ts` | TypeScript | Tailwind CSS configuration |
| `postcss.config.js` | JS | PostCSS (Tailwind) config |
| `package.json` | JSON | npm scripts & frontend dependencies |

---

### 10. Key Architectural Notes

- **IPC protocol:** Python writes JSON lines to stdout. Rust reads line-by-line, parses as `ProgressPayload`, and re-emits as Tauri events. This is a streaming protocol — no blocking.
- **Concurrency model:** Python uses `asyncio` with `run_in_executor` for blocking calls (DDG search, trafilatura scraping). Rust uses `tokio` + `tauri::async_runtime::spawn` for the backend process supervisor.
- **No WebSocket/gRPC:** The Python backend is a one-shot CLI process, not a long-running server (except MCP mode, which is optiona l and not yet implemented — `mcp_server.py` is imported but does not exist).
- **ChromaDB is session-scoped:** Each research run creates a collection, populates it, and deletes it. The persistent directory at `~/.local/share/deep_research/chroma/` accumulates only if cleanup fails.
- **DuckDuckGo is the sole search engine** — no Google/Bing/Brave API keys needed.
- **No authentication/rate limiting** for the Python backend — it is spawned locally by Tauri.
- **Minimal test coverage** — only 3 tests for `output_formatter.py`.
</task_result>
</task>
```

---

## Assistant (Plan · DeepSeek V4 Flash Free · 7.5s)

_Thinking:_

Now I have a thorough understanding of the codebase. Let me analyze the three problems:

1. **DuckDuckGo deprecation/errors**: The `duckduckgo_search` library version is `>=7.0.0`. There have been deprecations in DDG search. The search is done in `research_engine.py` via `_ddg_search()` method using `DDGS.text()`. I need to look at the exact implementation.

2. **Searches are random / let AI search websites with parallel programmatic searches**: This seems like the user wants the AI (LLM) to decide which search queries to run, while programmatic searches (like DuckDuckGo, maybe adding other providers) run in parallel in the background. Currently, the search phase runs for each sub-query from the decompose phase, but it seems the user thinks the searches are "random" (maybe the sub-queries from the LLM are not good enough, or the results are low quality).

3. **Clean up ChromaDB after research completes**: The code already does this (`rag.delete_collection()` in `research_engine.py:691-694`), but it's wrapped in try/except with `pass`. The user might be seeing orphaned collections, or the cleanup isn't happening reliably (perhaps when there's an error during research, the cleanup doesn't happen).

Let me now look at the specific search implementation to give more detailed recommendations.

Actually, I need to read the actual files to understand the exact code patterns. Let me read the key files.

Let me read the key source files to understand the exact issues before making a plan.

**Tool: read**

**Input:**
```json
{
  "filePath": "/home/davis/projects/deep_research/backend/research_engine.py"
}
```

**Output:**
```
<path>/home/davis/projects/deep_research/backend/research_engine.py</path>
<type>file</type>
<content>
1: """
2: research_engine.py — Core asynchronous research agent.
3: 
4: Optimised for speed + volume:
5:   - Single-pass extraction (multiple RAG retrievals, 1 LLM call per round)
6:   - High scrape concurrency with retry
7:   - Time watchdog — guarantees completion within limit
8:   - No gap analysis by default (saves LLM calls for broader scraping)
9: 
10: Pipeline (state machine):
11:   DECOMPOSE  → break user query into sub-queries
12:   SEARCH     → DuckDuckGo concurrent search
13:   SCRAPE     → Trafilatura extraction + ChromaDB ingestion
14:   EXTRACT    → RAG retrieval + single LLM fact extraction
15:   SYNTHESISE → Final LLM report compilation
16:   DONE / ERROR
17: """
18: 
19: from __future__ import annotations
20: 
21: import asyncio
22: import datetime
23: import hashlib
24: import json
25: import logging
26: import random
27: import re
28: import time as time_module
29: import uuid
30: from dataclasses import dataclass, field
31: from enum import Enum, auto
32: from typing import Callable
33: 
34: import trafilatura
35: from duckduckgo_search import DDGS
36: from openai import AsyncOpenAI
37: from openai import (
38:     APIConnectionError,
39:     APITimeoutError,
40:     AuthenticationError,
41:     RateLimitError,
42:     InternalServerError,
43: )
44: 
45: from config import Settings
46: from rag_memory import RAGMemory
47: from output_formatter import post_process_report, add_key_quotes_section, extract_key_quotes
48: 
49: log = logging.getLogger(__name__)
50: 
51: # ── State machine ─────────────────────────────────────────────────────────────
52: 
53: class AgentState(Enum):
54:     IDLE = auto()
55:     DECOMPOSE = auto()
56:     SEARCH = auto()
57:     SCRAPE = auto()
58:     EXTRACT = auto()
59:     SYNTHESISE = auto()
60:     DONE = auto()
61:     ERROR = auto()
62: 
63: # ── Result container ──────────────────────────────────────────────────────────
64: 
65: @dataclass
66: class ResearchResult:
67:     topic: str
68:     markdown: str
69:     sources: list[str] = field(default_factory=list)
70:     total_chunks: int = 0
71:     depth_used: int = 0
72:     session_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
73: 
74: # ── Engine ────────────────────────────────────────────────────────────────────
75: 
76: class ResearchEngine:
77:     def __init__(
78:         self,
79:         settings: Settings,
80:         on_log: Callable[[str], None],
81:         on_state: Callable[[AgentState], None],
82:         stop_event: asyncio.Event,
83:     ) -> None:
84:         self.settings = settings
85:         self._log = on_log
86:         self._state_cb = on_state
87:         self._stop = stop_event
88: 
89:         self._llm = AsyncOpenAI(
90:             base_url=settings.base_url,
91:             api_key=settings.api_key or "none",
92:             max_retries=3,
93:             timeout=120.0,
94:             default_headers={
95:                 "HTTP-Referer": "https://github.com/anomalyco/deep_research",
96:                 "X-OpenRouter-Title": "Deep Research",
97:             },
98:         )
99:         self._sources: dict[str, str] = {}
100:         self._source_index: dict[str, int] = {}
101: 
102:         # Time tracking
103:         self._start_time: float = 0.0
104:         self._time_limit_seconds: float = float(settings.time_limit_minutes * 60)
105: 
106:         # Polite-scrape headers
107:         self._scrape_headers = {
108:             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
109:                           "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
110:             "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
111:             "Accept-Language": "en-US,en;q=0.5",
112:         }
113: 
114:     # ── Time watchdog ─────────────────────────────────────────────────────────────
115: 
116:     def _time_remaining(self) -> float:
117:         return max(0.0, self._time_limit_seconds - (time_module.time() - self._start_time))
118: 
119:     def _time_expired(self) -> bool:
120:         return self._time_remaining() <= 5.0  # 5s buffer
121: 
122:     def _log_remaining(self, label: str) -> None:
123:         rem = self._time_remaining()
124:         self._log(f"[TIME] {label} — {rem:.0f}s remaining")
125: 
126:     # ── Helpers ───────────────────────────────────────────────────────────────
127: 
128:     def _transition(self, state: AgentState) -> None:
129:         self._state_cb(state)
130:         self._log(f"\n{'─'*60}\n[{state.name}]\n{'─'*60}")
131: 
132:     def _cite(self, url: str) -> str:
133:         if url not in self._source_index:
134:             n = len(self._source_index) + 1
135:             self._source_index[url] = n
136:         return f"[{self._source_index[url]}]"
137: 
138:     def _aborted(self) -> bool:
139:         return self._stop.is_set()
140: 
141:     async def _llm_complete(self, system: str, user: str, temperature: float = 0.3) -> str:
142:         max_attempts = 3
143:         last_error: Exception | None = None
144: 
145:         for attempt in range(1, max_attempts + 1):
146:             try:
147:                 response = await self._llm.chat.completions.create(
148:                     model=self.settings.model,
149:                     temperature=temperature,
150:                     messages=[
151:                         {"role": "system", "content": system},
152:                         {"role": "user", "content": user},
153:                     ],
154:                 )
155:                 return response.choices[0].message.content or ""
156:             except AuthenticationError as exc:
157:                 self._log(f"[LLM] Authentication failed — check your API key: {exc}")
158:                 raise
159:             except RateLimitError as exc:
160:                 wait = 2 ** attempt + random.uniform(0, 1)
161:                 self._log(f"[LLM] Rate limited (attempt {attempt}/{max_attempts}), waiting {wait:.1f}s: {exc}")
162:                 last_error = exc
163:             except APITimeoutError as exc:
164:                 self._log(f"[LLM] Timeout (attempt {attempt}/{max_attempts}): {exc}")
165:                 last_error = exc
166:             except APIConnectionError as exc:
167:                 self._log(f"[LLM] Connection error (attempt {attempt}/{max_attempts}): {exc}")
168:                 last_error = exc
169:             except InternalServerError as exc:
170:                 self._log(f"[LLM] Server error (attempt {attempt}/{max_attempts}): {exc}")
171:                 last_error = exc
172:             except Exception as exc:
173:                 self._log(f"[LLM] Unexpected error (attempt {attempt}/{max_attempts}): {exc}")
174:                 last_error = exc
175: 
176:             if attempt < max_attempts:
177:                 delay = 2 ** attempt + random.uniform(0, 1)
178:                 await asyncio.sleep(delay)
179: 
180:         raise RuntimeError(f"LLM call failed after {max_attempts} attempts") from last_error
181: 
182:     # ── Phase 1: Query decomposition ──────────────────────────────────────────
183: 
184:     async def _decompose(self, topic: str) -> list[str]:
185:         self._transition(AgentState.DECOMPOSE)
186:         system = (
187:             "You are a research planning assistant. "
188:             "Given a research topic, produce exactly 6 highly specific, "
189:             "distinct web search queries that together will comprehensively cover the topic "
190:             "from diverse angles appropriate to the topic (e.g. historical, technical, practical, "
191:             "controversial, future outlook, comparative — choose the ones that fit). "
192:             "Do NOT force an angle that does not apply to the topic. "
193:             "Every query MUST explicitly contain the core subject of the research topic. "
194:             "Return ONLY a JSON array of strings — no commentary, no markdown fences."
195:         )
196:         user = f"Research topic: {topic}"
197:         raw = await self._llm_complete(system, user, temperature=0.2)
198:         try:
199:             clean = re.sub(r"```[a-z]*|```", "", raw).strip()
200:             queries = json.loads(clean)
201:             if isinstance(queries, list) and all(isinstance(q, str) for q in queries):
202:                 # Validate queries: each must contain at least one word from the topic
203:                 topic_words = set(topic.lower().split())
204:                 valid = []
205:                 for q in queries[:6]:
206:                     q_lower = q.lower()
207:                     # Keep query if it shares at least one significant word with topic
208:                     q_words = set(q_lower.split())
209:                     overlap = topic_words & q_words
210:                     if overlap or not topic_words:
211:                         valid.append(q)
212:                     else:
213:                         self._log(f"[DECOMPOSE] Dropping irrelevant query: {q}")
214:                 if not valid:
215:                     valid = [topic]
216:                 self._log(f"[DECOMPOSE] Generated {len(valid)} sub-queries")
217:                 for i, q in enumerate(valid, 1):
218:                     self._log(f"  {i}. {q}")
219:                 return valid
220:         except Exception as exc:
221:             self._log(f"[DECOMPOSE] JSON parse failed ({exc}), falling back to topic")
222:         return [topic]
223: 
224:     # ── Phase 2: Search + Scrape ──────────────────────────────────────────────
225: 
226:     def _ddg_search(self, query: str, n: int, topic_keywords: set[str] | None = None) -> list[str]:
227:         try:
228:             with DDGS() as ddgs:
229:                 results = list(ddgs.text(query, max_results=n))
230:             urls = []
231:             for r in results:
232:                 if not r:
233:                     continue
234:                 url = r.get("href") or r.get("url", "")
235:                 if not url.startswith("http"):
236:                     continue
237:                 # Relevance check: skip results whose title/snippet lack any topic keyword
238:                 if topic_keywords:
239:                     title = (r.get("title") or "").lower()
240:                     body = (r.get("body") or "").lower()
241:                     combined = f"{title} {body}"
242:                     if not any(kw in combined for kw in topic_keywords):
243:                         self._log(f"[SEARCH] Skipping irrelevant result: {url[:70]}")
244:                         continue
245:                 urls.append(url)
246:             return urls
247:         except Exception as exc:
248:             self._log(f"[SEARCH] DDG error for '{query[:50]}': {exc}")
249:             return []
250: 
251:     async def _search_all(self, queries: list[str], topic_keywords: set[str] | None = None) -> list[str]:
252:         self._transition(AgentState.SEARCH)
253:         loop = asyncio.get_event_loop()
254:         tasks = [
255:             loop.run_in_executor(
256:                 None,
257:                 self._ddg_search,
258:                 q,
259:                 self.settings.search_results,
260:                 topic_keywords,
261:             )
262:             for q in queries
263:         ]
264:         results = await asyncio.gather(*tasks)
265:         seen_urls: set[str] = set()
266:         domain_count: dict[str, int] = {}
267:         urls: list[str] = []
268:         for batch in results:
269:             for u in batch:
270:                 if u in seen_urls:
271:                     continue
272:                 seen_urls.add(u)
273:                 # Domain diversity filter: max 3 per domain per search batch
274:                 domain = u.split("/")[2] if "//" in u else u
275:                 domain_count[domain] = domain_count.get(domain, 0) + 1
276:                 if domain_count[domain] <= 3:
277:                     urls.append(u)
278:         self._log(f"[SEARCH] {len(urls)} unique URLs (domain-diverse)")
279:         return urls
280: 
281:     def _scrape_url(self, url: str) -> str | None:
282:         try:
283:             downloaded = trafilatura.fetch_url(url)
284:             if not downloaded:
285:                 return None
286:             text = trafilatura.extract(
287:                 downloaded,
288:                 include_comments=False,
289:                 include_tables=True,
290:                 no_fallback=False,
291:                 favor_precision=True,
292:             )
293:             return text
294:         except Exception as exc:
295:             self._log(f"[SCRAPE] Failed {url[:70]}: {exc}")
296:             return None
297: 
298:     async def _scrape_with_retry(self, url: str, sem: asyncio.Semaphore, loop) -> tuple[str, str | None]:
299:         async with sem:
300:             for attempt in range(2):
301:                 if self._aborted():
302:                     return url, None
303:                 self._log(f"[SCRAPING] {url[:80]}" + (" (retry)" if attempt > 0 else ""))
304:                 text = await loop.run_in_executor(None, self._scrape_url, url)
305:                 if text and len(text) > 150:
306:                     return url, text
307:                 if attempt == 0:
308:                     await asyncio.sleep(1.0 + random.uniform(0, 0.5))
309:         return url, None
310: 
311:     async def _scrape_and_ingest(self, urls: list[str], rag: RAGMemory) -> None:
312:         self._transition(AgentState.SCRAPE)
313:         if not urls:
314:             return
315: 
316:         sem = asyncio.Semaphore(self.settings.concurrent_scrape)
317:         loop = asyncio.get_event_loop()
318: 
319:         tasks = [self._scrape_with_retry(u, sem, loop) for u in urls]
320:         results = await asyncio.gather(*tasks)
321: 
322:         ingested = 0
323:         for url, text in results:
324:             if text:
325:                 rag.ingest(text, url)
326:                 ingested += 1
327:             else:
328:                 self._log(f"[SCRAPE] No content from {url[:70]}")
329: 
330:         self._log(f"[SCRAPE] Done. {ingested}/{len(urls)} pages ingested. "
331:                   f"ChromaDB holds {rag.count()} chunks.")
332: 
333:     # ── Phase 3: Single-pass extraction ───────────────────────────────────────
334: 
335:     async def _extract_facts(self, topic: str, rag: RAGMemory) -> str:
336:         self._transition(AgentState.EXTRACT)
337: 
338:         # Multiple retrieval queries for broad RAG coverage — FREE (no LLM calls)
339:         retrieval_queries = [
340:             f"key facts and statistics about {topic}",
341:             f"main arguments and perspectives on {topic}",
342:             f"historical background and context for {topic}",
343:             f"recent developments and current status of {topic}",
344:             f"criticisms, controversies, and limitations related to {topic}",
345:             f"expert opinions and future predictions about {topic}",
346:             f"technical specifications, implementations, or methodologies for {topic}",
347:             f"comparative analysis and market or industry alternatives for {topic}",
348:         ]
349: 
350:         # Run all retrievals (fast, no LLM cost)
351:         all_chunks = []
352:         for eq in retrieval_queries:
353:             if self._aborted():
354:                 break
355:             chunks = rag.retrieve(eq, top_k=self.settings.top_k)
356:             all_chunks.extend(chunks)
357: 
358:         if not all_chunks:
359:             return ""
360: 
361:         # Deduplicate by text hash
362:         seen_hashes: set[str] = set()
363:         unique_chunks = []
364:         for c in all_chunks:
365:             h = hashlib.md5(c.text.encode()).hexdigest()
366:             if h not in seen_hashes:
367:                 seen_hashes.add(h)
368:                 unique_chunks.append(c)
369: 
370:         # Sort by relevance (distance) and keep best ones
371:         unique_chunks.sort(key=lambda c: c.distance)
372:         best = unique_chunks[:self.settings.top_k * 3]
373: 
374:         context = "\n\n---\n\n".join(
375:             f"[Source: {c.source_url}]\n{c.text}" for c in best
376:         )
377: 
378:         system = (
379:             "You are a rigorous research analyst. Extract key factual claims, data points, "
380:             "quotes, statistics, arguments, and insights that are RELEVANT to the research topic. "
381:             "Ignore content that is off-topic or unrelated. "
382:             "Organise your extraction by the following facets:\n"
383:             "1. Key facts & statistics\n"
384:             "2. Main arguments & perspectives\n"
385:             "3. Historical background & context\n"
386:             "4. Recent developments & current status\n"
387:             "5. Criticisms, controversies & limitations\n"
388:             "6. Expert opinions & future outlook\n"
389:             "7. Technical details & methodologies\n"
390:             "8. Comparative analysis & alternatives\n\n"
391:             "For EVERY claim, append the source URL in parentheses. "
392:             "Be comprehensive but stay on-topic. "
393:             "Use bullet points. Preserve exact numbers, dates, and names."
394:         )
395:         user = (
396:             f"Research topic: {topic}\n\n"
397:             f"Web source context:\n{context}"
398:         )
399: 
400:         facts = await self._llm_complete(system, user, temperature=0.1)
401:         self._log(f"[EXTRACT] Single-pass extraction complete ({len(best)} chunks, {len(facts)} chars)")
402:         return facts
403: 
404:     # ── Phase 4: Final synthesis ──────────────────────────────────────────────
405: 
406:     async def _synthesise(
407:         self,
408:         topic: str,
409:         extracted_facts: str,
410:         rag: RAGMemory,
411:         depth: int,
412:         rounds: int,
413:         session_id: str,
414:     ) -> str:
415:         self._transition(AgentState.SYNTHESISE)
416: 
417:         # Final broad context sweep — grab lots of chunks
418:         retrieval_queries = [
419:             topic,
420:             f"key findings about {topic}",
421:             f"important data and statistics about {topic}",
422:         ]
423:         all_chunks = []
424:         for q in retrieval_queries:
425:             chunks = rag.retrieve(q, top_k=min(25, rag.count()))
426:             all_chunks.extend(chunks)
427: 
428:         seen_hashes: set[str] = set()
429:         unique_final = []
430:         for c in all_chunks:
431:             h = hashlib.md5(c.text.encode()).hexdigest()
432:             if h not in seen_hashes:
433:                 seen_hashes.add(h)
434:                 unique_final.append(c)
435: 
436:         unique_final.sort(key=lambda c: c.distance)
437:         best_final = unique_final[:min(40, rag.count())]
438: 
439:         final_context = "\n\n---\n\n".join(
440:             f"[{self._cite(c.source_url)} Source: {c.source_url}]\n{c.text}"
441:             for c in best_final
442:         )
443: 
444:         ref_lines = "\n".join(
445:             f"[{n}] {url}" for url, n in sorted(self._source_index.items(), key=lambda x: x[1])
446:         )
447: 
448:         today = datetime.date.today().isoformat()
449:         system = (
450:             "You are a world-class research analyst producing a professional briefing document. "
451:             "Follow the EXACT structure below. Every claim MUST have an inline citation like [1], [2].\n\n"
452:             "## FORMATTING REQUIREMENTS\n\n"
453:             "### Rich Elements (use all throughout):\n"
454:             "- **Comparison matrices**: Markdown tables comparing entities across dimensions\n"
455:             "- **Data tables**: Quantitative data with source columns — minimum 3 tables\n"
456:             "- **Key Takeaway callouts**: `> **Key Takeaway:** <text>` for critical insights\n"
457:             "- **Confidence tags**: Mark each significant finding as:\n"
458:             "  - `[Established]` — ≥2 independent, credible sources agree\n"
459:             "  - `[Contested]` — sources conflict or disagree\n"
460:             "  - `[Uncertain]` — single source or low authority\n"
461:             "- **Timeline tables**: For chronological developments (| Date | Event | Source |)\n"
462:             "- **Bullet lists**: For enumerations, evidence lists, factor comparisons\n"
463:             "- **Bold** for key metrics, terms, and emphasis\n"
464:             "- `Code` for technical names, version numbers, commands\n"
465:             "- **Blockquotes** for expert quotations: `> \"<quote>\" — Expert Name, Title [N]`\n\n"
466:             "## REQUIRED SECTIONS (in order)\n\n"
467:             "---\n"
468:             "title: \"<topic>\"\n"
469:             "date: \"<today>\"\n"
470:             "depth: <N>\n"
471:             "rounds: <N>\n"
472:             "sources: <N>\n"
473:             "chunks: <N>\n"
474:             "---\n\n"
475:             "### Executive Summary\n"
476:             "4-6 paragraphs. First: what was investigated and why it matters. "
477:             "Then: 3-5 key metrics or statistics (with citations). "
478:             "Then: overview of major findings. "
479:             "End with: bottom-line assessment.\n\n"
480:             "### Key Findings\n"
481:             "Break into 4-6 thematic ### subsections. "
482:             "Each subsection:\n"
483:             "1. **Bold claim sentence** as the lead\n"
484:             "2. 2-4 evidence paragraphs with inline citations\n"
485:             "3. Confidence tag at the end: `[Established / Contested / Uncertain]`\n"
486:             "4. Include at least one comparison table or data table per subsection\n"
487:             "Use > **Key Takeaway:** blocks for the most important insight per subsection\n\n"
488:             "### Data & Statistics\n"
489:             "At least 3 rich Markdown tables. Each table MUST have a Source column. "
490:             "Types of tables to include:\n"
491:             "- | Metric | Value | Year | Source |\n"
492:             "- | Entity | Dimension A | Dimension B | Dimension C | Source |\n"
493:             "- | Factor | Impact | Evidence Level | Source |\n\n"
494:             "### Comparative Analysis\n"
495:             "Compare major perspectives, approaches, entities, or schools of thought. "
496:             "Use a comparison matrix table. "
497:             "Highlight where sources agree and where they diverge.\n\n"
498:             "### Case Studies & Examples\n"
499:             "2-3 real-world examples or case studies from the research. "
500:             "Each: context → what happened → outcome → source.\n\n"
501:             "### Timeline of Key Developments\n"
502:             "| Date | Event | Impact | Source | format when chronological data exists.\n\n"
503:             "### Expert Perspectives\n"
504:             "Notable quotes or positions from key figures/organizations. "
505:             "Use blockquote format: `> \"<quote>\" — Source [N]`\n\n"
506:             "### Analysis\n"
507:             "Critical analysis: patterns, implications, cause-effect relationships. "
508:             "Use **bold** for key terms. Compare and contrast evidence. "
509:             "Identify open questions.\n\n"
510:             "### Controversies & Limitations\n"
511:             "Conflicting viewpoints, methodological limitations, "
512:             "unanswered questions, known biases, low-confidence areas.\n\n"
513:             "### Glossary of Key Terms\n"
514:             "| Term | Definition |\n"
515:             "Only if the topic has specialized terminology.\n\n"
516:             "### Weakest Evidence\n"
517:             "Self-audit: list the 3 claims in this report with the weakest support, "
518:             "and explain why confidence is low.\n\n"
519:             "### Conclusion & Recommendations\n"
520:             "Summary of most important takeaway. "
521:             "3-5 actionable recommendations or directions. "
522:             "Explicit suggestions for further research.\n\n"
523:             "### References\n"
524:             "Numbered list exactly as provided below.\n\n"
525:             "RULES:\n"
526:             "- Minimum 5000 words.\n"
527:             "- Every factual claim → inline citation [n].\n"
528:             "- Minimum 3 data tables with source columns.\n"
529:             "- Do NOT fabricate sources — only cite URLs from the reference list.\n"
530:             "- Use **bold** for key terms, `code` for technical names.\n"
531:             "- Include > **Key Takeaway:** blocks for the 5-7 most critical insights.\n"
532:             "- Add [Established / Contested / Uncertain] tags on major findings."
533:         )
534:         user = (
535:             f"Topic: {topic}\n"
536:             f"Date: {today}\n"
537:             f"Depth: {depth}\n"
538:             f"Rounds: {rounds}\n"
539:             f"Sources: {len(self._source_index)}\n"
540:             f"Vectors stored: {rag.count()}\n\n"
541:             "REPORT REQUIREMENTS:\n"
542:             "- Professional briefing document for an informed reader\n"
543:             "- Minimum 5000 words\n"
544:             "- At least 3 data tables with source columns\n"
545:             "- [Established / Contested / Uncertain] tags on major findings\n"
546:             "- > **Key Takeaway:** callout blocks for critical insights\n"
547:             "- Comparison matrices where applicable\n"
548:             "- Include sections: Executive Summary → Key Findings → Data & Statistics → "
549:             "Comparative Analysis → Case Studies → Timeline → Expert Perspectives → "
550:             "Analysis → Controversies → Glossary → Weakest Evidence → Conclusion → References\n\n"
551:             f"=== EXTRACTED FACTS ===\n{extracted_facts[:12000]}\n\n"
552:             f"=== RETRIEVED CONTEXT ===\n{final_context[:15000]}\n\n"
553:             f"=== REFERENCE LIST ===\n{ref_lines}"
554:         )
555:         self._log("[SYNTHESISE] Asking LLM to compile final report …")
556:         report = await self._llm_complete(system, user, temperature=0.3)
557: 
558:         quotes = extract_key_quotes(extracted_facts)
559: 
560:         report = post_process_report(
561:             raw_markdown=report,
562:             topic=topic,
563:             depth=depth,
564:             rounds=rounds,
565:             sources=list(self._source_index.keys()),
566:             chunks=rag.count(),
567:             session_id=session_id,
568:             date=today,
569:         )
570: 
571:         report = add_key_quotes_section(report, quotes)
572: 
573:         self._log("[SYNTHESISE] Report compiled and post-processed successfully.")
574:         return report
575: 
576:     # ── Main entry point ──────────────────────────────────────────────────────
577: 
578:     async def run(self, topic: str) -> ResearchResult:
579:         session_id = uuid.uuid4().hex[:12]
580:         result = ResearchResult(topic=topic, markdown="", session_id=session_id)
581: 
582:         rag = RAGMemory(
583:             persist_dir=self.settings.chroma_path,
584:             session_id=session_id,
585:             chunk_size=self.settings.chunk_size,
586:             chunk_overlap=self.settings.chunk_overlap,
587:             on_log=self._log,
588:         )
589: 
590:         total_depth = 0
591:         all_extracted: list[str] = []
592:         self._start_time = time_module.time()
593: 
594:         try:
595:             num_rounds = max(1, self.settings.num_rounds)
596: 
597:             for round_num in range(1, num_rounds + 1):
598:                 if self._aborted() or self._time_expired():
599:                     if self._time_expired() and round_num > 1:
600:                         self._log(f"[TIME] {self._time_remaining():.0f}s remaining — skipping remaining rounds")
601:                     break
602: 
603:                 self._log(f"\n{'='*60}\n[ROUND {round_num}/{num_rounds}]\n{'='*60}")
604:                 self._log_remaining(f"Start of round {round_num}")
605: 
606:                 # ── Decompose ─────────────────────────────────────────────
607:                 round_context = topic
608:                 if round_num > 1 and all_extracted:
609:                     round_context = (
610:                         f"{topic}\n\n"
611:                         f"Previous rounds covered:\n{all_extracted[-1][:2000]}"
612:                     )
613:                 sub_queries = await self._decompose(round_context)
614:                 if self._aborted() or self._time_expired():
615:                     break
616: 
617:                 # ── Search + Scrape ────────────────────────────────────────
618:                 topic_keywords = set(w.lower() for w in topic.split() if len(w) > 2)
619:                 urls = await self._search_all(sub_queries, topic_keywords)
620:                 if self._aborted() or self._time_expired():
621:                     break
622:                 await self._scrape_and_ingest(urls, rag)
623:                 if self._aborted() or self._time_expired():
624:                     break
625: 
626:                 # ── Single-pass Extract ────────────────────────────────────
627:                 extracted = await self._extract_facts(topic, rag)
628:                 if self._aborted() or self._time_expired():
629:                     break
630: 
631:                 # Gap analysis: if max_depth > 0, run additional iterations
632:                 # that search for missing information not covered yet.
633:                 current_depth = 1
634:                 while (current_depth <= self.settings.max_depth
635:                        and not self._aborted()
636:                        and not self._time_expired()):
637:                     if current_depth > 1:
638:                         gap_queries = await self._decompose(
639:                             f"{topic}\n\nWhat aspects are still missing or poorly covered?\n"
640:                             f"Current findings:\n{extracted[-3000:]}"
641:                         )
642:                         if self._aborted() or self._time_expired():
643:                             break
644:                         gap_urls = await self._search_all(gap_queries, topic_keywords)
645:                         if self._aborted() or self._time_expired():
646:                             break
647:                         await self._scrape_and_ingest(gap_urls, rag)
648:                         if self._aborted() or self._time_expired():
649:                             break
650:                         extracted = await self._extract_facts(topic, rag)
651:                     current_depth += 1
652: 
653:                 total_depth += current_depth
654:                 all_extracted.append(extracted)
655:                 self._log_remaining(f"End of round {round_num}")
656: 
657:             result.depth_used = total_depth
658: 
659:             # ── Synthesise ─────────────────────────────────────────────────
660:             if self._time_remaining() > 15.0:
661:                 combined_facts = "\n\n".join(
662:                     f"## Round {i+1} Findings\n\n{extract}"
663:                     for i, extract in enumerate(all_extracted)
664:                 )
665: 
666:                 result.markdown = await self._synthesise(
667:                     topic, combined_facts, rag, total_depth, num_rounds, session_id
668:                 )
669:             else:
670:                 self._log("[TIME] Too little time remaining for synthesis — generating brief summary")
671:                 result.markdown = (
672:                     f"# Research: {topic}\n\n"
673:                     f"Research was interrupted due to time limit ({self.settings.time_limit_minutes} min).\n\n"
674:                     f"## Sources Collected\n\n"
675:                     + "\n".join(f"- {u}" for u in self._source_index.keys())
676:                 )
677: 
678:             result.sources = list(self._source_index.keys())
679:             result.total_chunks = rag.count()
680: 
681:             self._transition(AgentState.DONE)
682:             elapsed = time_module.time() - self._start_time
683:             self._log(
684:                 f"\n[DONE] Research complete in {elapsed:.0f}s.\n"
685:                 f"  Sources: {len(result.sources)} URLs\n"
686:                 f"  Chunks:  {result.total_chunks}\n"
687:                 f"  Rounds:  {num_rounds}\n"
688:                 f"  Depth:   {result.depth_used}"
689:             )
690: 
691:             try:
692:                 rag.delete_collection()
693:             except Exception:
694:                 pass
695: 
696:             return result
697: 
698:         except asyncio.CancelledError:
699:             self._log("[HALTED] Research cancelled by user.")
700:             self._transition(AgentState.ERROR)
701:             return result
702: 
703:         except Exception as exc:
704:             self._log(f"[ERROR] Fatal: {exc}")
705:             log.exception("ResearchEngine fatal error")
706:             self._transition(AgentState.ERROR)
707:             raise

(End of file - total 707 lines)
</content>
```

**Tool: read**

**Input:**
```json
{
  "filePath": "/home/davis/projects/deep_research/backend/rag_memory.py"
}
```

**Output:**
```
<path>/home/davis/projects/deep_research/backend/rag_memory.py</path>
<type>file</type>
<content>
1: """
2: rag_memory.py — Local RAG pipeline using ChromaDB.
3: 
4: Responsibilities:
5:   • Initialise (or open) a persistent ChromaDB collection per research session.
6:   • Split incoming text into overlapping chunks via langchain-text-splitters.
7:   • Embed and store chunks with metadata (source URL, chunk index).
8:   • Retrieve the top-K most semantically relevant chunks for a query.
9: """
10: 
11: from __future__ import annotations
12: 
13: import hashlib
14: import logging
15: import uuid
16: from dataclasses import dataclass
17: from typing import Callable
18: 
19: import chromadb
20: from chromadb.config import Settings as ChromaSettings
21: from langchain_text_splitters import RecursiveCharacterTextSplitter
22: 
23: log = logging.getLogger(__name__)
24: 
25: 
26: # ── Data model ────────────────────────────────────────────────────────────────
27: 
28: @dataclass
29: class Chunk:
30:     text: str
31:     source_url: str
32:     chunk_index: int
33:     doc_id: str
34: 
35: 
36: @dataclass
37: class RetrievedChunk:
38:     text: str
39:     source_url: str
40:     distance: float
41: 
42: 
43: # ── Manager ───────────────────────────────────────────────────────────────────
44: 
45: class RAGMemory:
46:     """
47:     Wraps a single ChromaDB collection for one research session.
48: 
49:     Parameters
50:     ----------
51:     persist_dir : str
52:         Filesystem path where ChromaDB stores its data.
53:     session_id : str
54:         Unique identifier for this research run; used as the collection name.
55:     chunk_size : int
56:         Maximum characters per chunk.
57:     chunk_overlap : int
58:         Character overlap between adjacent chunks.
59:     on_log : Callable[[str], None] | None
60:         Optional callback for status messages (forwarded to GUI log).
61:     """
62: 
63:     def __init__(
64:         self,
65:         persist_dir: str,
66:         session_id: str,
67:         chunk_size: int = 800,
68:         chunk_overlap: int = 120,
69:         on_log: Callable[[str], None] | None = None,
70:     ) -> None:
71:         self._log_cb = on_log or (lambda msg: None)
72:         self.session_id = session_id
73: 
74:         # Sanitise collection name — Chroma requires [a-zA-Z0-9_-] and 3-63 chars
75:         safe_id = "dr_" + session_id[:40].replace(" ", "_")
76: 
77:         self._log(f"[CHROMA] Opening collection '{safe_id}' at {persist_dir}")
78:         self._client = chromadb.PersistentClient(
79:             path=persist_dir,
80:             settings=ChromaSettings(anonymized_telemetry=False),
81:         )
82: 
83:         # Get-or-create so re-runs don't duplicate
84:         self._col = self._client.get_or_create_collection(
85:             name=safe_id,
86:             metadata={"hnsw:space": "cosine"},
87:         )
88: 
89:         self._splitter = RecursiveCharacterTextSplitter(
90:             chunk_size=chunk_size,
91:             chunk_overlap=chunk_overlap,
92:             length_function=len,
93:             separators=["\n\n", "\n", ". ", " ", ""],
94:         )
95: 
96:         self._stored_doc_ids: set[str] = set()
97:         self.total_chunks: int = 0
98: 
99:     # ── Internal helpers ──────────────────────────────────────────────────────
100: 
101:     def _log(self, msg: str) -> None:
102:         log.debug(msg)
103:         self._log_cb(msg)
104: 
105:     @staticmethod
106:     def _url_hash(url: str) -> str:
107:         return hashlib.md5(url.encode()).hexdigest()
108: 
109:     # ── Public API ────────────────────────────────────────────────────────────
110: 
111:     def ingest(self, text: str, source_url: str) -> int:
112:         """
113:         Chunk *text*, embed, and store in ChromaDB.
114: 
115:         Returns the number of new chunks stored (0 if already ingested).
116:         """
117:         doc_id = self._url_hash(source_url)
118:         if doc_id in self._stored_doc_ids:
119:             self._log(f"[CHROMA] Already ingested: {source_url[:80]}")
120:             return 0
121: 
122:         chunks = self._splitter.split_text(text)
123:         if not chunks:
124:             self._log(f"[CHROMA] No text extracted from: {source_url[:80]}")
125:             return 0
126: 
127:         ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
128:         metas = [{"source_url": source_url, "chunk_index": i} for i in range(len(chunks))]
129: 
130:         # ChromaDB will use its default embedding function (all-MiniLM-L6-v2)
131:         self._col.add(documents=chunks, metadatas=metas, ids=ids)
132: 
133:         self._stored_doc_ids.add(doc_id)
134:         self.total_chunks += len(chunks)
135:         self._log(f"[CHUNKING INTO CHROMA] {len(chunks)} chunks ← {source_url[:70]}")
136:         return len(chunks)
137: 
138:     def retrieve(self, query: str, top_k: int = 12) -> list[RetrievedChunk]:
139:         """
140:         Semantic search: return the top_k most relevant chunks for *query*.
141:         """
142:         n_results = min(top_k, self._col.count())
143:         if n_results == 0:
144:             return []
145: 
146:         result = self._col.query(
147:             query_texts=[query],
148:             n_results=n_results,
149:             include=["documents", "metadatas", "distances"],
150:         )
151: 
152:         chunks: list[RetrievedChunk] = []
153:         docs = result["documents"][0]
154:         metas = result["metadatas"][0]
155:         dists = result["distances"][0]
156: 
157:         for doc, meta, dist in zip(docs, metas, dists):
158:             chunks.append(
159:                 RetrievedChunk(
160:                     text=doc,
161:                     source_url=meta.get("source_url", "unknown"),
162:                     distance=dist,
163:                 )
164:             )
165: 
166:         self._log(f"[RETRIEVING] {len(chunks)} chunks for query: '{query[:60]}'")
167:         return chunks
168: 
169:     def count(self) -> int:
170:         """Total chunks currently in the collection."""
171:         return self._col.count()
172: 
173:     def delete_collection(self) -> None:
174:         """Drop this session's collection from ChromaDB (cleanup)."""
175:         safe_id = "dr_" + self.session_id[:40].replace(" ", "_")
176:         try:
177:             self._client.delete_collection(safe_id)
178:             self._log(f"[CHROMA] Collection {safe_id} deleted.")
179:         except Exception as exc:
180:             self._log(f"[CHROMA] Could not delete collection: {exc}")

(End of file - total 180 lines)
</content>
```

**Tool: read**

**Input:**
```json
{
  "filePath": "/home/davis/projects/deep_research/backend/main.py"
}
```

**Output:**
```
<path>/home/davis/projects/deep_research/backend/main.py</path>
<type>file</type>
<content>
1: """
2: backend/main.py — Entry point for the Deep Research Python backend.
3: 
4: Protocol: reads CLI arguments, runs the research loop, writes JSON lines to stdout.
5: Each line is a ProgressEvent consumed by the Tauri Rust layer.
6: """
7: 
8: from __future__ import annotations
9: 
10: import argparse
11: import json
12: import sys
13: import time
14: from datetime import datetime
15: from pathlib import Path
16: 
17: sys.path.insert(0, str(Path(__file__).parent.resolve()))
18: 
19: from research_engine import ResearchEngine, AgentState
20: from config import Settings, MCP_SERVER_HOST
21: import asyncio
22: 
23: 
24: def emit(
25:     event_type: str,
26:     message: str,
27:     stage: str | None = None,
28:     pct: int | None = None,
29:     data=None,
30:     round_num: int | None = None,
31:     round_total: int | None = None,
32:     elapsed: float | None = None,
33: ):
34:     payload = {
35:         "type": event_type,
36:         "stage": stage,
37:         "message": message,
38:         "pct": pct,
39:         "round": round_num,
40:         "roundTotal": round_total,
41:         "elapsed": elapsed,
42:         "data": data,
43:     }
44:     sys.stdout.write(json.dumps(payload, default=str) + "\n")
45:     sys.stdout.flush()
46: 
47: 
48: def main():
49:     parser = argparse.ArgumentParser(description="Deep Research Engine")
50:     parser.add_argument("topic", help="Research topic")
51:     parser.add_argument("--provider", default="openrouter")
52:     parser.add_argument("--base-url", default="https://openrouter.ai/api/v1")
53:     parser.add_argument("--api-key", default="")
54:     parser.add_argument("--model", default="google/gemini-2.0-flash-001")
55:     parser.add_argument("--depth", type=int, default=2)
56:     parser.add_argument("--rounds", type=int, default=2)
57:     parser.add_argument("--max-pages", type=int, default=5)
58:     parser.add_argument("--time-limit", type=int, default=30)
59:     parser.add_argument("--mcp", action="store_true", help="Run as MCP server instead of one-shot research")
60:     parser.add_argument("--mcp-port", type=int, default=9753, help="Port for MCP server (default: 9753)")
61:     args = parser.parse_args()
62: 
63:     if args.mcp:
64:         from mcp_server import run_server
65:         run_server(host=MCP_SERVER_HOST, port=args.mcp_port)
66:         return
67: 
68:     settings = Settings(
69:         provider_name=args.provider,
70:         base_url=args.base_url,
71:         api_key=args.api_key or "none",
72:         model=args.model,
73:         max_depth=args.depth,
74:         num_rounds=args.rounds,
75:         search_results=args.max_pages,
76:         concurrent_scrape=min(args.max_pages, 10),
77:         time_limit_minutes=args.time_limit,
78:     )
79: 
80:     output_dir = Path.home() / "deep_research_reports"
81:     output_dir.mkdir(parents=True, exist_ok=True)
82: 
83:     topic = args.topic
84:     num_rounds = args.rounds
85: 
86:     start_time = time.time()
87:     current_round = 0
88: 
89:     stage_map = {
90:         AgentState.DECOMPOSE: "decompose",
91:         AgentState.SEARCH: "search",
92:         AgentState.SCRAPE: "scrape",
93:         AgentState.EXTRACT: "extract",
94:         AgentState.SYNTHESISE: "synthesise",
95:         AgentState.DONE: "done",
96:         AgentState.ERROR: "error",
97:     }
98: 
99:     def on_log(msg: str):
100:         nonlocal current_round
101:         msg_str = str(msg)
102:         elapsed = round(time.time() - start_time, 1)
103: 
104:         round_match = __import__("re").search(r"\[ROUND (\d+)/(\d+)\]", msg_str)
105:         if round_match:
106:             current_round = int(round_match.group(1))
107: 
108:         emit("log", msg_str, elapsed=elapsed, round_num=current_round, round_total=num_rounds)
109: 
110:         if "[SEARCH]" in msg_str and "URLs" in msg_str:
111:             emit("progress", msg_str, stage="search", pct=30, round_num=current_round, round_total=num_rounds, elapsed=elapsed)
112:         elif "[SCRAPING]" in msg_str:
113:             emit("progress", msg_str, stage="scrape", round_num=current_round, round_total=num_rounds, elapsed=elapsed)
114:         elif "[SCRAPE]" in msg_str and "Done" in msg_str:
115:             emit("progress", msg_str, stage="scrape", pct=70, round_num=current_round, round_total=num_rounds, elapsed=elapsed)
116:         elif "[CHUNKING INTO CHROMA]" in msg_str:
117:             emit("progress", msg_str, stage="chunk", round_num=current_round, round_total=num_rounds, elapsed=elapsed)
118:         elif "[CHROMA]" in msg_str and "collection" in msg_str:
119:             emit("progress", msg_str, stage="chunk", round_num=current_round, round_total=num_rounds, elapsed=elapsed)
120:         elif "[EXTRACT]" in msg_str:
121:             emit("progress", msg_str, stage="extract", round_num=current_round, round_total=num_rounds, elapsed=elapsed)
122:         elif "[SYNTHESISE]" in msg_str:
123:             emit("progress", msg_str, stage="synthesise", round_num=current_round, round_total=num_rounds, elapsed=elapsed)
124:         elif "[DONE]" in msg_str:
125:             emit("progress", "Research complete", stage="done", pct=100, round_num=current_round, round_total=num_rounds, elapsed=elapsed)
126: 
127:     def on_state(state: AgentState):
128:         nonlocal current_round
129:         stage = stage_map.get(state)
130:         if stage:
131:             pct_map = {
132:                 AgentState.DECOMPOSE: 5,
133:                 AgentState.SEARCH: 15,
134:                 AgentState.SCRAPE: 40,
135:                 AgentState.EXTRACT: 60,
136:                 AgentState.SYNTHESISE: 80,
137:             }
138:             elapsed = round(time.time() - start_time, 1)
139:             emit(
140:                 "progress",
141:                 f"Phase: {state.name}",
142:                 stage=stage,
143:                 pct=pct_map.get(state),
144:                 round_num=current_round,
145:                 round_total=num_rounds,
146:                 elapsed=elapsed,
147:             )
148: 
149:     stop_event = asyncio.Event()
150: 
151:     engine = ResearchEngine(
152:         settings=settings,
153:         on_log=on_log,
154:         on_state=on_state,
155:         stop_event=stop_event,
156:     )
157: 
158:     try:
159:         result = asyncio.run(engine.run(topic))
160: 
161:         if result.markdown:
162:             ts = datetime.now().strftime("%Y%m%d_%H%M%S")
163:             safe_topic = "".join(c if c.isalnum() or c in " _-" else "_" for c in topic)[:60]
164:             filename = f"{ts}_{safe_topic}.md"
165:             filepath = output_dir / filename
166:             filepath.write_text(result.markdown, encoding="utf-8")
167: 
168:             emit("result", "Report generated", data={
169:                 "path": str(filepath),
170:                 "content": result.markdown,
171:             })
172:         else:
173:             emit("error", "Research produced no output.")
174: 
175:     except Exception as exc:
176:         emit("error", f"Research failed: {exc}")
177:         sys.exit(1)
178: 
179: 
180: if __name__ == "__main__":
181:     main()

(End of file - total 181 lines)
</content>
```

---

## Assistant (Plan · DeepSeek V4 Flash Free · 302.2s)

_Thinking:_

Now I have a thorough understanding of the code. Let me analyze the three problems:

## Problem 1: DuckDuckGo deprecation/errors

The `duckduckgo_search` library has been going through changes. The `DDGS` class and its `text()` method have had API changes across versions. In version 7+, the API might have changed. Looking at line 229:
```python
results = list(ddgs.text(query, max_results=n))
```

The `duckduckgo_search` library version is `>=7.0.0`. There could be deprecation warnings or errors depending on the exact version installed. Also, DuckDuckGo has been actively blocking automated searches, requiring proxies, etc. The user mentions "duckduckgo is deprecated" - this might mean the library's API has changed, or the `DDGS` usage pattern is from an older version.

Let me check what the current version of duckduckgo_search looks like...

Actually, the user said "like that" - they may be listing examples of the error type. The core issue is that the search provider is unreliable or has a deprecated API.

## Problem 2: Searches are random / need AI-directed with parallel background search

Currently:
1. AI (LLM) decomposes the topic into sub-queries (phase 1: DECOMPOSE)
2. Those sub-queries are searched via DuckDuckGo (phase 2: SEARCH)
3. Then scrape happens (SCRAPE)

The user wants:
- The AI to actually search the websites (I think they mean: let the AI evaluate search results and decide which websites are worth scraping, rather than just blindly taking top N results)
- In parallel, programmatic search engines (like DuckDuckGo, maybe adding more) run in the background

So the flow might be:
1. LLM generates search queries
2. Programmatic search runs in background (parallel) for all queries
3. The LLM evaluates the search results and picks the best URLs to scrape
4. Or: the LLM gets the search results AND can also suggest additional searches

Wait, re-reading: "i need you to let the ai search the websites and in the background parallely search the programs"

I think this means:
- Let the AI determine what URLs to search/scrape (maybe the LLM generates search queries, reviews results, picks URLs)
- In the background, run programmatic search (DuckDuckGo, etc.) in parallel to gather more results
- The AI can interleave: search → review → search deeper → scrape

Actually, I think the user wants:
1. The AI should be able to search the web (like using browser search or search tool access) - i.e., the LLM itself decides what to search for
2. In parallel, the programmatic search (DuckDuckGo etc.) happens in the background as a separate process to collect more data

## Problem 3: Clean up ChromaDB after research completes

Looking at lines 691-694:
```python
try:
    rag.delete_collection()
except Exception:
    pass
```

This is called after DONE. But:
1. If the research fails (the `except Exception as exc` block at line 703-707), the collection is NOT deleted - it just raises.
2. If cancelled via `CancelledError` (line 698-701), the collection is NOT deleted.
3. The `pass` means errors during cleanup are silently ignored.

So the fix would be to move cleanup to a `finally` block that runs regardless of success, cancellation, or error.

Now let me formulate a comprehensive plan.

Let me think about this more carefully:

### Problem 1: DuckDuckGo deprecation/unreliability

The `duckduckgo_search` library has had several breaking changes. The `DDGS` class and `text()` method API changed between versions:
- In v7.x, you use `DDGS().text(query, max_results=n)`
- In older versions, it was `DDGS().text(query, n)`

The user might be seeing deprecation warnings or the search might fail entirely. Additionally, DuckDuckGo has been known to rate-limit or block automated searches.

**Solution option 1**: Update the API usage to match the installed version
**Solution option 2**: Add multiple search providers (Brave Search, SearXNG, etc.) with fallback
**Solution option 3**: Add a web search tool that the AI/LLM can use alongside programmatic search

### Problem 2: AI-driven search with parallel background search

Currently:
- DECOMPOSE phase: LLM generates sub-queries
- SEARCH phase: Programmatic DuckDuckGo search for each sub-query (concurrent using asyncio.gather)
- SCRAPE phase: Trafilatura scrape of resulting URLs (semaphore-limited concurrency)

The user wants:
1. AI to be more involved in the search process (e.g., AI reviews search results and decides what to scrape)
2. Background parallel search that runs independently

**Solution**: 
- Create a dual-agent approach: 
  - An AI search agent that can iteratively search, review results, and decide next steps
  - A background programmatic search that runs in parallel, feeding results into a shared queue/ChromaDB
- Alternative: Make the LLM generate the search queries AND also let it browse/review results directly

Actually, I think the simplest interpretation is:
1. Let the AI evaluate search results and decide which URLs to scrape (currently it's just domain dedup + relevance filter)
2. Run multiple search providers in parallel in the background

### Problem 3: ChromaDB cleanup on all exit paths

Current state:
- Cleanup only in success path (line 691-694)
- Error path (703-707): no cleanup
- Cancellation path (698-701): no cleanup

**Solution**: Move cleanup to a `finally` block that runs regardless.

Let me now formulate the full plan.

Plan:

## 1. Fix DuckDuckGo Search Issues
- Update `duckduckgo_search` library API usage if needed
- Add proper error handling with fallbacks
- Optionally add alternative search providers (e.g., `httpx`-based web search, SearXNG, or use a different search backend)

## 2. AI-Guided Search with Parallel Background Search
- Restructure the search phase so that:
  a. LLM generates search queries (as currently done)
  b. A background task runs programmatic search (DDGS, etc.) for all queries in parallel
  c. The LLM receives search results and selects/scopes which URLs to scrape
  d. Both the programmatic results and AI-selected URLs are merged for scraping
- This could be implemented as an interleaved process where the AI "browses" (via LLM calls that get search results + snippets) to guide the direction, while the scraper harvests in the background

## 3. ChromaDB Cleanup on All Exit Paths
- Move `rag.delete_collection()` to a `finally` block in the `run()` method
- Ensure cleanup runs on success, cancellation, and error

Let me now present this to the user and get their feedback before implementing.

Now I have a clear picture. Let me present the plan.

---

## Analysis & Plan

### Problem 1: DuckDuckGo Errors / Deprecation

**Root cause**: `research_engine.py:228-229` — uses `DDGS().text(query, max_results=n)`. The `duckduckgo_search` library v7+ changed its API, and DuckDuckGo actively rate-limits/bots. Searches silently fail (line 247-248: `except Exception: return []`), so errors are hidden.

**Plan**:

1. **Fix DDGS API compatibility** — update `_ddg_search()` to match the latest `duckduckgo_search` API (the `text()` method signature changed). Pin a working version in `requirements.txt`.
2. **Add search provider abstraction** — create a `SearchProvider` base class with implementations:
   - `DuckDuckGoProvider` (fixed + more resilient, with proxy/retry support)
   - `HTTPProvider` (uses `httpx` to directly query search engine endpoints — faster, no library dependency)
   - Optionally: Brave Search, SearXNG, or Google Custom Search as additional providers
3. **Add automatic fallback** — if one provider fails, try the next. Log which provider is being used.
4. **Better error surfacing** — surface search failures to the UI instead of silently returning empty lists.

### Problem 2: AI-Guided Search with Parallel Background Search

**Current flow**:
```
DECOMPOSE → LLM makes sub-queries
  SEARCH → DDG searches each (concurrent but synchronous with pipeline)
  SCRAPE → fetch all URLs
  EXTRACT → LLM extracts facts from scraped content
```

**Issue**: The LLM has no feedback loop into the search — it can't drill deeper on promising results, pivot on dead ends, or evaluate result quality before scraping.

**Plan**: Restructure into a **dual-loop architecture**:

```
┌─────────────────────────────────────────────────────┐
│  AI Search Loop (drives direction)                  │
│    LLM proposes search queries                       │
│    ↓                                                 │
│    LLM reviews search results (titles + snippets)    │
│    ↓                                                 │
│    LLM selects URLs to scrape + proposes follow-ups  │
│    ↓                                                 │
│    (repeats until satisfied or time runs out)        │
└─────────────────────────────────────────────────────┘
                        ↕  shared queue
┌─────────────────────────────────────────────────────┐
│  Background Scraper (runs continuously)             │
│    Consumes URLs from queue                         │
│    Trafilatura scrape → ChromaDB ingest             │
│    High concurrency, retries                        │
└─────────────────────────────────────────────────────┘
                        ↕  shared ChromaDB
┌─────────────────────────────────────────────────────┐
│  Background Programmatic Search (parallel)          │
│    DDG + other providers                            │
│    Feeds results directly into scrape queue         │
└─────────────────────────────────────────────────────┘
```

Concretely in code:
1. Replace the sequential `_search_all` → `_scrape_and_ingest` with concurrent tasks running via `asyncio.gather` / `asyncio.create_task`.
2. Add an AI-driven search-review step: after the LLM generates sub-queries, run DDG searches but return *snippets + titles* to the LLM. The LLM picks which URLs to scrape.
3. The programmatic search runs as a background `asyncio.Task` that continuously feeds a shared `asyncio.Queue` of (url, query) pairs.
4. The scraper runs as another background task consuming from the same queue.
5. Multiple search queries can be dispatched at once and processed out-of-order.

### Problem 3: ChromaDB Cleanup on All Exit Paths

**Current state**: `rag.delete_collection()` (line 691-694) runs only in the success path. Both `CancelledError` (698) and generic `Exception` (703) skip cleanup.

**Plan**: Move cleanup to a `try/finally` block:

```python
# Pseudocode
try:
    # ... main research logic ...
    return result
except asyncio.CancelledError:
    # ... handle cancellation ...
    raise
except Exception:
    # ... handle error ...
    raise
finally:
    try:
        rag.delete_collection()
    except Exception:
        pass
```

Additionally, ensure the `RAGMemory` object is always created within the same try/finally scope so cleanup always has access to it.

---

### Summary Table

| Problem | Solution | Files to Change |
|---------|----------|----------------|
| **1** — DDG errors/deprecation | Fix API, add provider abstraction + fallback chain | `research_engine.py`, `requirements.txt`, new `search_providers.py` |
| **2** — Random/unguided searches | Dual-loop: AI reviews results + selects URLs; background scraper + search run in parallel as asyncio tasks | `research_engine.py` (restructure `run()` and `_search_all`/`_scrape_and_ingest`) |
| **3** — ChromaDB never cleaned up on error/cancel | Move `delete_collection()` to `finally` block | `research_engine.py` (relocate cleanup in `run()`) |

---

Before I start implementation, a couple of clarifying questions:

**Tool: question**

**Input:**
```json
{
  "questions": [
    {
      "question": "For Problem 1 (search provider), would you like me to add multiple search engine backends (e.g. fallback chain: DuckDuckGo → direct HTTP scraping of search results → Brave Search) or just fix the DuckDuckGo library usage?",
      "header": "Search Providers",
      "options": [
        {
          "label": "Fix DDG only",
          "description": "Just fix the duckduckgo_search API usage and add better error handling"
        },
        {
          "label": "Multiple providers",
          "description": "Add abstract provider with DDG + HTTP fallback + Brave Search support"
        }
      ]
    },
    {
      "question": "For Problem 2 (AI-guided search), how much control should the AI have over the search process?",
      "header": "AI Search Control",
      "options": [
        {
          "label": "AI reviews results",
          "description": "LLM sees search result snippets, picks which URLs to scrape (recommended)"
        },
        {
          "label": "Full AI browsing",
          "description": "LLM can iteratively search, review, and request follow-up searches in a loop"
        },
        {
          "label": "Keep current + background",
          "description": "Keep current LLM→search→scrape flow, but run programmatic search in parallel as background task"
        }
      ]
    },
    {
      "question": "For Problem 3 (ChromaDB cleanup), should I also add a periodic global GC task that purges orphaned collections older than a certain age?",
      "header": "ChromaDB Cleanup Scope",
      "options": [
        {
          "label": "Just fix cleanup",
          "description": "Move to finally block so it always runs"
        },
        {
          "label": "Cleanup + GC",
          "description": "Also add a startup routine that purges orphaned collections older than 24h"
        }
      ]
    }
  ]
}
```

**Output:**
```
User has answered your questions: "For Problem 1 (search provider), would you like me to add multiple search engine backends (e.g. fallback chain: DuckDuckGo → direct HTTP scraping of search results → Brave Search) or just fix the DuckDuckGo library usage?"="Fix DDG only", "For Problem 2 (AI-guided search), how much control should the AI have over the search process?"="AI reviews results", "For Problem 3 (ChromaDB cleanup), should I also add a periodic global GC task that purges orphaned collections older than a certain age?"="Cleanup + GC". You can now continue with the user's answers in mind.
```

---

## Assistant (Plan · DeepSeek V4 Flash Free · 42.8s)

---

## User

continue

---

## Assistant (Build · GLM 4.5 Air (free) · 44.0s)

---

## User

continue

---

## Assistant (Build · Nemotron 3 Ultra (free) · 164.7s)

---

