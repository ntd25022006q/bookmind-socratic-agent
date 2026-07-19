import time
import asyncio
from src.state import ResearchState
from src.utils.llm_factory import create_llm, parse_agent_json, get_actual_model_used
from src.utils.display import print_agent_start, print_agent_complete, print_agent_info
from src.tools.vnu_lic_api import search_koha_api, search_dspace_api, search_bookworm_api
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
        
    print_agent_start("Analyst Agent", "Truy xuất học liệu VNU-LIC Koha, DSpace & Bookworm và đề xuất tài liệu phù hợp")
    
    # 1. Query live VNU-LIC Koha, VNU DSpace Repository and VNU Bookworm APIs
    koha_results = await asyncio.to_thread(search_koha_api, topic)
    dspace_results = await asyncio.to_thread(search_dspace_api, topic)
    bookworm_results = await asyncio.to_thread(search_bookworm_api, topic)
    
    # 2. Get Local RAG context for VNU recommended books
    rag_context, citations = get_rag_context(topic, query_type="consulting")
    
    llm = create_llm(MODEL_RESEARCHER_AGENT, config=config, streaming=True)
    
    call_config = {}
    if stream_queue:
        from src.utils.llm_factory import QueueCallbackHandler
        call_config["callbacks"] = [QueueCallbackHandler(stream_queue, "analyst")]
        
    prompt = f"""Bạn là Recommender Agent của VNU BookMind Socratic. Hãy gợi ý 3 tài liệu phù hợp nhất với độc giả dựa trên hồ sơ học tập/sở thích: {profile}.
    Sử dụng thông tin sách từ:
    - Sách in thư viện VNU-LIC Koha: {koha_results}
    - Luận án/Nghiên cứu khoa học từ VNU Repository DSpace: {dspace_results}
    - Sách giáo trình số/eBook từ Bookworm VNU-LIC: {bookworm_results}
    - Tài liệu bổ trợ RAG: {rag_context}
    
    QUY TẮC QUAN TRỌNG VỀ ĐƯỜNG DẪN (URL):
    - CÓ ĐƯỜNG DẪN THẬT: Chỉ khi tài liệu được lấy từ kết quả API (Koha, DSpace, Bookworm) có chứa trường 'pdf_url' hoặc 'url' thật sự hoạt động, bạn mới hiển thị liên kết Markdown trỏ đến địa chỉ đó.
    - KHÔNG ĐƯỢC BỊA LINK: Đối với mọi tài liệu bổ trợ khác (sách do bạn tự suy luận, sách từ RAG không kèm link thật), bạn TUYỆT ĐỐI KHÔNG ĐƯỢC bịa đặt ra liên kết giả (như openlibrary.org/isbn/..., cas.vnu.edu.vn, link chế...). Đối với các tài liệu này, hãy viết đầy đủ Tên tài liệu, Tác giả, Nhà xuất bản, Năm công bố, và ghi chú rõ "Nguồn: Học liệu tự học bổ trợ (Chưa có liên kết trực tuyến)".
    
    Mỗi tài liệu gợi ý phải nêu rõ: Tên tài liệu, Tác giả, Nhà xuất bản/Năm công bố, Mã số tra cứu, Vị trí mượn hoặc Nguồn truy cập, và liên kết Markdown trỏ chính xác (nếu có).
    
    Hãy trả về dưới dạng:
    === QUÁ TRÌNH TƯ DUY ===
    [Lập luận chọn tài liệu từ các nguồn Koha, DSpace, Bookworm và RAG, phân loại rõ tài liệu nào có link thật và tài liệu nào không dùng link]
    === CONSOLE MESSAGE ===
    Đã gợi ý danh sách sách in, luận án và sách điện tử cá nhân hóa từ các cơ sở dữ liệu VNU-LIC Koha, DSpace và Bookworm.
    === BÁO CÁO CHI TIẾT ===
    DANH MỤC GỢI Ý (VNU-LIC):
    [Liệt kê các tài liệu gợi ý kèm thông tin chi tiết và liên kết đọc trực tuyến/PDF nếu có]
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
