import time
from src.state import ResearchState
from src.utils.llm_factory import create_llm, parse_agent_json, get_actual_model_used
from src.utils.display import print_agent_start, print_agent_complete, print_agent_info
from config import MODEL_RESEARCHER_AGENT

async def reporter_node(state: ResearchState, config=None) -> dict:
    start_time = time.time()
    topic = state.get("topic", "")
    profile = state.get("user_profile", "")
    books = state.get("analysis", "")
    questions = state.get("risks", "")
    citations = state.get("citations", [])
    
    stream_queue = config.get("configurable", {}).get("stream_queue") if config else None
    if stream_queue:
        await stream_queue.put({
            "type": "node_start",
            "node": "reporter"
        })
        
    print_agent_start("Reporter Agent", "Tổng hợp toàn bộ báo cáo và xây dựng sơ đồ Mermaid")
    llm = create_llm(MODEL_RESEARCHER_AGENT, config=config, streaming=True)
    
    call_config = {}
    if stream_queue:
        from src.utils.llm_factory import QueueCallbackHandler
        call_config["callbacks"] = [QueueCallbackHandler(stream_queue, "reporter")]
        
    prompt = f"""Bạn là Reporter Agent của VNU BookMind Socratic. Nhiệm vụ: Biên soạn một báo cáo đọc sách học thuật chi tiết, đẹp, chuyên nghiệp bằng Markdown để người dùng có thể in hoặc lưu trữ.

QUY TẮC NGHIÊM NGẶT KHI VIẾT BÁO CÁO:
1. VIẾT ĐẦY ĐỦ từng phần, KHÔNG được rút gọn, KHÔNG dùng placeholder như "(đã có ở trên)", "(xem thêm)", "(không lặp lại)", hoặc bất kỳ cụm từ lười biếng nào.
2. TUYỆT ĐỐI KHÔNG dùng ký hiệu ** trong báo cáo. Thay vào đó sử dụng đúng cú pháp Markdown: dùng # ## ### cho tiêu đề, dùng > cho trích dẫn, dùng | cho bảng, dùng - cho danh sách.
3. Mỗi cuốn sách gợi ý phải có: tựa đề, tác giả, nhà xuất bản, năm, lý do gợi ý chi tiết (ít nhất 3 câu phân tích), và liên kết đọc/xem trực tiếp.
4. Liên kết phải là URL hoàn chỉnh thực tế, ví dụ [Đọc trực tuyến tại đây](https://...) — KHÔNG ĐƯỢC để link giả.

Chủ đề: {topic}
Hồ sơ: {profile}
Sách gợi ý (bao gồm tên, tác giả, URL): {books}
Câu hỏi Socrates & Phản biện: {questions}
Tài liệu trích nguồn: {citations}

Hãy trả về ĐÚNG theo định dạng sau (không thêm bớt ký tự === nào khác):
=== QUÁ TRÌNH TƯ DUY ===
[Phân tích cách bạn sẽ cấu trúc báo cáo — không quá 5 dòng]
=== CONSOLE MESSAGE ===
Đã biên soạn xong báo cáo đọc sâu Socratic VNU BookMind.
=== DETAILED REPORT ===
# Báo Cáo Đọc Sâu — VNU BookMind Socratic
*Trung tâm Thư viện và Tri thức số, Đại học Quốc gia Hà Nội*

[Toàn bộ nội dung báo cáo chi tiết — đầy đủ, không placeholder, không **]
=== MERMAID DIAGRAM ===
graph TD
    A[Độc giả đặt câu hỏi] --> B[Profiler phân tích hồ sơ]
    B --> C[Recommender tra cứu Koha API]
    C --> D[Questioner đặt câu hỏi Socratic]
    D --> E[Critic phản biện nhận thức]
    E --> F[Reporter tổng hợp báo cáo]
=== DIAGRAM EXPLANATION ===
Sơ đồ mô tả quy trình 6 tác tử AI cộng tác theo phương pháp Socratic, hỗ trợ sinh viên đọc sâu và phản biện tư duy tại VNU.
"""
    
    res = await llm.ainvoke(prompt, config=call_config)
    parsed = parse_agent_json(res.content, "detailed_report")
    
    # Save diagram
    from config import OUTPUT_DIR
    from pathlib import Path
    Path(OUTPUT_DIR).mkdir(exist_ok=True)
    (Path(OUTPUT_DIR) / "diagram.mermaid").write_text(parsed["mermaid_diagram"], encoding="utf-8")
    (Path(OUTPUT_DIR) / "diagram_explanation.txt").write_text(parsed["diagram_explanation"], encoding="utf-8")
    
    tokens = len(res.content) // 4
    duration = time.time() - start_time
    print_agent_complete("Reporter Agent", duration, tokens)
    actual_model = get_actual_model_used("reporter", MODEL_RESEARCHER_AGENT)
    toks_per_sec = round(tokens / duration, 1) if duration > 0 else 0
    
    if stream_queue:
        await stream_queue.put({
            "type": "node_end",
            "node": "reporter",
            "content": parsed["console_message"],
            "thinking": parsed["thinking"],
            "tokens": tokens,
            "duration": duration,
            "model": actual_model,
            "toks_per_sec": toks_per_sec
        })
        
    return {
        "report": parsed["detailed_report"],
        "messages": [res],
        "csv_data": parsed["console_message"]
    }
