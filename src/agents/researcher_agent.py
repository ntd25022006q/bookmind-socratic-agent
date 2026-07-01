from src.state import ResearchState
from src.utils.llm_factory import create_llm, parse_agent_json
from config import MODEL_RESEARCHER_AGENT

async def researcher_node(state: ResearchState, config=None) -> dict:
    topic = state.get("topic", "")
    llm = create_llm(MODEL_RESEARCHER_AGENT, config=config)
    
    prompt = f"""Bạn là Profiler Agent của hệ thống VNU BookMind. Nhiệm vụ của bạn là xây dựng hồ sơ độc giả dựa trên câu hỏi và chủ đề đọc sách của họ. Hãy suy đoán xem người dùng có thể là sinh viên ngành nào, sở thích đọc sách là gì, và mục tiêu phát triển bản thân của họ.
    
    Câu hỏi/Chủ đề: "{topic}"
    
    Hãy trả về dưới định dạng:
    === QUÁ TRÌNH TƯ DUY ===
    [Phân tích tâm lý và hồ sơ độc giả]
    === CONSOLE MESSAGE ===
    Đã xây dựng xong hồ sơ độc giả cho chủ đề: {topic}.
    === BÁO CÁO CHI TIẾT ===
    HỒ SƠ ĐỘC GIẢ GIẢ ĐỊNH:
    - Ngành học dự kiến: [Ngành học]
    - Gu đọc sách: [Sở thích]
    - Nhu cầu tư duy: [Mục tiêu]
    """
    
    res = await llm.ainvoke(prompt)
    parsed = parse_agent_json(res.content, "detailed_report")
    return {
        "user_profile": parsed["detailed_report"],
        "messages": [res],
        "research_data": parsed["console_message"]
    }
