# Deep Research

Autonomous web research desktop application. Enter a topic, and the agent searches the web, extracts content, builds a local RAG index, and synthesizes a comprehensive markdown report with citations.

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

**Pipeline:** Decompose → Search (DuckDuckGo) → Scrape (Trafilatura) → Chunk (ChromaDB) → Extract (RAG + LLM) → Gap-fill → Synthesise

## Requirements

- **Node.js** 18+
- **Rust** (via rustup)
- **Python** 3.11+
- **Linux:** webkit2gtk-4.1 (for Tauri)

## Quick Start

```bash
# Install dependencies
./setup.sh

# Development
npm run tauri:dev

# Production build
npm run tauri:build
```

## First Run

1. Open **Settings** → select a provider (OpenRouter, LM Studio, or OpenCode Proxy)
2. Enter API key if required → **Connect** → choose a model
3. Click **Save Settings**
4. Enter a research topic and click **Research**

Reports are saved to `~/deep_research_reports/`.

## Configuration

| Setting | Description | Default |
|---------|-------------|---------|
| Depth | Gap-fill iterations per round | 4 |
| Pages / Query | Search results scraped per query | 15 |
| Rounds | Full pipeline passes | 3 |

## Providers

| Provider | Base URL | API Key |
|----------|----------|---------|
| OpenRouter | `https://openrouter.ai/api/v1` | Required |
| LM Studio | `http://localhost:1234/v1` | Optional |
| OpenCode Proxy | `http://127.0.0.1:4010/v1` | Optional |

## Project Structure

```
├── src/                  # React frontend
├── src-tauri/            # Tauri shell + Rust commands
├── backend/              # Python research engine
│   ├── main.py           # CLI entry (JSON stdout protocol)
│   ├── research_engine.py
│   ├── rag_memory.py
│   └── output_formatter.py
└── setup.sh              # CachyOS/Arch setup script
```

## License

Private — all rights reserved.
