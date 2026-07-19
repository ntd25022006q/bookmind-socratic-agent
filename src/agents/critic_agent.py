import time
from src.state import ResearchState
from src.utils.llm_factory import create_llm, parse_agent_json, get_actual_model_used
from src.utils.display import print_agent_start, print_agent_complete, print_agent_info
from config import MODEL_ANALYST_AGENT

async def critic_node(state: ResearchState, config=None) -> dict:
    start_time = time.time()
    topic = state.get("topic", "")
    profile = state.get("user_profile", "")
    rec = state.get("analysis", "")
    qa = state.get("risks", "")
    
    stream_queue = config.get("configurable", {}).get("stream_queue") if config else None
    if stream_queue:
        await stream_queue.put({
            "type": "node_start",
            "node": "critic"  # Maps to node-critic in UI
        })
        
    print_agent_start("Critic Agent", "Phản biện tư duy và phát hiện điểm mù nhận thức độc giả")
    llm = create_llm(MODEL_ANALYST_AGENT, config=config, streaming=True)
    
    call_config = {}
    if stream_queue:
        from src.utils.llm_factory import QueueCallbackHandler
        call_config["callbacks"] = [QueueCallbackHandler(stream_queue, "critic")]
        
    prompt = f"""Bạn là Critic Agent (Tác nhân Phản biện) của VNU BookMind Socratic. Hãy phân tích các đề xuất sách và câu hỏi đối thoại hiện tại.
    Chủ đề: {topic}
    Hồ sơ độc giả: {profile}
    Đề xuất sách: {rec}
    Câu hỏi Socratic: {qa}
    
    Nhiệm vụ:
    - Phát hiện các điểm mù nhận thức (cognitive blind spots) hoặc thiên kiến xác nhận độc giả có thể gặp phải.
    - Đưa ra các checkpoint tư duy phản biện để độc giả tự vấn bản thân khi đọc các tài liệu này.
    
    Hãy trả về dưới dạng:
    === QUÁ TRÌNH TƯ DUY ===
    [Phân tích phản biện các điểm mù nhận thức]
    === CONSOLE MESSAGE ===
    Đã kết xuất phân tích điểm mù nhận thức và checkpoint phản biện.
    === BÁO CÁO CHI TIẾT ===
    ### PHẢN BIỆN TƯ DUY & ĐIỂM MÙ NHẬN THỨC:
    [Nêu rõ các thiên kiến nhận thức có thể gặp và 3 checkpoint tự vấn]
    """
    
    res = await llm.ainvoke(prompt, config=call_config)
    parsed = parse_agent_json(res.content, "detailed_report")
    
    tokens = len(res.content) // 4
    duration = time.time() - start_time
    print_agent_complete("Critic Agent", duration, tokens)
    actual_model = get_actual_model_used("critic", MODEL_ANALYST_AGENT)
    toks_per_sec = round(tokens / duration, 1) if duration > 0 else 0
    
    if stream_queue:
        await stream_queue.put({
            "type": "node_end",
            "node": "critic",
            "content": parsed["console_message"],
            "thinking": parsed["thinking"],
            "tokens": tokens,
            "duration": duration,
            "model": actual_model,
            "toks_per_sec": toks_per_sec
        })
        
    return {
        "risks": qa + "\n\n" + parsed["detailed_report"],
        "messages": [res]
    }
