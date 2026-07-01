import os
import time
import json
import re
import threading
import urllib.request
import asyncio
from langchain_openai import ChatOpenAI
from langchain_core.callbacks import AsyncCallbackHandler
from config import OLLAMA_API_KEY, OLLAMA_BASE_URL

# Thread-local or simple dict to track the actual model used per node during a run
_actual_model_used: dict = {}

class QueueCallbackHandler(AsyncCallbackHandler):
    """Callback handler that pushes LLM tokens onto an asyncio.Queue in real-time
    and records the actual model name when generation starts."""
    def __init__(self, queue: asyncio.Queue, node_name: str):
        self.queue = queue
        self.node_name = node_name

    async def on_llm_start(self, serialized, prompts, **kwargs) -> None:
        """Record the actual model name at generation start."""
        try:
            model_name = serialized.get("kwargs", {}).get("model_name") or serialized.get("name", "unknown")
            _actual_model_used[self.node_name] = model_name
        except Exception:
            pass

    async def on_llm_new_token(self, token: str, **kwargs) -> None:
        await self.queue.put({
            "type": "token",
            "node": self.node_name,
            "token": token
        })
# Dynamic model health & latency cache
_model_latencies: dict = {}
_latency_checker_started = False
_latency_lock = threading.Lock()

def check_model_latencies_sync():
    """Verify availability and latency of Ollama models to build an optimized fallback list."""
    global _model_latencies
    models_to_check = ["gemma3:12b", "ministral-3:8b", "qwen3-coder-next", "gemma3:27b"]
    new_latencies = {}
    
    for model in models_to_check:
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": "ping"}],
            "max_tokens": 1
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{OLLAMA_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {OLLAMA_API_KEY}",
                "Content-Type": "application/json"
            },
            data=data,
            method="POST"
        )
        
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=3.0) as response:
                response.read()
                latency = time.time() - t0
                new_latencies[model] = latency
        except Exception:
            new_latencies[model] = 999.0  # Offline / Unhealthy penalty
            
    with _latency_lock:
        _model_latencies = new_latencies

def start_latency_checker():
    """Start background daemon thread to periodically update model latencies."""
    global _latency_checker_started
    with _latency_lock:
        if _latency_checker_started:
            return
        _latency_checker_started = True
        
    def worker():
        # Quick initial check
        try:
            check_model_latencies_sync()
        except Exception:
            pass
        while True:
            time.sleep(300)  # Re-check every 5 minutes
            try:
                check_model_latencies_sync()
            except Exception:
                pass
                
    t = threading.Thread(target=worker, daemon=True)
    t.start()

def clear_actual_models():
    """Clear the model tracking data from previous runs."""
    _actual_model_used.clear()


def create_llm(model: str, temperature: float = 0.2, max_tokens: int = 2000, streaming: bool = False, config = None):
    """Create a ChatOpenAI wrapper instance pointing to the Ollama Cloud API,
    equipped with fallbacks from the best free Ollama Cloud models sorted by latency.
    """
    # Start latency checker in background
    try:
        start_latency_checker()
    except Exception:
        pass

    # Extract custom keys from config if provided
    custom_ollama_key = ""
    custom_openrouter_key = ""
    if config:
        if isinstance(config, dict):
            configurable = config.get("configurable", {})
        else:
            configurable = getattr(config, "configurable", {})
        if isinstance(configurable, dict):
            custom_ollama_key = configurable.get("ollama_api_key", "")
            custom_openrouter_key = configurable.get("openrouter_api_key", "")

    active_ollama_key = custom_ollama_key or OLLAMA_API_KEY
    active_openrouter_key = custom_openrouter_key or os.environ.get("OPENROUTER_API_KEY", "")

    latencies = _model_latencies
    if not latencies:
        # Default order if cache is not populated yet
        sorted_models = ["gemma3:12b", "ministral-3:8b", "qwen3-coder-next", "gemma3:27b"]
    else:
        # Sort based on latency (lowest/healthiest first)
        sorted_models = sorted(
            ["gemma3:12b", "ministral-3:8b", "qwen3-coder-next", "gemma3:27b"],
            key=lambda m: latencies.get(m, 1.0)
        )

    # Determine primary model and fallback candidates
    primary_latency = latencies.get(model, 1.0)
    
    # If the requested primary model is healthy (latency < 10s), try it first
    if primary_latency < 10.0:
        primary_model = model
        fallback_candidates = [m for m in sorted_models if m != model]
    else:
        # If primary model is offline/unhealthy, bypass it and try the healthiest model first
        primary_model = sorted_models[0]
        fallback_candidates = [m for m in sorted_models if m != primary_model] + [model]

    primary_llm = ChatOpenAI(
        model=primary_model,
        api_key=active_ollama_key,
        base_url=OLLAMA_BASE_URL,
        temperature=temperature,
        timeout=120,         # 120s — generous timeout for LLM streaming
        max_retries=0,       # Fail over instantly
        max_tokens=max_tokens,
        streaming=streaming
    )
    
    fallbacks = []
    for fallback_model in fallback_candidates:
        # Skip models that are known to be down (latency >= 999s) to avoid unnecessary timeouts
        if latencies.get(fallback_model, 1.0) >= 999.0:
            continue
        fallbacks.append(
            ChatOpenAI(
                model=fallback_model,
                api_key=active_ollama_key,
                base_url=OLLAMA_BASE_URL,
                temperature=temperature,
                timeout=90,          # 90s timeout for fallbacks
                max_retries=0,
                max_tokens=max_tokens,
                streaming=streaming
            )
        )
        
    # OpenRouter fallback integration to thoroughly resolve Ollama weekly limits (429)
    if active_openrouter_key:
        openrouter_base_url = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        for or_model in ["google/gemini-2.5-flash:free", "meta-llama/llama-3.3-70b-instruct:free", "deepseek/deepseek-chat:free"]:
            fallbacks.append(
                ChatOpenAI(
                    model=or_model,
                    api_key=active_openrouter_key,
                    base_url=openrouter_base_url,
                    temperature=temperature,
                    timeout=120,         # 120s — generous timeout for OpenRouter
                    max_retries=0,
                    max_tokens=max_tokens,
                    streaming=streaming,
                    default_headers={
                        "HTTP-Referer": "https://github.com/ntd25022006q/fpt-multi-agent-system",
                        "X-Title": "FPT Multi-Agent System"
                    }
                )
            )
        
    llm = primary_llm.with_fallbacks(fallbacks=fallbacks)
    return llm

