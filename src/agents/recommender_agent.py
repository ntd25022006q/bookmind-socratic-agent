from src.state import ResearchState
from src.utils.llm_factory import create_llm, parse_agent_json
from src.tools.vnu_lic_api import search_koha_api
from src.tools.rag_tools import get_rag_context
from config import MODEL_RESEARCHER_AGENT

async def recommender_node(state: ResearchState, config=None) -> dict:
    topic = state.get("topic", "")
    profile = state.get("user_profile", "")
    
    # 1. Call simulated VNU-LIC Koha API
    koha_results = search_koha_api(topic)
    
    # 2. Get Local RAG context for VNU recommended books
    rag_context, citations = get_rag_context(topic, query_type="consulting")
    
    llm = create_llm(MODEL_RESEARCHER_AGENT, config=config)
    prompt = f"""Bạn là Recommender Agent của VNU BookMind Socratic. Hãy gợi ý 3 cuốn sách phù hợp nhất với độc giả dựa trên hồ sơ: {profile}.
    Sử dụng thông tin sách từ thư viện VNU-LIC: {koha_results} và tài liệu bổ trợ: {rag_context}.
    Mỗi cuốn sách gợi ý phải nêu rõ: Tên sách, Tác giả, Nhà xuất bản, Mã sách (Biblionumber/ISBN), vị trí kệ sách tại quầy thư viện VNU-LIC, và lý do tại sao cuốn sách này giúp nâng cao tư duy của họ.
    
    Hãy trả về dưới dạng:
    === QUÁ TRÌNH TƯ DUY ===
    [Lập luận chọn sách từ VNU-LIC DB và RAG]
    === CONSOLE MESSAGE ===
    Đã gợi ý danh sách sách học trình cá nhân hóa từ cơ sở dữ liệu VNU-LIC Koha.
    === BÁO CÁO CHI TIẾT ===
    DANH MỤC GỢI Ý (VNU-LIC):
    [Liệt kê 3 sách kèm Biblionumber, ISBN, Vị trí kệ mượn và lý do]
    """
    
    res = await llm.ainvoke(prompt)
    parsed = parse_agent_json(res.content, "detailed_report")
    return {
        "analysis": parsed["detailed_report"],
        "messages": [res],
        "retrieved_context": parsed["console_message"],
        "citations": citations
    }
