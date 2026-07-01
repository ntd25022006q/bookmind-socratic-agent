from src.state import ResearchState
from src.utils.llm_factory import create_llm, parse_agent_json
from src.tools.rag_tools import get_rag_context
from config import MODEL_GUARDRAIL_AGENT

async def guardrail_node(state: ResearchState, config=None) -> dict:
    topic = state.get("topic", "")
    llm = create_llm(MODEL_GUARDRAIL_AGENT, config=config)
    
    # Retrieve local RAG context to check guidelines
    context, _ = get_rag_context(topic, query_type="qa")
    
    prompt = f"""Bạn là Guardrail Agent của VNU BookMind Socratic. Nhiệm vụ của bạn là kiểm tra xem câu hỏi có thuộc phạm vi học thuật, tri thức sách vở, phương pháp đọc, hoặc mượn tài liệu thư viện hay không.
    
    Câu hỏi: "{topic}"
    Ngữ cảnh định hướng: {context}
    
    Hãy trả về dưới dạng:
    === QUÁ TRÌNH TƯ DUY ===
    [Lập luận xem câu hỏi có thuộc chủ đề học thuật/sách vở không]
    === CONSOLE MESSAGE ===
    [Thông báo ngắn gọn]
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
