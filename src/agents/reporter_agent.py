from src.state import ResearchState
from src.utils.llm_factory import create_llm, parse_agent_json
from config import MODEL_RESEARCHER_AGENT

async def reporter_node(state: ResearchState, config=None) -> dict:
    topic = state.get("topic", "")
    profile = state.get("user_profile", "")
    books = state.get("analysis", "")
    questions = state.get("risks", "")
    
    llm = create_llm(MODEL_RESEARCHER_AGENT, config=config)
    
    prompt = f"""Bạn là Reporter Agent của hệ thống VNU BookMind. Hãy tổng hợp toàn bộ thông tin từ các tác nhân trước để tạo nên một Báo cáo Gợi ý & Định hướng đọc sâu Socratic hoàn chỉnh cho độc giả. 
    Báo cáo phải trình bày đẹp mắt bằng Markdown, bao gồm bối cảnh chủ đề, hồ sơ độc giả, danh sách sách nên đọc, và các câu hỏi phản biện Socrates. Vẽ thêm sơ đồ Mermaid mô tả lộ trình đọc sách (ví dụ: Đọc -> Phản biện -> Tự suy ngẫm).
    
    Chủ đề đọc: {topic}
    Hồ sơ độc giả: {profile}
    Sách gợi ý: {books}
    Câu hỏi Socrates: {questions}
    
    Hãy trả về dưới định dạng:
    === QUÁ TRÌNH TƯ DUY ===
    [Tổng hợp và thiết lập định dạng báo cáo]
    === CONSOLE MESSAGE ===
    Báo cáo đọc sâu VNU BookMind đã được tổng hợp thành công.
    === DETAILED REPORT ===
    [Nội dung báo cáo chi tiết sử dụng Markdown]
    === MERMAID DIAGRAM ===
    graph TD
        A[Đọc Sách Chủ Động] --> B[S Socrates Agent Hỏi]
        B --> C[Độc Giả Tranh Biện]
        C --> D[Ghi Nhật Ký Tư Duy]
    === DIAGRAM EXPLANATION ===
    [Giải thích sơ đồ lộ trình đọc]
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
