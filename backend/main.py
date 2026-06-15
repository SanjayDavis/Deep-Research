"""
backend/main.py — Entry point for the Deep Research Python backend.

Protocol: reads CLI arguments, runs the research loop, writes JSON lines to stdout.
Each line is a ProgressEvent consumed by the Tauri Rust layer.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.resolve()))

from research_engine import ResearchEngine, AgentState
from config import Settings, MCP_SERVER_HOST
import asyncio


def emit(
    event_type: str,
    message: str,
    stage: str | None = None,
    pct: int | None = None,
    data=None,
    round_num: int | None = None,
    round_total: int | None = None,
    elapsed: float | None = None,
):
    payload = {
        "type": event_type,
        "stage": stage,
        "message": message,
        "pct": pct,
        "round": round_num,
        "roundTotal": round_total,
        "elapsed": elapsed,
        "data": data,
    }
    sys.stdout.write(json.dumps(payload, default=str) + "\n")
    sys.stdout.flush()


def main():
    parser = argparse.ArgumentParser(description="Deep Research Engine")
    parser.add_argument("topic", help="Research topic")
    parser.add_argument("--provider", default="openrouter")
    parser.add_argument("--base-url", default="https://openrouter.ai/api/v1")
    parser.add_argument("--api-key", default="")
    parser.add_argument("--model", default="google/gemini-2.0-flash-001")
    parser.add_argument("--depth", type=int, default=2)
    parser.add_argument("--rounds", type=int, default=2)
    parser.add_argument("--max-pages", type=int, default=5)
    parser.add_argument("--time-limit", type=int, default=30)
    parser.add_argument("--searxng-url", default="")
    parser.add_argument("--mcp", action="store_true", help="Run as MCP server instead of one-shot research")
    parser.add_argument("--mcp-port", type=int, default=9753, help="Port for MCP server (default: 9753)")
    args = parser.parse_args()

    if args.mcp:
        from mcp_server import run_server
        run_server(host=MCP_SERVER_HOST, port=args.mcp_port)
        return

    settings = Settings(
        provider_name=args.provider,
        base_url=args.base_url,
        api_key=args.api_key or "none",
        model=args.model,
        max_depth=args.depth,
        num_rounds=args.rounds,
        search_results=args.max_pages,
        concurrent_scrape=min(args.max_pages, 10),
        time_limit_minutes=args.time_limit,
        searxng_url=args.searxng_url,
    )

    output_dir = Path.home() / "deep_research_reports"
    output_dir.mkdir(parents=True, exist_ok=True)

    topic = args.topic
    num_rounds = args.rounds

    start_time = time.time()
    current_round = 0

    stage_map = {
        AgentState.DECOMPOSE: "decompose",
        AgentState.SEARCH: "search",
        AgentState.SCRAPE: "scrape",
        AgentState.EXTRACT: "extract",
        AgentState.SYNTHESISE: "synthesise",
        AgentState.DONE: "done",
        AgentState.ERROR: "error",
    }

    def on_log(msg: str):
        nonlocal current_round
        msg_str = str(msg)
        elapsed = round(time.time() - start_time, 1)

        round_match = __import__("re").search(r"\[ROUND (\d+)/(\d+)\]", msg_str)
        if round_match:
            current_round = int(round_match.group(1))

        emit("log", msg_str, elapsed=elapsed, round_num=current_round, round_total=num_rounds)

        if "[SEARCH]" in msg_str and "URLs" in msg_str:
            emit("progress", msg_str, stage="search", pct=30, round_num=current_round, round_total=num_rounds, elapsed=elapsed)
        elif "[SCRAPING]" in msg_str:
            emit("progress", msg_str, stage="scrape", round_num=current_round, round_total=num_rounds, elapsed=elapsed)
        elif "[SCRAPE]" in msg_str and "Done" in msg_str:
            emit("progress", msg_str, stage="scrape", pct=70, round_num=current_round, round_total=num_rounds, elapsed=elapsed)
        elif "[CHUNKING INTO CHROMA]" in msg_str:
            emit("progress", msg_str, stage="chunk", round_num=current_round, round_total=num_rounds, elapsed=elapsed)
        elif "[CHROMA]" in msg_str and "collection" in msg_str:
            emit("progress", msg_str, stage="chunk", round_num=current_round, round_total=num_rounds, elapsed=elapsed)
        elif "[EXTRACT]" in msg_str:
            emit("progress", msg_str, stage="extract", round_num=current_round, round_total=num_rounds, elapsed=elapsed)
        elif "[SYNTHESISE]" in msg_str:
            emit("progress", msg_str, stage="synthesise", round_num=current_round, round_total=num_rounds, elapsed=elapsed)
        elif "[DONE]" in msg_str:
            emit("progress", "Research complete", stage="done", pct=100, round_num=current_round, round_total=num_rounds, elapsed=elapsed)

    def on_state(state: AgentState):
        nonlocal current_round
        stage = stage_map.get(state)
        if stage:
            pct_map = {
                AgentState.DECOMPOSE: 5,
                AgentState.SEARCH: 15,
                AgentState.SCRAPE: 40,
                AgentState.EXTRACT: 60,
                AgentState.SYNTHESISE: 80,
            }
            elapsed = round(time.time() - start_time, 1)
            emit(
                "progress",
                f"Phase: {state.name}",
                stage=stage,
                pct=pct_map.get(state),
                round_num=current_round,
                round_total=num_rounds,
                elapsed=elapsed,
            )

    stop_event = asyncio.Event()

    engine = ResearchEngine(
        settings=settings,
        on_log=on_log,
        on_state=on_state,
        stop_event=stop_event,
    )

    try:
        result = asyncio.run(engine.run(topic))

        if result.markdown:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_topic = "".join(c if c.isalnum() or c in " _-" else "_" for c in topic)[:60]
            base_name = f"{ts}_{safe_topic}"
            md_path = output_dir / f"{base_name}.md"
            meta_path = output_dir / f"{base_name}.json"

            # Atomic write: write to temp, then rename
            import tempfile
            import os
            
            # Write markdown
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=output_dir, delete=False, suffix='.md') as tmp:
                tmp.write(result.markdown)
                tmp_path = tmp.name
            os.replace(tmp_path, md_path)
            
            # Verify markdown was written
            if not md_path.exists() or md_path.stat().st_size == 0:
                raise RuntimeError(f"Report file not created or empty: {md_path}")
            
            # Write metadata
            metadata = {
                "topic": topic,
                "session_id": result.session_id,
                "timestamp": ts,
                "sources": result.sources,
                "total_chunks": result.total_chunks,
                "depth_used": result.depth_used,
                "rounds_completed": args.rounds,
                "model": args.model,
                "report_path": str(md_path),
                "report_size_bytes": md_path.stat().st_size,
            }
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=output_dir, delete=False, suffix='.json') as tmp:
                json.dump(metadata, tmp, indent=2)
                tmp_path = tmp.name
            os.replace(tmp_path, meta_path)

            emit("result", "Report generated", data={
                "path": str(md_path),
                "content": result.markdown,
                "metadata_path": str(meta_path),
            })
            emit("log", f"[STORAGE] Report saved to {md_path} ({md_path.stat().st_size:,} bytes)")
            emit("log", f"[STORAGE] Metadata saved to {meta_path}")
        else:
            emit("error", "Research produced no output.")

    except Exception as exc:
        emit("error", f"Research failed: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
