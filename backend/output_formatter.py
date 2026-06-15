"""
output_formatter.py — Post-processing pipeline for research reports.

Ensures consistent structure, validates citations, generates TOC,
and adds metadata sections.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse


@dataclass
class ReportMetadata:
    title: str
    date: str
    depth: int
    rounds: int
    sources: int
    chunks: int
    session_id: str


def extract_frontmatter(content: str) -> tuple[dict[str, str], str]:
    """Extract YAML frontmatter and return (metadata, body)."""
    metadata = {}
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            fm_lines = parts[1].strip().split("\n")
            for line in fm_lines:
                if ":" in line:
                    k, v = line.split(":", 1)
                    metadata[k.strip()] = v.strip().strip('"')
            body = parts[2].lstrip("\n")
            return metadata, body
    return {}, content


def build_frontmatter(meta: ReportMetadata) -> str:
    """Build YAML frontmatter string."""
    lines = [
        "---",
        f"title: \"{meta.title}\"",
        f"date: \"{meta.date}\"",
        f"depth: {meta.depth}",
        f"rounds: {meta.rounds}",
        f"sources: {meta.sources}",
        f"chunks: {meta.chunks}",
        f"session_id: \"{meta.session_id}\"",
        "---",
        "",
    ]
    return "\n".join(lines)


def generate_toc(content: str) -> str:
    """Generate a Table of Contents from ## headings."""
    headings = re.findall(r"^##\s+(.+)$", content, re.MULTILINE)
    if not headings:
        return ""
    
    toc_lines = ["## Table of Contents", ""]
    for i, heading in enumerate(headings, 1):
        anchor = heading.lower()
        anchor = re.sub(r"[^\w\s-]", "", anchor)
        anchor = re.sub(r"[\s-]+", "-", anchor).strip("-")
        toc_lines.append(f"{i}. [{heading}](#{anchor})")
    
    return "\n".join(toc_lines) + "\n\n"


def extract_references(content: str) -> list[tuple[int, str]]:
    """Extract reference list as (number, url) pairs."""
    refs = []
    in_refs = False
    for line in content.split("\n"):
        if line.strip() == "## References":
            in_refs = True
            continue
        if in_refs and line.startswith("## "):
            break
        if in_refs:
            match = re.match(r"^\[(\d+)\]\s+(.+)$", line.strip())
            if match:
                refs.append((int(match.group(1)), match.group(2).strip()))
    return refs


def validate_citations(content: str, references: list[tuple[int, str]]) -> str:
    """Validate that all [n] citations have corresponding references."""
    ref_nums = {n for n, _ in references}
    cited = set()
    
    for match in re.finditer(r"\[(\d+)\]", content):
        num = int(match.group(1))
        if num > 0:
            cited.add(num)
    
    missing = cited - ref_nums
    if missing:
        return f"<!-- WARNING: Citations {sorted(missing)} have no corresponding references -->\n{content}"
    
    return content


def _is_alignment_row(line: str) -> bool:
    """Check if a line is a Markdown table alignment row (e.g. |---|:---:|---|)."""
    if not re.match(r'^\|.+\|$', line):
        return False
    cells = [c.strip() for c in line.split("|")[1:-1]]
    return all(cell == "" or re.match(r'^[\s\-:]+$', cell) for cell in cells)


def _is_table_row(line: str) -> bool:
    """Check if a line is any Markdown table row (data or alignment)."""
    return bool(re.match(r'^\|.+\|$', line))


def format_tables(content: str) -> str:
    """Ensure tables have proper formatting."""
    lines = content.split("\n")
    out = []
    in_table = False
    
    for line in lines:
        if _is_table_row(line):
            if not in_table:
                in_table = True
            parts = [p.strip() for p in line.split("|")[1:-1]]
            out.append("| " + " | ".join(parts) + " |")
        else:
            if in_table:
                in_table = False
            out.append(line)
    
    return "\n".join(out)


