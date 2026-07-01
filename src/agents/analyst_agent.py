from src.state import ResearchState
from src.utils.llm_factory import create_llm, parse_agent_json
from config import MODEL_RESEARCHER_AGENT

async def analyst_node(state: ResearchState, config=None) -> dict:
    topic = state.get("topic", "")
    profile = state.get("user_profile", "")
    llm = create_llm(MODEL_RESEARCHER_AGENT, config=config)
    
    prompt = f"""Bạn là Recommender Agent của hệ thống VNU BookMind. Hãy gợi ý 3 cuốn sách phát hành hợp pháp tại Việt Nam phù hợp với sở thích của người dùng và chủ đề họ đang tìm kiếm. Nêu rõ tác giả, nhà xuất bản, và lý do vì sao họ nên đọc.
    
    Chủ đề: "{topic}"
    Hồ sơ độc giả: {profile}
    
    Hãy trả về dưới định dạng:
    === QUÁ TRÌNH TƯ DUY ===
    [Phân tích danh mục sách phù hợp]
    === CONSOLE MESSAGE ===
    Đã tạo thành công danh mục sách gợi ý cá nhân hóa.
    === BÁO CÁO CHI TIẾT ===
    DANH SÁCH GỢI Ý:
    1. [Tên sách 1] - Tác giả - NXB. Lý do gợi ý.
    2. [Tên sách 2] - Tác giả - NXB. Lý do gợi ý.
    3. [Tên sách 3] - Tác giả - NXB. Lý do gợi ý.
    """
    
    res = await llm.ainvoke(prompt)
    parsed = parse_agent_json(res.content, "detailed_report")
    return {
        "analysis": parsed["detailed_report"],
        "messages": [res],
        "csv_data": parsed["console_message"]
    }
