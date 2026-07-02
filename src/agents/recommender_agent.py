import time
import asyncio
from src.state import ResearchState
from src.utils.llm_factory import create_llm, parse_agent_json, get_actual_model_used
from src.utils.display import print_agent_start, print_agent_complete, print_agent_info
from src.tools.vnu_lic_api import search_koha_api, search_dspace_api
from src.tools.rag_tools import get_rag_context
from config import MODEL_RESEARCHER_AGENT

async def recommender_node(state: ResearchState, config=None) -> dict:
    start_time = time.time()
    topic = state.get("topic", "")
    profile = state.get("user_profile", "")
    
    stream_queue = config.get("configurable", {}).get("stream_queue") if config else None
    if stream_queue:
        await stream_queue.put({
            "type": "node_start",
            "node": "analyst"  # Maps to node-analyst in UI
        })
        
    print_agent_start("Analyst Agent", "Truy xuất học liệu VNU-LIC Koha & DSpace và đề xuất tài liệu phù hợp")
    
    # 1. Query live VNU-LIC Koha and VNU DSpace Repository REST API
    koha_results = await asyncio.to_thread(search_koha_api, topic)
    dspace_results = await asyncio.to_thread(search_dspace_api, topic)
    
    # 2. Get Local RAG context for VNU recommended books
    rag_context, citations = get_rag_context(topic, query_type="consulting")
    
    llm = create_llm(MODEL_RESEARCHER_AGENT, config=config, streaming=True)
    
    call_config = {}
    if stream_queue:
        from src.utils.llm_factory import QueueCallbackHandler
        call_config["callbacks"] = [QueueCallbackHandler(stream_queue, "analyst")]
        
    prompt = f"""Bạn là Recommender Agent của VNU BookMind Socratic. Hãy gợi ý 3 tài liệu phù hợp nhất với độc giả dựa trên hồ sơ: {profile}.
    Sử dụng thông tin sách từ thư viện VNU-LIC Koha: {koha_results}, Luận án/Nghiên cứu khoa học từ VNU Repository DSpace: {dspace_results} và tài liệu bổ trợ RAG: {rag_context}.
    
    Mỗi tài liệu gợi ý phải nêu rõ: Tên tài liệu, Tác giả, Nhà xuất bản/Năm công bố, Mã số tra cứu, Vị trí mượn hoặc Nguồn truy cập, và đặc biệt bắt buộc phải hiển thị một liên kết Markdown có nhãn [Đọc bản PDF / Đọc trực tuyến tại đây](địa_chỉ_pdf_url) sử dụng trường 'pdf_url' từ dữ liệu sách/luận văn được truyền vào.
    
    Hãy trả về dưới dạng:
    === QUÁ TRÌNH TƯ DUY ===
    [Lập luận chọn tài liệu từ VNU-LIC Koha, DSpace và RAG]
    === CONSOLE MESSAGE ===
    Đã gợi ý danh sách sách và luận án cá nhân hóa từ cơ sở dữ liệu VNU-LIC Koha và DSpace.
    === BÁO CÁO CHI TIẾT ===
    DANH MỤC GỢI Ý (VNU-LIC):
    [Liệt kê các tài liệu gợi ý kèm thông tin chi tiết và liên kết đọc PDF]
    """
    
    res = await llm.ainvoke(prompt, config=call_config)
    parsed = parse_agent_json(res.content, "detailed_report")
    
    tokens = len(res.content) // 4
    duration = time.time() - start_time
    print_agent_complete("Analyst Agent", duration, tokens)
    actual_model = get_actual_model_used("recommender", MODEL_RESEARCHER_AGENT)
    toks_per_sec = round(tokens / duration, 1) if duration > 0 else 0
    
    if stream_queue:
        await stream_queue.put({
            "type": "node_end",
            "node": "analyst",
            "content": parsed["console_message"],
            "thinking": parsed["thinking"],
            "tokens": tokens,
            "duration": duration,
            "model": actual_model,
            "toks_per_sec": toks_per_sec
        })
        
    return {
        "analysis": parsed["detailed_report"],
        "messages": [res],
        "retrieved_context": parsed["console_message"],
        "citations": citations
    }