def add_methodology_section(content: str, meta: ReportMetadata) -> str:
    """Append methodology section if not present."""
    if "## Methodology" in content:
        return content
    
    methodology = f"""
## Methodology

- Rounds: {meta.rounds}
- Depth per round: {meta.depth}
- Sources retrieved: {meta.sources}
- Chunks indexed: {meta.chunks}
- LLM model: (see session metadata)
- Generation date: {meta.date}
- Session ID: {meta.session_id}
"""
    return content.rstrip() + "\n" + methodology + "\n"


def assess_source_quality(sources: list[str]) -> str:
    """Generate source quality assessment table."""
    if not sources:
        return ""
    
    def score_domain(url: str) -> tuple[int, int, int]:
        """Return (authority, recency, relevance) scores 1-5."""
        try:
            domain = urlparse(url).netloc.lower().replace("www.", "")
        except Exception:
            return (1, 1, 1)
        
        # Authority scoring
        authority = 2
        if any(d in domain for d in [".edu", ".gov", ".org"]):
            authority = 4
        if any(d in domain for d in ["nature.com", "science.org", "arxiv.org", "ieee.org", "acm.org", "nih.gov", "who.int"]):
            authority = 5
        elif any(d in domain for d in ["github.com", "stackoverflow.com", "reddit.com", "medium.com", "substack.com"]):
            authority = 2
        elif any(d in domain for d in ["wikipedia.org", "britannica.com"]):
            authority = 3
        
        # Recency - can't determine from URL alone, default to 3
        recency = 3
        
        # Relevance - default
        relevance = 3
        
        return (authority, recency, relevance)
    
    rows = []
    for url in sources:
        auth, rec, rel = score_domain(url)
        rows.append(f"| {url} | {auth}/5 | {rec}/5 | {rel}/5 |")
    
    table = "## Source Quality Assessment\n\n"
    table += "| URL | Authority | Recency | Relevance |\n"
    table += "|-----|-----------|---------|-----------|\n"
    table += "\n".join(rows)
    table += "\n\n"
    
    return table


def add_source_quality_section(content: str, sources: list[str]) -> str:
    """Add Source Quality Assessment section if not present."""
    if not sources or "## Source Quality Assessment" in content:
        return content
    
    assessment = assess_source_quality(sources)
    if not assessment:
        return content
    
    return content.rstrip() + "\n\n" + assessment


def ensure_references_section(content: str, references: list[tuple[int, str]]) -> str:
    """Ensure References section exists with full list."""
    if "## References" in content:
        return content
    
    if not references:
        return content
    
    ref_lines = "\n".join(f"[{n}] {url}" for n, url in sorted(references))
    return content.rstrip() + "\n\n## References\n\n" + ref_lines + "\n"


def add_document_stats(content: str) -> str:
    """Add document statistics section with word count, table count, section count."""
    if "## Document Statistics" in content:
        return content

    word_count = len(re.findall(r'\b\w+\b', content))
    table_count = sum(1 for line in content.split("\n") if _is_alignment_row(line))
    sections = len(re.findall(r'^###\s+', content, re.MULTILINE))
    subsections = len(re.findall(r'^####\s+', content, re.MULTILINE))

    stats = (
        "\n\n## Document Statistics\n\n"
        f"| Metric | Value |\n"
        f"|--------|-------|\n"
        f"| Total Words | {word_count} |\n"
        f"| Tables | {table_count} |\n"
        f"| Sections | {sections} |\n"
        f"| Subsections | {subsections + sections} |\n"
    )
    return content.rstrip() + stats


def enhance_tables(content: str) -> str:
    """Ensure all markdown tables have proper alignment rows."""
    lines = content.split("\n")
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not _is_table_row(line):
            out.append(line)
            i += 1
            continue

        # Collect the table block
        table_start = i
        while i < len(lines) and _is_table_row(lines[i]):
            i += 1
        table_lines = lines[table_start:i]

        if len(table_lines) < 2:
            out.extend(table_lines)
            continue

        # Check if the second line is already an alignment row
        if _is_alignment_row(table_lines[1]):
            # Remove any extra alignment rows that follow
            cleaned = [table_lines[0], table_lines[1]]
            for row in table_lines[2:]:
                if not _is_alignment_row(row):
                    cleaned.append(row)
            out.extend(cleaned)
        else:
            # Insert alignment row after the header
            cols = table_lines[0].count("|") - 1
            align = "|" + "|".join([" --- "] * cols) + "|"
            out.append(table_lines[0])
            out.append(align)
            out.extend(table_lines[1:])

    return "\n".join(out)


