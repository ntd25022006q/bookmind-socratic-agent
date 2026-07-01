from src.state import ResearchState
from src.utils.llm_factory import create_llm, parse_agent_json
from config import MODEL_RESEARCHER_AGENT

async def reporter_node(state: ResearchState, config=None) -> dict:
    topic = state.get("topic", "")
    profile = state.get("user_profile", "")
    books = state.get("analysis", "")
    questions = state.get("risks", "")
    citations = state.get("citations", [])
    
    llm = create_llm(MODEL_RESEARCHER_AGENT, config=config)
    prompt = f"""Bạn là Reporter Agent tổng hợp của VNU BookMind Socratic. Hãy tổng hợp báo cáo đọc sách chi tiết, đẹp mắt bằng Markdown.
    Báo cáo bao gồm:
    - Bối cảnh và Tinh thần Đọc sách Socratic tại VNU
    - Hồ sơ học thuật của độc giả
    - Danh sách gợi ý từ quầy học liệu số VNU-LIC
    - Các câu hỏi phản biện mở giúp đọc sâu
    - Trích dẫn thư mục nguồn.
    
    Chủ đề: {topic}
    Hồ sơ: {profile}
    Sách gợi ý: {books}
    Câu hỏi Socrates: {questions}
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
        A[Độc giả đặt câu hỏi] --> B[Profiler xây hồ sơ]
        B --> C[Recommender tìm Koha API]
        C --> D[Socrates đặt câu hỏi phản biện]
        D --> E[Sinh viên ghi nhật ký đọc sâu]
    === DIAGRAM EXPLANATION ===
    Sơ đồ mô tả quy trình tư duy phản biện 4 tác tử hỗ trợ sinh viên tự học chủ động.
    """
    
    res = await llm.ainvoke(prompt)
    parsed = parse_agent_json(res.content, "detailed_report")
    
    # Save diagram
    from config import OUTPUT_DIR
    from pathlib import Path
    Path(OUTPUT_DIR).mkdir(exist_ok=True)
    (Path(OUTPUT_DIR) / "diagram.mermaid").write_text(parsed["mermaid_diagram"], encoding="utf-8")
    (Path(OUTPUT_DIR) / "diagram_explanation.txt").write_text(parsed["diagram_explanation"], encoding="utf-8")
    
    return {
        "report": parsed["detailed_report"],
        "messages": [res],
        "csv_data": parsed["console_message"]
    }