def get_actual_model_used(node_name: str, default_model: str) -> str:
    """Return the actual model name recorded for a node (set by QueueCallbackHandler)."""
    return _actual_model_used.get(node_name, default_model)


def parse_agent_json(content: str, fallback_key: str) -> dict:
    """Parse output from agents using a robust delimiter-based check, extracting thinking logs,
    console messages, detailed reports, and diagrams."""
    content = content.strip()
    
    think_markers = ["=== THINKING ===", "=== QUÁ TRÌNH TƯ DUY ===", "=== SUY NGHĨ ===", "=== TƯ DUY ==="]
    console_markers = ["=== CONSOLE MESSAGE ===", "=== THÔNG BÁO CONSOLE ===", "=== NHẬT KÝ CONSOLE ===", "=== TÓM TẮT CONSOLE ===", "=== NHẬT KÝ ===", "=== TÓM TẮT ==="]
    report_markers = ["=== DETAILED REPORT ===", "=== BÁO CÁO CHI TIẾT ===", "=== BÁO CÁO CỤ THỂ ===", "=== BÁO CÁO ==="]
    mermaid_markers = ["=== MERMAID DIAGRAM ===", "=== SƠ ĐỒ MERMAID ===", "=== BIỂU ĐỒ MERMAID ==="]
    explanation_markers = ["=== DIAGRAM EXPLANATION ===", "=== GIẢI THÍCH CHI TIẾT SƠ ĐỒ ===", "=== GIẢI THÍCH SƠ ĐỒ ===", "=== GIẢI THÍCH ==="]
    
    sections = {
        "thinking": "",
        "console_message": "",
        "detailed_report": "",
        "mermaid_diagram": "",
        "diagram_explanation": ""
    }
    
    # Find all matches of markers in content
    matches = []
    
    markers_map = [
        ("thinking", think_markers),
        ("console_message", console_markers),
        ("detailed_report", report_markers),
        ("mermaid_diagram", mermaid_markers),
        ("diagram_explanation", explanation_markers)
    ]
    
    content_lower = content.lower()
    for key, markers in markers_map:
        for marker in markers:
            idx = content_lower.find(marker.lower())
            if idx != -1:
                matches.append((idx, idx + len(marker), key))
                
    # Sort matches by start index (ascending) and length (descending) to prioritize longer markers
    matches.sort(key=lambda x: (x[0], -(x[1] - x[0])))
    
    # Filter out overlapping matches
    filtered_matches = []
    for m in matches:
        start, end, key = m
        overlap = False
        for accepted in filtered_matches:
            astart, aend, _ = accepted
            if not (end <= astart or start >= aend):
                overlap = True
                break
        if not overlap:
            filtered_matches.append(m)
            
    matches = filtered_matches
    matches.sort(key=lambda x: x[0])

    
    result = None
    
    if matches:
        # Step 1: Pre-process console_message block to see if report is inside it
        for i in range(len(matches)):
            start_idx, end_idx, key = matches[i]
            next_start = matches[i+1][0] if i + 1 < len(matches) else len(content)
            block_text = content[end_idx:next_start].strip()
            
            if key == "console_message" and i == len(matches) - 1:
                split_match = re.search(r"\n\s*(?:#+|\d+\.|\*\*)\s+", block_text)
                if split_match:
                    split_idx = split_match.start()
                    real_console = block_text[:split_idx].strip()
                    real_report = block_text[split_idx:].strip()
                    sections["console_message"] = real_console
                    sections["detailed_report"] = real_report
                else:
                    if sections[key]:
                        sections[key] += "\n\n" + block_text
                    else:
                        sections[key] = block_text
            else:
                if sections[key]:
                    sections[key] += "\n\n" + block_text
                else:
                    sections[key] = block_text
                    
        detailed_report = sections["detailed_report"]
        console_message = sections["console_message"]
        thinking = sections["thinking"]
        mermaid_diagram = sections["mermaid_diagram"]
        diagram_explanation = sections["diagram_explanation"]
        
        report_data = detailed_report
        
        if not report_data:
            # Reconstruct content by omitting thinking and console blocks
            sorted_matches = sorted(matches, key=lambda x: x[0])
            reconstructed_parts = []
            last_idx = 0
            for i in range(len(sorted_matches)):
                start_idx, end_idx, key = sorted_matches[i]
                next_start = sorted_matches[i+1][0] if i + 1 < len(sorted_matches) else len(content)
                
                if last_idx < start_idx:
                    unmarked_text = content[last_idx:start_idx].strip()
                    if unmarked_text:
                        reconstructed_parts.append(unmarked_text)
                
                if key not in ["thinking", "console_message"]:
                    block_text = content[start_idx:next_start].strip()
                    if block_text:
                        reconstructed_parts.append(block_text)
                last_idx = next_start
                
            if last_idx < len(content):
                rem = content[last_idx:].strip()
                if rem:
                    reconstructed_parts.append(rem)
            
            if reconstructed_parts:
                report_data = "\n\n".join(reconstructed_parts)
            else:
                report_data = content

        if mermaid_diagram.startswith("```mermaid"):
            mermaid_diagram = mermaid_diagram[10:]
        elif mermaid_diagram.startswith("```"):
            mermaid_diagram = mermaid_diagram[3:]
        if mermaid_diagram.endswith("```"):
            mermaid_diagram = mermaid_diagram[:-3]
        mermaid_diagram = mermaid_diagram.strip()

        result = {
            fallback_key: report_data,
            "console_message": console_message if console_message else f"Tôi đã hoàn thành việc xử lý thông tin cho phần {fallback_key}.",
            "thinking": thinking,
            "mermaid_diagram": mermaid_diagram,
            "diagram_explanation": diagram_explanation
        }
    
    if not result:
        # JSON-based parsing (fallback)
        json_content = content
        if json_content.startswith("```json"):
            json_content = json_content[7:]
        elif json_content.startswith("```"):
            json_content = json_content[3:]
        if json_content.endswith("```"):
            json_content = json_content[:-3]
        json_content = json_content.strip()
        
        try:
            start_idx = json_content.find('{')
            end_idx = json_content.rfind('}')
            if start_idx != -1 and end_idx != -1:
                json_str = json_content[start_idx:end_idx+1]
            else:
                json_str = json_content
                
            data = json.loads(json_str)
            if fallback_key in data and "console_message" in data:
                result = {
                    fallback_key: data[fallback_key],
                    "console_message": data["console_message"],
                    "thinking": data.get("thinking", ""),
                    "mermaid_diagram": data.get("mermaid_diagram", ""),
                    "diagram_explanation": data.get("diagram_explanation", "")
                }
        except Exception:
            try:
                escaped = re.sub(r'(?<!\\)\n', r'\\n', json_content)
                start_idx = escaped.find('{')
                end_idx = escaped.rfind('}')
                if start_idx != -1 and end_idx != -1:
                    data = json.loads(escaped[start_idx:end_idx+1])
                    if fallback_key in data and "console_message" in data:
                        result = {
                            fallback_key: data[fallback_key],
                            "console_message": data["console_message"],
                            "thinking": data.get("thinking", ""),
                            "mermaid_diagram": data.get("mermaid_diagram", ""),
                            "diagram_explanation": data.get("diagram_explanation", "")
                        }
            except Exception:
                pass
                
    if not result:
        # Raw Text fallback
        result = {
            fallback_key: content,
            "console_message": f"Tôi đã hoàn thành việc xử lý thông tin cho phần {fallback_key}.",
            "thinking": "",
            "mermaid_diagram": "",
            "diagram_explanation": ""
        }
        
    # Step 2: Post-process all text values to strip header markers robustly
    clean_pattern = r"(?im)^\s*={0,}\s*\*?\*?\s*(thinking|console\s*message|detailed\s*report|mermaid\s*diagram|diagram\s*explanation|quá\s*trình\s*tư\s*duy|suy\s*nghĩ|tư\s*duy|thông\s*báo\s*console|nhật\s*ký\s*console|tóm\s*tắt\s*console|nhật\s*ký|tóm\s*tắt|báo\s*cáo\s*chi\s*tiết|báo\s*cáo\s*cụ\s*thể|báo\s*cáo|sơ\s*đồ\s*mermaid|biểu\s*đồ\s*mermaid|giải\s*thích\s*chi\s*tiết\s*sơ\s*đồ|giải\s*thích\s*sơ\s*đồ|giải\s*thích)\s*\*?\*?\s*={0,}\s*$"
    
    for k in [fallback_key, "console_message", "thinking", "diagram_explanation"]:
        val = result.get(k, "")
        if isinstance(val, str) and val:
            val = re.sub(clean_pattern, "", val)
            val = re.sub(r'={2,}', '', val)
            val = val.replace("***", "")
            result[k] = val.strip()
            
    return result