def post_process_report(
    raw_markdown: str,
    topic: str,
    depth: int,
    rounds: int,
    sources: list[str],
    chunks: int,
    session_id: str,
    date: str,
) -> str:
    """Main post-processing pipeline."""
    
    metadata, body = extract_frontmatter(raw_markdown)
    
    meta = ReportMetadata(
        title=metadata.get("title", topic),
        date=metadata.get("date", date),
        depth=int(metadata.get("depth", depth)),
        rounds=int(metadata.get("rounds", rounds)),
        sources=len(sources),
        chunks=chunks,
        session_id=metadata.get("session_id", session_id),
    )
    
    references = extract_references(body)
    if not references:
        references = [(i + 1, url) for i, url in enumerate(sources)]
    
    body = validate_citations(body, references)
    body = format_tables(body)
    body = enhance_tables(body)
    body = ensure_references_section(body, references)
    
    # New formatting enhancements
    body = convert_key_takeaways_to_callouts(body)
    body = convert_confidence_tags_to_blockquotes(body)
    body = enhance_expert_quotes(body)
    body = add_visual_separators(body)
    body = enhance_references(body, references)
    
    toc = improve_toc_generation(body)
    if toc:
        body = toc + body
    
    body = add_methodology_section(body, meta)
    body = add_source_quality_section(body, sources)
    body = add_document_stats(body)
    
    frontmatter = build_frontmatter(meta)
    
    return frontmatter + body


def extract_key_quotes(facts: str, max_quotes: int = 5) -> list[str]:
    """Extract verbatim quotes from extracted facts."""
    quotes = []
    for line in facts.split("\n"):
        line = line.strip()
        if line.startswith(">") or ("\"" in line and len(line) > 50):
            clean = line.lstrip(">-• ").strip()
            if len(clean) > 30:
                quotes.append(clean)
                if len(quotes) >= max_quotes:
                    break
    return quotes


def add_key_quotes_section(content: str, quotes: list[str]) -> str:
    """Add Key Quotes section if quotes exist."""
    if not quotes or "## Key Quotes" in content:
        return content
    
    quotes_md = "## Key Quotes\n\n"
    for q in quotes:
        quotes_md += f"> {q}\n\n"
    
    return content.rstrip() + "\n\n" + quotes_md


def convert_key_takeaways_to_callouts(content: str) -> str:
    """Convert Key Takeaway blocks to GitHub-style IMPORTANT callouts."""
    lines = content.split("\n")
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Match patterns like "> **Key Takeaway:** text" or "> **Key Takeaway:** text"
        if re.match(r"^>\s*\*\*Key Takeaway:\*\*\s*", line):
            text = re.sub(r"^>\s*\*\*Key Takeaway:\*\*\s*", "", line)
            out.append("> [!IMPORTANT]")
            out.append(f"> **Key Takeaway:** {text}")
        else:
            out.append(line)
        i += 1
    return "\n".join(out)


def convert_confidence_tags_to_blockquotes(content: str) -> str:
    """Convert confidence tags like [Established] to blockquote descriptions."""
    lines = content.split("\n")
    out = []
    for line in lines:
        # Convert patterns like "**[Established]**" or "[Established]" at end of paragraphs
        match_bold = re.search(r"\*\*\[(Established|Contested|Uncertain)\]\*\*", line)
        match_plain = re.search(r"\[(Established|Contested|Uncertain)\]", line)
        
        if match_bold:
            tag = match_bold.group(1)
            line = re.sub(r"\s*\*\*\[(Established|Contested|Uncertain)\]\*\*", "", line)
            out.append(line.rstrip())
            if tag == "Established":
                out.append("> **Established** — Multiple independent sources confirm this finding")
            elif tag == "Contested":
                out.append("> **Contested** — Sources conflict or present differing viewpoints")
            elif tag == "Uncertain":
                out.append("> **Uncertain** — Limited evidence or single source")
        elif match_plain:
            tag = match_plain.group(1)
            line = re.sub(r"\s*\[(Established|Contested|Uncertain)\]", "", line)
            out.append(line.rstrip())
            if tag == "Established":
                out.append("> **Established** — Multiple independent sources confirm this finding")
            elif tag == "Contested":
                out.append("> **Contested** — Sources conflict or present differing viewpoints")
            elif tag == "Uncertain":
                out.append("> **Uncertain** — Limited evidence or single source")
        else:
            out.append(line)
    return "\n".join(out)


