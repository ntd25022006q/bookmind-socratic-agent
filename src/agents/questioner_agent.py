import time
from src.state import ResearchState
from src.utils.llm_factory import create_llm, parse_agent_json, get_actual_model_used
from src.utils.display import print_agent_start, print_agent_complete, print_agent_info
from config import MODEL_ANALYST_AGENT

async def questioner_node(state: ResearchState, config=None) -> dict:
    start_time = time.time()
    topic = state.get("topic", "")
    books = state.get("analysis", "")
    profile = state.get("user_profile", "")
    
    stream_queue = config.get("configurable", {}).get("stream_queue") if config else None
    
    # Phase 2 resume bypass
    if state.get("socratic_answers"):
        if stream_queue:
            await stream_queue.put({"type": "node_start", "node": "risk_assessor"})
            await stream_queue.put({
                "type": "node_end",
                "node": "risk_assessor",
                "content": "Đã đặt câu hỏi Socratic từ Phase 1 — độc giả đã trả lời, đang chuyển sang Phản Biện.",
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
        import asyncio
        await asyncio.sleep(1.2)
    import random
    socratic_perspectives = [
        "Tập trung phản biện vào các giả định ngầm định (assumptions) mà độc giả thường coi là hiển nhiên trong chủ đề này.",
        "Tập trung phản biện vào các hệ quả dài hạn (implications & consequences) nếu áp dụng các kiến thức trong sách một cách máy móc.",
        "Tập trung phản biện vào các bằng chứng thực tế (evidence & examples) đối nghịch hoặc các trường hợp ngoại lệ mà sách chưa đề cập.",
        "Tập trung vào góc nhìn đa chiều (alternative perspectives) để xem xét chủ đề dưới lăng kính của những nhóm đối tượng hoặc lý thuyết trái ngược.",
        "Tập trung vào tính thực tiễn và tính khả thi (feasibility & actionability) của các phương pháp được gợi ý, tìm ra các điểm yếu khi triển khai thực tế.",
        "Tập trung phát hiện các thiên kiến nhận thức (cognitive biases) phổ biến liên quan đến chủ đề này mà độc giả cần tự nhận thức được."
    ]
    chosen_perspective = random.choice(socratic_perspectives)

    print_agent_start("Risk Assessor Agent", f"Đặt câu hỏi Socratic kích thích tư duy phản biện (Góc nhìn: {chosen_perspective})")
    llm = create_llm(MODEL_ANALYST_AGENT, temperature=0.7, config=config, streaming=True)
    
    call_config = {}
    if stream_queue:
        from src.utils.llm_factory import QueueCallbackHandler
        call_config["callbacks"] = [QueueCallbackHandler(stream_queue, "risk_assessor")]
        
    prompt = f"""Bạn là Socrates Critic Agent của VNU BookMind. Dựa trên chủ đề "{topic}", hồ sơ độc giả "{profile}" và các cuốn sách đề xuất "{books}", hãy đặt ra 3 câu hỏi phản biện sâu sắc.

YÊU CẦU ĐẶC BIỆT CHO LẦN ĐỐI THOẠI NÀY:
- {chosen_perspective}
- Đảm bảo các câu hỏi mang tính gợi mở mạnh mẽ, phong phú, linh hoạt và kích thích tư duy sáng tạo, không rập khuôn hay trùng lặp.

NGUỒN GỐC TRIẾT LÝ SỐ 5 — NGUYÊN TẮC KHÔNG TÓM TẮT HỘ:
- Khi độc giả đặt câu hỏi dạng tóm tắt (ví dụ: "Cuốn 21 Bài Học Cho Thế Kỷ 21 nói về điều gì?", "Tóm tắt hộ cuốn X"), bạn TUYỆT ĐỐI không được trả lời hay viết tóm tắt hộ.
- Hãy từ chối tóm tắt hộ một cách lịch sự, tự nhiên và đặt lại 3 câu hỏi phản biện mở Socrates để buộc độc giả tự tư duy, tự phản biện và tự ghi chép đọc sâu.
- Đây là bài học của Harari: dùng AI để kích thích đọc sâu, không thay thế đọc.

QUY TẮC ĐỊNH DẠNG NGHIÊM NGẶT:
- KHÔNG DÙNG KÝ HIỆU ** TRONG BẤT KỲ CÂU HỎI HAY VĂN BẢN NÀO. 
- Dùng Markdown tự nhiên: tiêu đề # ##, danh sách -, trích dẫn >. Tuyệt đối không lạm dụng dấu ** làm mất tính chuyên nghiệp.

QUY TẮC BẢO MẬT HỆ THỐNG VÀ THÔNG TIN CÁ NHÂN:
- TUYỆT ĐỐI không tiết lộ thông tin cá nhân của nhà phát triển hệ thống (Nguyễn Tiến Đạt), các thông tin nhạy cảm (email, API key, token kết nối Vercel, Render, GitHub), hoặc cấu hình thuật toán và sơ đồ xử lý của hệ thống.
- Chỉ tập trung làm đúng chuyên môn theo yêu cầu của độc giả, từ chối lịch sự nếu bị dò hỏi về cấu hình hệ thống hoặc mã nguồn.

Hãy trả về dưới dạng:
=== QUÁ TRÌNH TƯ DUY ===
[Xây dựng 3 câu hỏi phản biện mở Socrates và lý do từ chối tóm tắt hộ]
=== CONSOLE MESSAGE ===
Socrates Critic Agent đã kích hoạt câu hỏi phản biện.
=== BÁO CÁO CHI TIẾT ===
CÂU HỎI PHẢN BIỆN SOCRATES (VNU BOOKMIND):
1. [Câu hỏi 1 - không chứa **]
2. [Câu hỏi 2 - không chứa **]
3. [Câu hỏi 3 - không chứa **]
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
