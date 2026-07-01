from src.state import ResearchState
from src.utils.llm_factory import create_llm, parse_agent_json
from config import MODEL_RESEARCHER_AGENT

async def questioner_node(state: ResearchState, config=None) -> dict:
    topic = state.get("topic", "")
    books = state.get("analysis", "")
    profile = state.get("user_profile", "")
    
    llm = create_llm(MODEL_RESEARCHER_AGENT, config=config)
    prompt = f"""Bạn là Socrates Critic Agent của VNU BookMind. Dựa trên chủ đề "{topic}", hồ sơ độc giả "{profile}" và các cuốn sách đề xuất "{books}", hãy đặt ra 3 câu hỏi phản biện sâu sắc.
    TUÂN THỦ: Không tóm tắt nội dung sách, không đưa ra câu trả lời sẵn. Hãy đặt câu hỏi mở Socrates kích thích sự hoài nghi lành mạnh, tranh luận tự thân và định hướng ghi chép đọc sách tích cực.
    
    Hãy trả về dưới dạng:
    === QUÁ TRÌNH TƯ DUY ===
    [Xây dựng 3 câu hỏi phản biện mở Socrates]
    === CONSOLE MESSAGE ===
    Socrates Critic Agent đã kích hoạt câu hỏi phản biện.
    === BÁO CÁO CHI TIẾT ===
    CÂU HỎI PHẢN BIỆN SOCRATES (VNU BOOKMIND):
    1. [Câu hỏi 1]
    2. [Câu hỏi 2]
    3. [Câu hỏi 3]
    """
    
    res = await llm.ainvoke(prompt)
    parsed = parse_agent_json(res.content, "detailed_report")
    return {
        "risks": parsed["detailed_report"],
        "messages": [res],
        "csv_data": parsed["console_message"]
    }
