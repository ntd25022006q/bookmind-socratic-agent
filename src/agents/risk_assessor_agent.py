from src.state import ResearchState
from src.utils.llm_factory import create_llm, parse_agent_json
from config import MODEL_RESEARCHER_AGENT

async def risk_assessor_node(state: ResearchState, config=None) -> dict:
    topic = state.get("topic", "")
    books = state.get("analysis", "")
    llm = create_llm(MODEL_RESEARCHER_AGENT, config=config)
    
    prompt = f"""Bạn là Socrates Critic Agent của hệ thống VNU BookMind. Dựa trên chủ đề "{topic}" và các cuốn sách gợi ý: {books}, hãy tạo ra 3 câu hỏi phản biện mở kiểu Socrates. Nhiệm vụ của bạn không phải là tóm tắt sách hay trả lời hộ, mà là bắt độc giả phải động não, tự phản biện và ghi nhật ký đọc.
    
    Hãy trả về dưới định dạng:
    === QUÁ TRÌNH TƯ DUY ===
    [Thiết lập các câu hỏi kích thích tư duy]
    === CONSOLE MESSAGE ===
    Socrates Agent đã tạo xong các câu hỏi phản biện mở.
    === BÁO CÁO CHI TIẾT ===
    CÂU HỎI PHẢN BIỆN SOCRATES:
    - Câu hỏi 1: [Nội dung câu hỏi]
    - Câu hỏi 2: [Nội dung câu hỏi]
    - Câu hỏi 3: [Nội dung câu hỏi]
    """
    
    res = await llm.ainvoke(prompt)
    parsed = parse_agent_json(res.content, "detailed_report")
    return {
        "risks": parsed["detailed_report"],
        "messages": [res],
        "retrieved_context": parsed["console_message"]
    }