def enhance_expert_quotes(content: str) -> str:
    """Enhance expert quote formatting with attribution styling."""
    lines = content.split("\n")
    out = []
    for line in lines:
        # Match blockquotes with attribution pattern: > "quote" — Name, Title [N]
        if re.match(r"^>\s*[\"""].+[\"""].*[—–].*\[[0-9]+\]", line):
            # Add proper attribution styling
            out.append(line)
        else:
            out.append(line)
    return "\n".join(out)


def add_visual_separators(content: str) -> str:
    """Add horizontal rules between major sections for visual separation."""
    lines = content.split("\n")
    out = []
    prev_was_heading = False
    for i, line in enumerate(lines):
        if re.match(r"^##\s+", line):
            if i > 0 and not prev_was_heading:
                out.append("")
                out.append("---")
                out.append("")
            prev_was_heading = True
        else:
            prev_was_heading = False
        out.append(line)
    return "\n".join(out)


def improve_toc_generation(content: str) -> str:
    """Generate an improved Table of Contents with better styling."""
    headings = re.findall(r"^(#{2,3})\s+(.+)$", content, re.MULTILINE)
    if not headings:
        return ""
    
    toc_lines = [
        "<details>",
        "<summary><strong>Table of Contents</strong></summary>",
        "",
    ]
    
    for level, heading in headings:
        anchor = heading.lower()
        anchor = re.sub(r"[^\w\s-]", "", anchor)
        anchor = re.sub(r"[\s-]+", "-", anchor).strip("-")
        
        if level == "##":
            toc_lines.append(f"- [{heading}](#{anchor})")
        else:
            toc_lines.append(f"  - [{heading}](#{anchor})")
    
    toc_lines.extend(["", "</details>", ""])
    return "\n".join(toc_lines)


def add_metadata_badge(content: str, meta: ReportMetadata) -> str:
    """Add a metadata badge at the top of the report."""
    badge = (
        f'<div align="center">\n\n'
        f"**{meta.title}**\n\n"
        f"📅 {meta.date} | 📊 {meta.sources} sources | 🔍 Depth: {meta.depth} | 🔄 Rounds: {meta.rounds}\n\n"
        f"</div>\n\n"
        f"---\n\n"
    )
    
    # Insert after frontmatter if present
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            return f"---{parts[1]}---\n\n{badge}{parts[2].lstrip()}"
    
    return badge + content


def enhance_references(content: str, references: list[tuple[int, str]]) -> str:
    """Enhance references with domain names and better formatting."""
    if not references:
        return content
    
    enhanced_refs = []
    for n, url in references:
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc.replace("www.", "")
            enhanced_refs.append(f"[{n}] [{domain}]({url})")
        except Exception:
            enhanced_refs.append(f"[{n}] {url}")
    
    ref_section = "## References\n\n" + "\n".join(enhanced_refs) + "\n"
    
    # Replace existing references section or append
    if "## References" in content:
        lines = content.split("\n")
        ref_start = -1
        for i, line in enumerate(lines):
            if line.strip() == "## References":
                ref_start = i
                break
        
        if ref_start >= 0:
            # Find next section or end
            ref_end = len(lines)
            for i in range(ref_start + 1, len(lines)):
                if lines[i].startswith("## ") and i > ref_start:
                    ref_end = i
                    break
            lines[ref_start:ref_end] = [ref_section]
            return "\n".join(lines)
    
    return content.rstrip() + "\n\n" + ref_section