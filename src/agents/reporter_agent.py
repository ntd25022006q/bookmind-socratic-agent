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
            "node": "reporter"  # Maps to node-reporter in UI
        })
        
    print_agent_start("Reporter Agent", "Tổng hợp toàn bộ báo cáo và xây dựng sơ đồ Mermaid")
    llm = create_llm(MODEL_RESEARCHER_AGENT, config=config, streaming=True)
    
    call_config = {}
    if stream_queue:
        from src.utils.llm_factory import QueueCallbackHandler
        call_config["callbacks"] = [QueueCallbackHandler(stream_queue, "reporter")]
        
    prompt = f"""Bạn là Reporter Agent tổng hợp của VNU BookMind Socratic. Hãy tổng hợp báo cáo đọc sách chi tiết, đẹp mắt bằng Markdown. Đảm bảo giữ lại đầy đủ các liên kết [Đọc bản PDF / Đọc trực tuyến tại đây](địa_chỉ_pdf_url) cho mỗi cuốn sách và tài liệu nghiên cứu.
    Báo cáo bao gồm:
    - Bối cảnh và Tinh thần Đọc sách Socratic tại VNU
    - Hồ sơ học thuật của độc giả
    - Danh sách gợi ý từ quầy học liệu số VNU-LIC (kèm liên kết đọc PDF)
    - Các câu hỏi phản biện mở giúp đọc sâu và phản biện tư duy điểm mù
    - Trích dẫn thư mục nguồn.
    
    Chủ đề: {topic}
    Hồ sơ: {profile}
    Sách gợi ý: {books}
    Câu hỏi Socrates & Phản biện: {questions}
    Tài liệu trích nguồn: {citations}
    
    Hãy trả về dưới dạng:
    === QUÁ TRÌNH TƯ DUY ===
    [Hệ thống hóa bố cục báo cáo đọc sâu]
    === CONSOLE MESSAGE ===
    Đã kết xuất báo cáo đọc sâu Socratic hoàn chỉnh.
    === DETAILED REPORT ===
    # BÁO CÁO ĐỌC SÂU SOCRATES VNU BOOKMIND
    [Nội dung Markdown chuyên nghiệp]
    === MERMAID DIAGRAM ===
    graph TD
        A[Độc gia đặt câu hỏi] --> B[Profiler xây hồ sơ]
        B --> C[Recommender tìm Koha API]
        C --> D[Socrates đặt câu hỏi phản biện]
        D --> E[Critic phản biện nhận thức]
        E --> F[Sinh viên ghi nhật ký đọc sâu]
    === DIAGRAM EXPLANATION ===
    Sơ đồ mô tả quy trình tư duy phản biện 5 tác tử hỗ trợ sinh viên tự học chủ động.
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
