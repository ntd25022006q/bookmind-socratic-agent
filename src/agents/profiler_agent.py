import time
from src.state import ResearchState
from src.utils.llm_factory import create_llm, parse_agent_json, get_actual_model_used
from src.utils.display import print_agent_start, print_agent_complete, print_agent_info
from config import MODEL_RESEARCHER_AGENT

async def profiler_node(state: ResearchState, config=None) -> dict:
    start_time = time.time()
    topic = state.get("topic", "")
    
    stream_queue = config.get("configurable", {}).get("stream_queue") if config else None
    if stream_queue:
        await stream_queue.put({
            "type": "node_start",
            "node": "researcher"  # Maps to node-researcher in UI
        })
        
    print_agent_start("Researcher Agent", "Phân tích hồ sơ độc giả và nhu cầu tự học chủ động")
    llm = create_llm(MODEL_RESEARCHER_AGENT, config=config, streaming=True)
    
    call_config = {}
    if stream_queue:
        from src.utils.llm_factory import QueueCallbackHandler
        call_config["callbacks"] = [QueueCallbackHandler(stream_queue, "researcher")]
        
    user_profile = state.get("user_profile", "")
    prompt = f"""Bạn là Profiler Agent của VNU BookMind Socratic. Hãy phân tích sở thích đọc sách, gu học thuật và phong cách tư duy của độc giả từ truy vấn: "{topic}".
    Đặc biệt, độc giả đã cung cấp thông tin hồ sơ của họ như sau: "{user_profile}".
    Nhiệm vụ của bạn là kết hợp thông tin hồ sơ này và chủ đề truy vấn để lập nên một báo cáo Hồ sơ Độc giả thông minh và đầy đủ nhất.
    Chú ý: Tuyệt đối giữ đúng các thông tin thật (Họ tên, MSSV, Ngành học) mà độc giả đã cung cấp trong hồ sơ, không được tự bịa ra thông tin mới về các trường này.
    
    Hãy trả về dưới dạng:
    === QUÁ TRÌNH TƯ DUY ===
    [Phân tích nhu cầu tư duy, phong cách đọc dựa trên hồ sơ cung cấp và truy vấn]
    === CONSOLE MESSAGE ===
    Đã lập hồ sơ độc giả thông minh từ thông tin đăng ký.
    === BÁO CÁO CHI TIẾT ===
    HỒ SƠ ĐỘC GIẢ:
    - Họ và tên độc giả: [Họ tên từ hồ sơ]
    - Mã số sinh viên: [MSSV từ hồ sơ]
    - Ngành học & Khóa: [Ngành học từ hồ sơ]
    - Phong cách tư duy: [Phong cách tư duy từ hồ sơ hoặc phân tích]
    - Lĩnh vực đặc biệt quan tâm: [Lĩnh vực quan tâm từ hồ sơ + phân tích từ chủ đề "{topic}"]
    """
    
    res = await llm.ainvoke(prompt, config=call_config)
    parsed = parse_agent_json(res.content, "detailed_report")
    
    tokens = len(res.content) // 4
    duration = time.time() - start_time
    print_agent_complete("Researcher Agent", duration, tokens)
    actual_model = get_actual_model_used("profiler", MODEL_RESEARCHER_AGENT)
    toks_per_sec = round(tokens / duration, 1) if duration > 0 else 0
    
    if stream_queue:
        await stream_queue.put({
            "type": "node_end",
            "node": "researcher",
            "content": parsed["console_message"],
            "thinking": parsed["thinking"],
            "tokens": tokens,
            "duration": duration,
            "model": actual_model,
            "toks_per_sec": toks_per_sec
        })
        
    return {
        "user_profile": parsed["detailed_report"],
        "messages": [res],
        "research_data": parsed["console_message"]
    }
