"""
config.py — Application-wide configuration for the Deep Research Tool.
All user-tunable defaults live here; the GUI writes back to a JSON file
in the same directory so settings persist across restarts.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────

APP_DIR = Path(__file__).parent.resolve()
SETTINGS_FILE = APP_DIR / "settings.json"
DEFAULT_OUTPUT_DIR = Path.home() / "deep_research_reports"
DEFAULT_CHROMA_PATH = Path.home() / ".local" / "share" / "deep_research" / "chroma"

# OpenCode binary location — use env var, then which(), then default
_which = __import__("shutil", fromlist=["which"]).which
OPENCODE_BINARY = Path(
    os.environ.get("OPENCODE_BINARY")
    or (_which("opencode") if _which else "")
    or "/usr/local/bin/opencode"
)
OPENCODE_PROXY_BASE = "http://127.0.0.1:4010/v1"

# ── LLM Provider Presets ──────────────────────────────────────────────────────

PROVIDER_PRESETS: dict[str, dict] = {
    "LM Studio (local)": {
        "base_url": "http://localhost:1234/v1",
        "api_key": "lm-studio",          # LM Studio ignores the key
        "model": "local-model",
    },
    "OpenRouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "api_key": "",                   # user must supply
        "model": "openai/gpt-4o-mini",
    },
    "OpenCode Proxy": {
        "base_url": OPENCODE_PROXY_BASE,
        "api_key": "opencode",
        "model": "auto",
    },
    "Custom": {
        "base_url": "http://localhost:1234/v1",
        "api_key": "",
        "model": "",
    },
}

# ── Research Defaults ─────────────────────────────────────────────────────────

DEFAULT_MAX_DEPTH: int = 3          # gap-fill iterations per round (disabled by default, kept small)
DEFAULT_NUM_ROUNDS: int = 2         # full pipeline iterations (quality > quantity per round)
DEFAULT_TOP_K: int = 25             # chunks retrieved per retrieval query
DEFAULT_CHUNK_SIZE: int = 1200      # characters per RAG chunk (fewer, richer chunks)
DEFAULT_CHUNK_OVERLAP: int = 150    # overlap between adjacent chunks
DEFAULT_SEARCH_RESULTS: int = 25    # DuckDuckGo results per sub-query
DEFAULT_CONCURRENT_SCRAPE: int = 20 # parallel scrape tasks
DEFAULT_TIME_LIMIT_MINUTES: int = 30  # hard stop for research

# ── MCP Server ────────────────────────────────────────────────────────────────

MCP_SERVER_HOST = "127.0.0.1"
MCP_SERVER_PORT = 9_753             # default; user-configurable

# ── Dataclass — persisted settings ────────────────────────────────────────────

@dataclass
class Settings:
    # LLM
    provider_name: str = "LM Studio (local)"
    base_url: str = "http://localhost:1234/v1"
    api_key: str = "lm-studio"
    model: str = "local-model"

    # RAG
    chroma_path: str = str(DEFAULT_CHROMA_PATH)
    chunk_size: int = DEFAULT_CHUNK_SIZE
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP
    top_k: int = DEFAULT_TOP_K

    # Research loop
    max_depth: int = DEFAULT_MAX_DEPTH
    num_rounds: int = DEFAULT_NUM_ROUNDS
    search_results: int = DEFAULT_SEARCH_RESULTS
    concurrent_scrape: int = DEFAULT_CONCURRENT_SCRAPE
    time_limit_minutes: int = DEFAULT_TIME_LIMIT_MINUTES

    # Search
    searxng_url: str = ""

    # Output
    output_dir: str = str(DEFAULT_OUTPUT_DIR)

    # MCP
    mcp_enabled: bool = False
    mcp_port: int = MCP_SERVER_PORT

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Settings":
        valid = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
        return cls(**valid)


def load_settings() -> Settings:
    """Load persisted settings; fall back to defaults on any error."""
    if SETTINGS_FILE.exists():
        try:
            raw = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
            return Settings.from_dict(raw)
        except Exception:
            pass
    return Settings()


def save_settings(settings: Settings) -> None:
    """Persist settings to JSON alongside the application."""
    SETTINGS_FILE.write_text(
        json.dumps(settings.to_dict(), indent=2),
        encoding="utf-8",
    )
