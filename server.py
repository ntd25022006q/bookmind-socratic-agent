"""
VNU BookMind Socratic — Agentic Research & Detailed Report Dashboard
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

# ── Concurrent pipeline protection (session-specific via asyncio.Locks) ───────
_session_locks = {}
_session_tasks = {}
_session_history = {}  # session_id -> list of events
_session_queues = {}   # session_id -> set of asyncio.Queue instances
_session_queries = {}  # session_id -> (topic, user_profile, socratic_answers)
_session_start_times = {}  # session_id -> start timestamp

class SessionQueueAdapter(asyncio.Queue):
    def __init__(self, session_id: str):
        super().__init__()
        self.session_id = session_id

    async def put(self, item):
        await publish_event(self.session_id, item)

async def publish_event(session_id: str, event: dict):
    if session_id not in _session_history:
        _session_history[session_id] = []
    _session_history[session_id].append(event)
    
    queues = _session_queues.get(session_id, set())
    for q in list(queues):
        try:
            await q.put(event)
        except Exception:
            pass

def get_session_lock(session_id: str) -> asyncio.Lock:
    sid = session_id if session_id else "default"
    if sid not in _session_locks:
        _session_locks[sid] = asyncio.Lock()
    return _session_locks[sid]

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
    title="VNU BookMind Socratic Agentic Research & Detailed Report Dashboard",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# ── Serve frontend assets with read-only/serverless compatibility ────
try:
    FRONTEND_DIR = Path(WORKSPACE_DIR) / "frontend"
    # Canonical frontend directory is always 'frontend/'
    # No wildcard scan needed — all builds place static files in 'frontend/'
                
    # Mount static files only if directory exists
    if FRONTEND_DIR.exists():
        app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIR)), name="assets")

        lib_dir = FRONTEND_DIR / "lib"
        if lib_dir.exists():
            app.mount("/lib", StaticFiles(directory=str(lib_dir)), name="lib")

        fonts_dir = FRONTEND_DIR / "webfonts"
        if fonts_dir.exists():
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


@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "VNU BookMind Socratic API is running."}


@app.get("/api/report")
def get_report(response: Response, session_id: str = ""):
    """Return the generated report, diagram, and explanation as JSON for a specific session."""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    suffix = f"_{session_id}" if session_id else ""
    report_path = Path(OUTPUT_DIR) / f"research_report{suffix}.md"
    diagram_path = Path(OUTPUT_DIR) / f"diagram{suffix}.mermaid"
    explanation_path = Path(OUTPUT_DIR) / f"diagram_explanation{suffix}.txt"

    report = report_path.read_text(encoding="utf-8") if report_path.exists() else "# Báo cáo chưa được tạo"
    diagram = diagram_path.read_text(encoding="utf-8") if diagram_path.exists() else ""
    explanation = explanation_path.read_text(encoding="utf-8") if explanation_path.exists() else ""

    return {
        "report": report,
        "diagram": diagram,
        "explanation": explanation
    }


@app.get("/api/download-csv")
def download_csv(session_id: str = ""):
    suffix = f"_{session_id}" if session_id else ""
    path = Path(OUTPUT_DIR) / f"vnu_bookmind_socratic_data{suffix}.csv"

    if path.exists():
        return FileResponse(str(path), media_type="text/csv",
                            filename=f"vnu_bookmind_socratic_data{suffix}.csv")
    return {"error": "CSV not generated yet — run the pipeline first."}


@app.get("/api/download-markdown")
def download_markdown(session_id: str = ""):
    suffix = f"_{session_id}" if session_id else ""
    path = Path(OUTPUT_DIR) / f"research_report{suffix}.md"

    if path.exists():
        return FileResponse(
            str(path),
            media_type="text/markdown",
            filename=f"VNU_BookMind_Socratic_BaoCao_ChiTiet{suffix}.md",
            headers={**BYPASS_HEADERS}
        )
    return {"error": "Report not generated yet — run the pipeline first."}


# ── Request model ─────────────────────────────────────────────────────────────
class RunRequest(BaseModel):
    topic: str
    user_profile: str = ""
    ollama_api_key: str = ""
    openrouter_api_key: str = ""
    socratic_answers: str = ""
    analysis: str = ""
    risks: str = ""
    research_data: str = ""
    retrieved_context: str = ""
    citations: list = []
    session_id: str = ""


@app.post("/api/stop")
async def stop_pipeline(session_id: str = ""):
    """Cancel a running pipeline for the given session_id."""
    sid = session_id if session_id else "default"
    task = _session_tasks.get(sid)
    if task and not task.done():
        task.cancel()
        # Also release lock so new requests can proceed immediately
        lock = _session_locks.get(sid)
        if lock and lock.locked():
            try:
                lock.release()
            except Exception:
                pass
        return {"stopped": True, "session_id": sid}
    return {"stopped": False, "message": "No active task for this session."}


@app.post("/api/run")
async def run_agents(request: RunRequest):
    """LangGraph multi-agent pipeline via Server-Sent Events.
    Uses POST to prevent API key exposure in URL query parameters and server logs."""
    topic = request.topic
    user_profile = request.user_profile
    ollama_api_key = request.ollama_api_key
    openrouter_api_key = request.openrouter_api_key
    socratic_answers = request.socratic_answers
    analysis = request.analysis
    risks = request.risks
    research_data = request.research_data
    retrieved_context = request.retrieved_context
    citations = request.citations
    session_id = request.session_id or "default"

    # Xác thực đầu vào
    if not topic or not topic.strip():
        return {"error": "Chủ đề không được để trống."}
    if len(topic) > 5000:
        return {"error": "Chủ đề vượt quá giới hạn 5000 ký tự."}

    global _session_tasks, _session_queries, _session_history, _session_start_times, _session_queues

    is_running = session_id in _session_tasks and not _session_tasks[session_id].done()
    query_key = (topic, user_profile, socratic_answers)
    is_same_query = _session_queries.get(session_id) == query_key

    if is_running and is_same_query:
        print(f"[Server] Session {session_id} is already running the same query. Connecting client to existing stream.")
    else:
        if is_running:
            print(f"[Server] Cancelling active task for session {session_id} because query changed.")
            _session_tasks[session_id].cancel()
            try:
                await _session_tasks[session_id]
            except Exception:
                pass
            
            # Force release the lock for this session
            lock = get_session_lock(session_id)
            if lock.locked():
                try:
                    lock.release()
                except Exception:
                    pass

        # Start execution in the background
        _session_queries[session_id] = query_key
        _session_history[session_id] = []
        _session_start_times[session_id] = time.time()

        # Clear stale model tracking data from previous runs
        from src.utils.llm_factory import clear_actual_models
        clear_actual_models()

        lock = get_session_lock(session_id)
        lock_acquired = False
        for _attempt in range(10):
            if not lock.locked():
                await lock.acquire()
                lock_acquired = True
                break
            await asyncio.sleep(0.5)
        if not lock_acquired:
            return {"error": "Hệ thống đang xử lý một yêu cầu khác trên cuộc trò chuyện này. Vui lòng đợi hoàn thành trước khi gửi yêu cầu mới."}

        initial_state = {
            "topic": topic,
            "user_profile": user_profile,
            "research_data": research_data,
            "analysis": analysis,
            "risks": risks,
            "recommendations": "",
            "report": "",
            "messages": [],
            "irrelevant": False,
            "csv_data": "",
            "retrieved_context": retrieved_context,
            "citations": citations,
            "query_type": "consulting",
            "language": "vi",
            "socratic_answers": socratic_answers,
        }

        async def run_graph_task():
            try:
                # Clean up old reports and diagrams for this specific session
                suffix = f"_{session_id}" if session_id else ""
                for filename in [f"research_report{suffix}.md", f"diagram{suffix}.mermaid", f"diagram_explanation{suffix}.txt", f"vnu_bookmind_socratic_data{suffix}.csv"]:
                    filepath = Path(OUTPUT_DIR) / filename
                    if filepath.exists():
                        try:
                            filepath.unlink()
                        except Exception:
                            pass

                # Run the graph app using SessionQueueAdapter
                adapter = SessionQueueAdapter(session_id)
                final_state = await graph_app.ainvoke(
                    initial_state,
                    config={
                        "configurable": {
                            "session_id": session_id,
                            "stream_queue": adapter,
                            "ollama_api_key": ollama_api_key,
                            "openrouter_api_key": openrouter_api_key
                        }
                    }
                )
                await publish_event(session_id, {
                    "type": "graph_complete",
                    "final_state": final_state
                })
            except Exception as exc:
                import traceback
                await publish_event(session_id, {
                    "type": "error",
                    "error": str(exc) + "\n" + traceback.format_exc()
                })
            finally:
                # Always release the session lock and signal completion
                if lock.locked():
                    try:
                        lock.release()
                    except Exception:
                        pass
                await publish_event(session_id, {
                    "type": "done_sentinel"
                })

        _session_tasks[session_id] = asyncio.create_task(run_graph_task())

    async def event_generator():
        client_queue = asyncio.Queue()
        if session_id not in _session_queues:
            _session_queues[session_id] = set()
        _session_queues[session_id].add(client_queue)

        start_time = _session_start_times.get(session_id, time.time())
        agent_tokens = {k: 0 for k in ["guardrail", "researcher", "analyst", "risk_assessor", "recommender", "reporter"]}
        agent_models = {k: "" for k in ["guardrail", "researcher", "analyst", "risk_assessor", "recommender", "reporter"]}
        agent_toks_per_sec = {k: 0.0 for k in ["guardrail", "researcher", "analyst", "risk_assessor", "recommender", "reporter"]}
        agent_durations = {k: 0.0 for k in ["guardrail", "researcher", "analyst", "risk_assessor", "recommender", "reporter"]}

        def process_event(event):
            nonlocal start_time
            if event.get("type") == "node_end":
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
                return f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

            elif event.get("type") == "graph_complete":
                final_state = event["final_state"]
                elapsed = time.time() - start_time
                if "elapsed_time" in event:
                    elapsed = event["elapsed_time"]
                else:
                    event["elapsed_time"] = elapsed

                if not final_state.get("socratic_answers") and not final_state.get("irrelevant", False):
                    return f"data: {json.dumps({'socratic_pause': True, 'socratic_questions': final_state.get('risks', ''), 'state_snapshot': {'topic': final_state.get('topic', ''), 'user_profile': final_state.get('user_profile', ''), 'analysis': final_state.get('analysis', ''), 'risks': final_state.get('risks', ''), 'research_data': final_state.get('research_data', ''), 'retrieved_context': final_state.get('retrieved_context', ''), 'citations': final_state.get('citations', [])}}, ensure_ascii=False)}\n\n"

                total_tokens = sum(agent_tokens.values())
                agents_count = 1 if final_state.get("irrelevant") else 6

                final_report = final_state.get("report", "# No report generated")
                final_report = clean_internal_filenames(final_report)
                try:
                    Path(OUTPUT_DIR).mkdir(exist_ok=True)
                except Exception:
                    pass
                
                suffix = f"_{session_id}" if session_id else ""
                (Path(OUTPUT_DIR) / f"research_report{suffix}.md").write_text(final_report, encoding="utf-8")

                diagram_path = Path(OUTPUT_DIR) / f"diagram{suffix}.mermaid"
                explanation_path = Path(OUTPUT_DIR) / f"diagram_explanation{suffix}.txt"
                
                diagram = diagram_path.read_text(encoding="utf-8") if diagram_path.exists() else ""
                explanation = explanation_path.read_text(encoding="utf-8") if explanation_path.exists() else ""
                explanation = clean_internal_filenames(explanation)

                return f"data: {json.dumps({'done': True, 'report': final_report, 'diagram': diagram, 'explanation': explanation, 'stats': {'time': f'{elapsed:.3f}s', 'tokens': f'{total_tokens:,}', 'agents': agents_count, 'irrelevant': final_state.get('irrelevant', False), 'agent_tokens': agent_tokens, 'agent_models': agent_models, 'agent_toks_per_sec': agent_toks_per_sec, 'agent_durations': agent_durations}}, ensure_ascii=False)}\n\n"

            else:
                if event.get("content"):
                    event["content"] = clean_internal_filenames(event["content"])
                if event.get("thinking"):
                    event["thinking"] = clean_internal_filenames(event["thinking"])
                return f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

        try:
            history = list(_session_history.get(session_id, []))
            for ev in history:
                yield process_event(ev)
                if ev.get("type") in ["graph_complete", "error", "done_sentinel"]:
                    return

            while True:
                try:
                    event = await asyncio.wait_for(client_queue.get(), timeout=15.0)
                except asyncio.TimeoutError:
                    yield ": ping\n\n"
                    continue

                if event.get("type") == "done_sentinel":
                    break
                elif event.get("type") == "error":
                    yield f"data: {json.dumps({'error': event['error']}, ensure_ascii=False)}\n\n"
                    break

                yield process_event(event)
                if event.get("type") == "graph_complete":
                    break

        except Exception as exc:
            import traceback
            yield f"data: {json.dumps({'error': str(exc) + chr(10) + traceback.format_exc()})}\n\n"
        finally:
            _session_queues[session_id].discard(client_queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={**BYPASS_HEADERS, "Cache-Control": "no-cache, no-transform"},
    )

if __name__ == "__main__":
    import uvicorn
    # VNU BookMind Socratic API Server Initialized
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
