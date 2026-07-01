"""
FPT Software — AI-First Research & Detailed Report Dashboard
FastAPI backend: SSE pipeline streaming + file downloads + localtunnel bypass
"""
import json
import os
import sys
import time
import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import StreamingResponse, FileResponse, Response, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.graph import app as graph_app
from src.utils.cleaner import clean_internal_filenames
from config import WORKSPACE_DIR, OUTPUT_DIR

# ── Encoding ──────────────────────────────────────────────────────────────────
for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

# ── Concurrent pipeline protection (thread-safe via asyncio.Lock) ────────────
_pipeline_lock = asyncio.Lock()

# ── Lifespan: replaces deprecated @app.on_event("startup") ──────────────────
@asynccontextmanager
async def lifespan(app_instance):
    # Startup: pre-initialize RAG cached documents in memory
    from src.tools.rag_tools import get_all_docs
    print("Pre-initializing RAG documents in memory...")
    try:
        await asyncio.to_thread(get_all_docs)
        print("RAG documents cached in memory and ready!")
    except Exception as e:
        print(f"Failed to pre-initialize RAG documents: {e}")
    yield
    # Shutdown: cleanup if needed
    print("Shutting down...")

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="FPT Software AI-First Research & Detailed Report Dashboard",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "https://bookmind-socratic-agent.onrender.com",
        "https://bookmind-socratic-agent.vercel.app",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# ── Serve frontend assets with read-only/serverless compatibility ────
try:
    FRONTEND_DIR = Path(WORKSPACE_DIR) / "frontend"
    # Find customized frontend directory dynamically
    if not FRONTEND_DIR.exists():
        for d in os.listdir(WORKSPACE_DIR):
            if d.endswith("-frontend") and os.path.isdir(os.path.join(WORKSPACE_DIR, d)):
                FRONTEND_DIR = Path(WORKSPACE_DIR) / d
                break
                
    # Only make directories if they don't exist yet to reduce write operations
    if not FRONTEND_DIR.exists():
        try:
            FRONTEND_DIR.mkdir(exist_ok=True)
        except Exception:
            pass
            
    lib_dir = FRONTEND_DIR / "lib"
    if not lib_dir.exists():
        try:
            lib_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass
            
    fonts_dir = FRONTEND_DIR / "webfonts"
    if not fonts_dir.exists():
        try:
            fonts_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass

    # Mount static assets under /assets, /lib, /webfonts
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIR)), name="assets")
    app.mount("/lib", StaticFiles(directory=str(lib_dir)), name="lib")
    app.mount("/webfonts", StaticFiles(directory=str(fonts_dir)), name="webfonts")
except Exception as e:
    print(f"Skipping static files mount on read-only serverless: {e}")


# ── Bypass header helper (only tunnel/CDN bypass headers, no encoding) ───────
BYPASS_HEADERS = {
    "Bypass-Tunnel-Reminder": "true",
    "ngrok-skip-browser-warning": "true",
    "X-Accel-Buffering": "no",
    "Cache-Control": "no-cache, no-transform",
}


# ── Middleware: inject bypass headers on every response ───────────────────────
class BypassHeadersMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                for k, v in BYPASS_HEADERS.items():
                    key_bytes = k.lower().encode("utf-8")
                    val_bytes = v.encode("utf-8")
                    if not any(h[0] == key_bytes for h in headers):
                        headers.append((key_bytes, val_bytes))
                message["headers"] = headers
            await send(message)

        await self.app(scope, receive, send_wrapper)

app.add_middleware(BypassHeadersMiddleware)


