"""Basic tests for output_formatter."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from output_formatter import (  # noqa: E402
    extract_frontmatter,
    validate_citations,
    build_frontmatter,
    ReportMetadata,
)


def test_extract_frontmatter():
    content = '---\ntitle: "Test"\ndate: "2026-01-01"\n---\n\n# Body'
    meta, body = extract_frontmatter(content)
    assert meta["title"] == "Test"
    assert "# Body" in body


def test_validate_citations_warns_on_missing():
    content = "Claim [99] here.\n\n## References\n\n[1] https://example.com"
    refs = [(1, "https://example.com")]
    result = validate_citations(content, refs)
    assert "WARNING" in result


def test_build_frontmatter():
    meta = ReportMetadata(
        title="Topic",
        date="2026-01-01",
        depth=2,
        rounds=1,
        sources=3,
        chunks=10,
        session_id="abc123",
    )
    fm = build_frontmatter(meta)
    assert 'title: "Topic"' in fm
    assert "session_id:" in fm
