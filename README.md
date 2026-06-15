# Deep Research

**Autonomous web research desktop application** — enter a topic and let the agent search the web, extract content, build a local RAG index, and synthesize a comprehensive markdown report with citations.

---

## Features

- **Multi-provider LLM support** — OpenRouter, LM Studio, OpenCode Proxy, or any OpenAI-compatible API
- **RAG-powered extraction** — ChromaDB vector store for semantic retrieval across scraped content
- **Concurrent search & scraping** — DuckDuckGo search + Trafilatura extraction with parallel workers
- **Multi-round research** — iterative refinement across configurable rounds and gap-fill depth
- **Desktop native** — Tauri shell with a React/Tailwind UI, no Electron overhead
- **Real-time progress** — live JSON-streamed pipeline events displayed in the UI
- **MCP server mode** — run as a Model Context Protocol server for agent integration
- **Report management** — organized output with markdown reports and metadata saved to disk

---

## Architecture

```
┌─────────────────┐     JSON events      ┌──────────────────┐
│  React UI       │ ◄─────────────────── │  Tauri (Rust)    │
│  (Vite + TS)    │ ── invoke commands ─►│  Bridge          │
└─────────────────┘                      └────────┬─────────┘
                                                  │ spawns
                                                  ▼
                                         ┌──────────────────┐
                                         │  Python Backend  │
                                         │  research_engine │
                                         └──────────────────┘
```

### Research Pipeline

1. **Decompose** — break user query into sub-queries
2. **Search** — concurrent DuckDuckGo searches per sub-query
3. **Scrape** — Trafilatura content extraction with retry logic
4. **Chunk** — text split into overlapping segments, embedded into ChromaDB
5. **Extract** — RAG retrieval + single LLM call for fact extraction
6. **Synthesise** — final LLM pass compiles the structured report
7. **Repeat** — configurable rounds with gap analysis for deeper coverage

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, TypeScript, Vite, Tailwind CSS, Zustand |
| Desktop | Tauri 2 (Rust) |
| Backend | Python 3.11+, asyncio |
| Search | DuckDuckGo (`ddgs`), optional SearXNG |
| Scraping | Trafilatura |
| Vector Store | ChromaDB |
| LLM Protocol | OpenAI-compatible HTTP API |

---

## Prerequisites

- **Node.js** 18+
- **Rust** (via `rustup`)
- **Python** 3.11+
- **Linux:** `webkit2gtk-4.1` (Tauri dependency)

---

## Quick Start

```bash
# Install all dependencies (Node, Python venv, Tauri system deps)
./setup.sh

# Launch in development mode
npm run tauri:dev

# Production build
npm run tauri:build
```

---

## First Run

1. Open **Settings** → select a provider (OpenRouter, LM Studio, or OpenCode Proxy)
2. Enter API key if required → click **Connect**
3. Choose a model from the populated list → click **Save Settings**
4. Enter a research topic in the main input → click **Research**
5. Watch real-time progress as the agent searches, scrapes, and synthesises

Reports are saved to `~/deep_research_reports/` as `.md` + `.json` metadata pairs.

---

## Configuration

### Research Parameters

| Setting | Description | Default |
|---------|-------------|---------|
| Depth | Gap-fill iterations per round | 3 |
| Pages / Query | Search results scraped per sub-query | 25 |
| Rounds | Full pipeline passes | 2 |
| Time Limit | Hard stop for research (minutes) | 30 |

### LLM Providers

| Provider | Base URL | API Key |
|----------|----------|---------|
| OpenRouter | `https://openrouter.ai/api/v1` | Required |
| LM Studio | `http://localhost:1234/v1` | Optional |
| OpenCode Proxy | `http://127.0.0.1:4010/v1` | Optional |
| Custom | User-defined | User-defined |

### Persistence

Settings are saved to `backend/settings.json` and persist across restarts. Reports and metadata are stored in `~/deep_research_reports/`.

---

## Project Structure

```
├── src/                    # React frontend (Vite + TypeScript)
│   ├── components/         # UI components by domain
│   ├── hooks/              # Custom React hooks
│   ├── lib/                # API client, types, utilities
│   ├── stores/             # Zustand state stores
│   └── styles/             # Global CSS
├── src-tauri/              # Tauri Rust shell
│   └── src/commands/       # Rust command handlers
├── backend/                # Python research engine
│   ├── main.py             # CLI entry point (JSON stdout protocol)
│   ├── research_engine.py  # Core async research agent
│   ├── rag_memory.py       # ChromaDB vector store wrapper
│   ├── output_formatter.py # Report synthesis
│   ├── config.py           # Settings dataclass + persistence
│   └── requirements.txt    # Python dependencies
├── setup.sh                # CachyOS/Arch setup script
└── launch.sh                # Installed binary launcher
```

---

## Development

```bash
# Start Vite dev server (frontend only)
npm run dev

# Run Tauri dev (full app)
npm run tauri:dev

# Backend standalone (without Tauri)
python backend/main.py "your topic" --provider openrouter --api-key <key>
```

---

## MCP Server Mode

The backend can run as a Model Context Protocol server for integration with agent frameworks:

```bash
python backend/main.py --mcp --mcp-port 9753
```

---

## License

Private — all rights reserved.
