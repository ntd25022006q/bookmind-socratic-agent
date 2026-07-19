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
            "node": "profiler"  # Maps to node-profiler in UI
        })
        
    print_agent_start("Profiler Agent", "Phân tích hồ sơ độc giả và nhu cầu tự học chủ động")
    llm = create_llm(MODEL_RESEARCHER_AGENT, config=config, streaming=True)
    
    call_config = {}
    if stream_queue:
        from src.utils.llm_factory import QueueCallbackHandler
        call_config["callbacks"] = [QueueCallbackHandler(stream_queue, "profiler")]
        
    prompt = f"""Bạn là Profiler Agent của VNU BookMind Socratic. Hãy phân tích sở thích đọc sách, gu học thuật và lĩnh vực quan tâm giả định của độc giả từ truy vấn:
    "{topic}"
    
    Hãy trả về dưới dạng:
    === QUÁ TRÌNH TƯ DUY ===
    [Phân tích nhu cầu tư duy và gu học thuật]
    === CONSOLE MESSAGE ===
    Đã lập hồ sơ độc giả thông minh.
    === BÁO CÁO CHI TIẾT ===
    HỒ SƠ ĐỘC GIẢ:
    - Chủ đề quan tâm: {topic}
    - Phong cách tư duy: [Sáng tạo/Phân tích/Thực tiễn]
    - Nhu cầu đọc sâu: [Học thuật/Kỹ năng/Khai phóng]
    """
    
    res = await llm.ainvoke(prompt, config=call_config)
    parsed = parse_agent_json(res.content, "detailed_report")
    
    tokens = len(res.content) // 4
    duration = time.time() - start_time
    print_agent_complete("Profiler Agent", duration, tokens)
    actual_model = get_actual_model_used("profiler", MODEL_RESEARCHER_AGENT)
    toks_per_sec = round(tokens / duration, 1) if duration > 0 else 0
    
    if stream_queue:
        await stream_queue.put({
            "type": "node_end",
            "node": "profiler",
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
