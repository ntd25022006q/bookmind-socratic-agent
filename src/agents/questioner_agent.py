import time
from src.state import ResearchState
from src.utils.llm_factory import create_llm, parse_agent_json, get_actual_model_used
from src.utils.display import print_agent_start, print_agent_complete, print_agent_info
from config import MODEL_RESEARCHER_AGENT

async def questioner_node(state: ResearchState, config=None) -> dict:
    start_time = time.time()
    topic = state.get("topic", "")
    books = state.get("analysis", "")
    profile = state.get("user_profile", "")
    
    stream_queue = config.get("configurable", {}).get("stream_queue") if config else None
    
    # Phase 2 resume bypass
    if state.get("socratic_answers"):
        if stream_queue:
            await stream_queue.put({
                "type": "node_start",
                "node": "risk_assessor"
            })
            await stream_queue.put({
                "type": "node_end",
                "node": "risk_assessor",
                "content": state.get("csv_data", ""),
                "thinking": "",
                "tokens": 0,
                "duration": 0.0,
                "model": "bypass",
                "toks_per_sec": 0.0
            })
        return {
            "risks": state.get("risks", ""),
            "csv_data": state.get("csv_data", "")
        }
        
    if stream_queue:
        await stream_queue.put({
            "type": "node_start",
            "node": "risk_assessor"  # Maps to node-risk_assessor in UI
        })
        
    print_agent_start("Risk Assessor Agent", "Đặt câu hỏi Socratic kích thích tư duy phản biện")
    llm = create_llm(MODEL_RESEARCHER_AGENT, config=config, streaming=True)
    
    call_config = {}
    if stream_queue:
        from src.utils.llm_factory import QueueCallbackHandler
        call_config["callbacks"] = [QueueCallbackHandler(stream_queue, "risk_assessor")]
        
    prompt = f"""Bạn là Socrates Critic Agent của VNU BookMind. Dựa trên chủ đề "{topic}", hồ sơ độc giả "{profile}" và các cuốn sách đề xuất "{books}", hãy đặt ra 3 câu hỏi phản biện sâu sắc.

NGUYÊN TẮC KHÔNG TÓM TẮT HỘ:
- Nếu người dùng yêu cầu tóm tắt sách (ví dụ: "Cuốn sách X nói về điều gì?", "Tóm tắt hộ cuốn Y"), bạn TUYỆT ĐỐI không được tóm tắt nội dung sách hay cung cấp câu trả lời sẵn. 
- Thay vào đó, hãy từ chối tóm tắt hộ một cách lịch sự, tự nhiên và đặt lại 3 câu hỏi phản biện mở Socrates liên quan để buộc độc giả tự tư duy, tự phản biện và tự ghi chép đọc sâu.
- Định hướng câu hỏi: kích thích sự hoài nghi lành mạnh, tranh luận tự thân và định hướng ghi chép đọc sách tích cực.

Hãy trả về dưới dạng:
=== QUÁ TRÌNH TƯ DUY ===
[Xây dựng 3 câu hỏi phản biện mở Socrates và lý do từ chối tóm tắt hộ]
=== CONSOLE MESSAGE ===
Socrates Critic Agent đã kích hoạt câu hỏi phản biện.
=== BÁO CÁO CHI TIẾT ===
CÂU HỎI PHẢN BIỆN SOCRATES (VNU BOOKMIND):
1. [Câu hỏi 1]
2. [Câu hỏi 2]
3. [Câu hỏi 3]
"""
    
    res = await llm.ainvoke(prompt, config=call_config)
    parsed = parse_agent_json(res.content, "detailed_report")
    
    tokens = len(res.content) // 4
    duration = time.time() - start_time
    print_agent_complete("Risk Assessor Agent", duration, tokens)
    actual_model = get_actual_model_used("questioner", MODEL_RESEARCHER_AGENT)
    toks_per_sec = round(tokens / duration, 1) if duration > 0 else 0
    
    if stream_queue:
        await stream_queue.put({
            "type": "node_end",
            "node": "risk_assessor",
            "content": parsed["console_message"],
            "thinking": parsed["thinking"],
            "tokens": tokens,
            "duration": duration,
            "model": actual_model,
            "toks_per_sec": toks_per_sec
        })
        
    return {
        "risks": parsed["detailed_report"],
        "messages": [res],
        "csv_data": parsed["console_message"]
    }