# ─────────────────────────────────────────────────────────────────────────────
#  STATIC FILE ROUTES  (explicit, so /api/* is never shadowed)
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def serve_index():
    """Serve index.html at the root."""
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return HTMLResponse(content=index_path.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>index.html not found</h1>", status_code=404)


@app.get("/style.css", include_in_schema=False)
async def serve_css():
    return FileResponse(
        str(FRONTEND_DIR / "style.css"),
        media_type="text/css",
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
    )


@app.get("/app.js", include_in_schema=False)
async def serve_js():
    return FileResponse(
        str(FRONTEND_DIR / "app.js"),
        media_type="application/javascript",
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
    )


@app.get("/favicon.png", include_in_schema=False)
async def serve_favicon_png():
    return FileResponse(str(FRONTEND_DIR / "favicon.png"), media_type="image/png")


@app.get("/favicon.ico", include_in_schema=False)
async def serve_favicon_ico():
    return FileResponse(str(FRONTEND_DIR / "favicon.png"), media_type="image/png")


# ─────────────────────────────────────────────────────────────────────────────
#  API ROUTES
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/api/diagnose")
def diagnose():
    from config import CHROMA_DB_DIR
    local_model_path = os.path.join(WORKSPACE_DIR, "data", "models", "all-MiniLM-L6-v2")
    exists = os.path.exists(local_model_path)
    files = os.listdir(local_model_path) if exists else []

    chroma_exists = os.path.exists(CHROMA_DB_DIR)
    chroma_files = os.listdir(CHROMA_DB_DIR) if chroma_exists else []

    from src.utils.llm_factory import _model_latencies

    return {
        "workspace": WORKSPACE_DIR,
        "local_model_path": local_model_path,
        "model_exists": exists,
        "model_files": files,
        "chroma_db_dir": CHROMA_DB_DIR,
        "chroma_exists": chroma_exists,
        "chroma_files": chroma_files,
        "model_latencies": _model_latencies
    }

@app.get("/api/report")
def get_report(response: Response):
    """Return the latest generated report, diagram, and explanation as JSON."""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    report_path = Path(OUTPUT_DIR) / "research_report.md"
    diagram_path = Path(OUTPUT_DIR) / "diagram.mermaid"
    explanation_path = Path(OUTPUT_DIR) / "diagram_explanation.txt"

    report = report_path.read_text(encoding="utf-8") if report_path.exists() else "# Báo cáo chưa được tạo"
    diagram = diagram_path.read_text(encoding="utf-8") if diagram_path.exists() else ""
    explanation = explanation_path.read_text(encoding="utf-8") if explanation_path.exists() else ""

    return {
        "report": report,
        "diagram": diagram,
        "explanation": explanation
    }


@app.get("/api/download-csv")
def download_csv():
    path = Path(OUTPUT_DIR) / "fpt_consulting_data.csv"
    if path.exists():
        return FileResponse(str(path), media_type="text/csv",
                            filename="fpt_consulting_data.csv")
    return {"error": "CSV not generated yet — run the pipeline first."}


@app.get("/api/download-markdown")
def download_markdown():
    path = Path(OUTPUT_DIR) / "research_report.md"
    if path.exists():
        return FileResponse(
            str(path),
            media_type="text/markdown",
            filename=f"FPT_BaoCao_ChiTiet.md",
            headers={**BYPASS_HEADERS}
        )
    return {"error": "Report not generated yet — run the pipeline first."}


# ── POST request body for /api/run (secure: API keys not exposed in URL/logs) ─
class RunRequest(BaseModel):
    topic: str
    ollama_api_key: str = ""
    openrouter_api_key: str = ""


@app.post("/api/run")
async def run_agents(request: RunRequest):
    """LangGraph multi-agent pipeline via Server-Sent Events.
    Uses POST to prevent API key exposure in URL query parameters and server logs."""
    topic = request.topic
    ollama_api_key = request.ollama_api_key
    openrouter_api_key = request.openrouter_api_key

    # Xác thực đầu vào
    if not topic or not topic.strip():
        return {"error": "Chủ đề không được để trống."}
    if len(topic) > 5000:
        return {"error": "Chủ đề vượt quá giới hạn 5000 ký tự."}

    # Prevent concurrent pipeline runs using asyncio.Lock (thread-safe)
    if _pipeline_lock.locked():
        return {"error": "Hệ thống đang xử lý một yêu cầu khác. Vui lòng đợi hoàn thành trước khi gửi yêu cầu mới."}

    # Acquire lock — will be released in the finally block of the background task
    await _pipeline_lock.acquire()

    # Clear stale model tracking data from previous runs
    from src.utils.llm_factory import clear_actual_models
    clear_actual_models()

    async def event_generator():
        initial_state = {
            "topic": topic,
            "research_data": "",
            "analysis": "",
            "risks": "",
            "recommendations": "",
            "report": "",
            "messages": [],
            "irrelevant": False,
            "csv_data": "",
            "retrieved_context": "",
            "citations": [],
            "query_type": "consulting",
            "language": "vi",
        }

        stream_queue = asyncio.Queue()

        async def run_graph_task():
            try:
                # Clean up old reports and diagrams from previous runs
                for filename in ["research_report.md", "diagram.mermaid", "diagram_explanation.txt", "fpt_consulting_data.csv"]:
                    filepath = Path(OUTPUT_DIR) / filename
                    if filepath.exists():
                        try:
                            filepath.unlink()
                        except Exception:
                            pass

                # Run the graph app
                final_state = await graph_app.ainvoke(
                    initial_state,
                    config={
                        "configurable": {
                            "stream_queue": stream_queue,
                            "ollama_api_key": ollama_api_key,
                            "openrouter_api_key": openrouter_api_key
                        }
                    }
                )
                await stream_queue.put({
                    "type": "graph_complete",
                    "final_state": final_state
                })
            except Exception as exc:
                import traceback
                await stream_queue.put({
                    "type": "error",
                    "error": str(exc) + "\n" + traceback.format_exc()
                })
            finally:
                # Always release the lock and signal completion
                _pipeline_lock.release()
                await stream_queue.put({
                    "type": "done_sentinel"
                })

        # Start execution in the background — lưu reference để tránh GC thu hồi task
        graph_task = asyncio.create_task(run_graph_task())

        start_time = time.time()
        agent_tokens = {
            "guardrail": 0,
            "researcher": 0,
            "analyst": 0,
            "risk_assessor": 0,
            "recommender": 0,
            "reporter": 0
        }
        agent_models = {
            "guardrail": "",
            "researcher": "",
            "analyst": "",
            "risk_assessor": "",
            "recommender": "",
            "reporter": ""
        }
        agent_toks_per_sec = {
            "guardrail": 0.0,
            "researcher": 0.0,
            "analyst": 0.0,
            "risk_assessor": 0.0,
            "recommender": 0.0,
            "reporter": 0.0
        }
        agent_durations = {
            "guardrail": 0.0,
            "researcher": 0.0,
            "analyst": 0.0,
            "risk_assessor": 0.0,
            "recommender": 0.0,
            "reporter": 0.0
        }

        try:
            while True:
                if graph_task.done() and graph_task.exception():
                    # Nếu task bị lỗi, truyền lỗi ra SSE
                    exc = graph_task.exception()
                    yield f"data: {json.dumps({'error': str(exc)}, ensure_ascii=False)}\n\n"
                    break
                try:
                    event = await asyncio.wait_for(stream_queue.get(), timeout=10.0)
                except asyncio.TimeoutError:
                    # Send an SSE keep-alive comment to prevent router/load-balancer timeouts
                    yield ": ping\n\n"
                    continue

                if event.get("type") == "done_sentinel":
                    break
                elif event.get("type") == "error":
                    yield f"data: {json.dumps({'error': event['error']}, ensure_ascii=False)}\n\n"
                    break
                elif event.get("type") == "graph_complete":
                    final_state = event["final_state"]
                    elapsed = time.time() - start_time

                    total_tokens = sum(agent_tokens.values())
                    agents_count = 1 if final_state.get("irrelevant") else (3 if final_state.get("query_type") == "qa" else 6)

                    # Save clean report without metrics suffix as requested
                    final_report = final_state.get("report", "# No report generated").replace("***", "")

                    # Clean internal filenames programmatically
                    final_report = clean_internal_filenames(final_report)
                    try:
    Path(OUTPUT_DIR).mkdir(exist_ok=True)
except Exception:
    pass
                    (Path(OUTPUT_DIR) / "research_report.md").write_text(final_report, encoding="utf-8")

                    # Read diagram and explanation if they exist to pass directly in SSE done event
                    diagram_path = Path(OUTPUT_DIR) / "diagram.mermaid"
                    explanation_path = Path(OUTPUT_DIR) / "diagram_explanation.txt"
                    diagram = diagram_path.read_text(encoding="utf-8") if diagram_path.exists() else ""
                    explanation = explanation_path.read_text(encoding="utf-8") if explanation_path.exists() else ""

                    explanation = clean_internal_filenames(explanation)

                    # Yield completion with stats, report, diagram, explanation and individual token/model/speed counts
                    yield f"data: {json.dumps({'done': True, 'report': final_report, 'diagram': diagram, 'explanation': explanation, 'stats': {'time': f'{elapsed:.3f}s', 'tokens': f'{total_tokens:,}', 'agents': agents_count, 'irrelevant': final_state.get('irrelevant', False), 'agent_tokens': agent_tokens, 'agent_models': agent_models, 'agent_toks_per_sec': agent_toks_per_sec, 'agent_durations': agent_durations}}, ensure_ascii=False)}\n\n"
                elif event.get("type") == "node_end":
                    node_name = event.get("node")
                    tokens = event.get("tokens", 0)
                    if node_name in agent_tokens:
                        agent_tokens[node_name] = tokens
                    if node_name in agent_models and event.get("model"):
                        agent_models[node_name] = event.get("model", "")
                    if node_name in agent_toks_per_sec:
                        agent_toks_per_sec[node_name] = event.get("toks_per_sec", 0.0)
                    if node_name in agent_durations:
                        agent_durations[node_name] = event.get("duration", 0.0)

                    if event.get("content"):
                        event["content"] = clean_internal_filenames(event["content"])
                    if event.get("thinking"):
                        event["thinking"] = clean_internal_filenames(event["thinking"])

                    yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
                else:
                    # Clean internal filenames in any other event that might have text fields
                    if event.get("content"):
                        event["content"] = clean_internal_filenames(event["content"])
                    if event.get("thinking"):
                        event["thinking"] = clean_internal_filenames(event["thinking"])
                    yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

        except Exception as exc:
            import traceback
            yield f"data: {json.dumps({'error': str(exc) + chr(10) + traceback.format_exc()})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={**BYPASS_HEADERS, "Cache-Control": "no-cache, no-transform"},
    )

# ─────────────────────────────────────────────────────────────────────────────

#  ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
