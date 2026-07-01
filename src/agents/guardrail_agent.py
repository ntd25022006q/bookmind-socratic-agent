from src.state import ResearchState
from src.utils.llm_factory import create_llm, parse_agent_json
from config import MODEL_GUARDRAIL_AGENT

async def guardrail_node(state: ResearchState, config=None) -> dict:
    topic = state.get("topic", "")
    llm = create_llm(MODEL_GUARDRAIL_AGENT, config=config)
    
    prompt = f"""Bạn là Guardrail Agent của hệ thống VNU BookMind. Nhiệm vụ của bạn là kiểm tra xem câu hỏi đầu vào có liên quan đến chủ đề sách, văn hóa đọc, phương pháp học tập, học liệu hoặc yêu cầu phản biện sách hay không.
    
    Câu hỏi: "{topic}"
    
    Hãy phân tích và trả về kết quả dưới định dạng sau:
    === QUÁ TRÌNH TƯ DUY ===
    [Lập luận xem câu hỏi có thuộc chủ đề sách/đọc/học tập không]
    === CONSOLE MESSAGE ===
    [Thông báo ngắn gọn kết quả kiểm duyệt]
    === BÁO CÁO CHI TIẾT ===
    {{"irrelevant": true hoặc false}}
    """
    
    res = await llm.ainvoke(prompt)
    parsed = parse_agent_json(res.content, "detailed_report")
    import json
    try:
        data = json.loads(parsed["detailed_report"])
        irr = data.get("irrelevant", False)
    except:
        irr = "true" in res.content.lower()
        
    return {
        "irrelevant": irr,
        "messages": [res],
        "analysis": parsed["thinking"],
        "research_data": parsed["console_message"]
    }
