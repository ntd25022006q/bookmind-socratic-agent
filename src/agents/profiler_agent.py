from src.state import ResearchState
from src.utils.llm_factory import create_llm, parse_agent_json
from config import MODEL_RESEARCHER_AGENT

async def profiler_node(state: ResearchState, config=None) -> dict:
    topic = state.get("topic", "")
    llm = create_llm(MODEL_RESEARCHER_AGENT, config=config)
    
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
    
    res = await llm.ainvoke(prompt)
    parsed = parse_agent_json(res.content, "detailed_report")
    return {
        "user_profile": parsed["detailed_report"],
        "messages": [res],
        "research_data": parsed["console_message"]
    }
