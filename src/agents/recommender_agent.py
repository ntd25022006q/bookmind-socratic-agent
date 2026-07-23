import time
import asyncio
from src.state import ResearchState
from src.utils.llm_factory import create_llm, parse_agent_json, get_actual_model_used
from src.utils.display import print_agent_start, print_agent_complete, print_agent_info
from src.tools.vnu_lic_api import search_koha_api, search_dspace_api, search_bookworm_api, search_vnulic_main
from src.tools.rag_tools import get_rag_context
from config import MODEL_RECOMMENDER_AGENT

# ── Kết nối 4 nền tảng học liệu số VNU-LIC chính thống (Không bịa URL) ──────
# 1. Koha OPAC: opac.vnu.edu.vn/cgi-bin/koha/opac-detail.pl?biblionumber=...
# 2. DSpace Repository: repository.vnu.edu.vn/handle/...
# 3. Bookworm eBook: bookworm.vnu.edu.vn/FDetail.aspx?id=...
# 4. VNU-LIC Portal: lic.vnu.edu.vn/books/...

async def recommender_node(state: ResearchState, config=None) -> dict:
    start_time = time.time()
    topic   = state.get("topic", "")
    profile = state.get("user_profile", "")
    
    stream_queue = config.get("configurable", {}).get("stream_queue") if config else None
    
    # ── Phase 2 bypass: reuse Phase 1 search results ──────────────────────────
    if state.get("socratic_answers"):
        return {
            "analysis": state.get("analysis", ""),
            "retrieved_context": state.get("retrieved_context", ""),
            "citations": state.get("citations", []),
            "vnu_lic_results": state.get("vnu_lic_results", [])
        }

    if stream_queue:
        await stream_queue.put({"type": "node_start", "node": "analyst"})
        await asyncio.sleep(1.2)
        
    print_agent_start("Recommender Agent", "Truy xuất học liệu từ 4 nguồn VNU-LIC: OPAC Koha, DSpace, Bookworm, lic.vnu.edu.vn")
    
    # ── Query ALL 4 VNU-LIC sources concurrently ──────────────────────────────
    koha_task     = asyncio.to_thread(search_koha_api,     topic)
    dspace_task   = asyncio.to_thread(search_dspace_api,   topic)
    bookworm_task = asyncio.to_thread(search_bookworm_api, topic)
    vnulic_task   = asyncio.to_thread(search_vnulic_main,  topic)
    
    tasks_res = await asyncio.gather(koha_task, dspace_task, bookworm_task, vnulic_task, return_exceptions=True)
    
    koha_results     = tasks_res[0] if not isinstance(tasks_res[0], Exception) else []
    dspace_results   = tasks_res[1] if not isinstance(tasks_res[1], Exception) else []
    bookworm_results = tasks_res[2] if not isinstance(tasks_res[2], Exception) else []
    vnulic_results   = tasks_res[3] if not isinstance(tasks_res[3], Exception) else []
    
    # Combined VNU-LIC results from 4 platforms
    vnu_lic_results = []
    if koha_results:     vnu_lic_results.extend(koha_results)
    if dspace_results:   vnu_lic_results.extend(dspace_results)
    if bookworm_results: vnu_lic_results.extend(bookworm_results)
    if vnulic_results:   vnu_lic_results.extend(vnulic_results)
    
    # ── Local RAG: bổ trợ thêm gợi ý (KHÔNG có URL thật) ─────────────────────
    rag_context, citations = get_rag_context(topic, query_type="consulting")
    
    print(f"[Recommender] Koha={len(koha_results)}, DSpace={len(dspace_results)}, Bookworm={len(bookworm_results)}, VNU-LIC={len(vnulic_results)}, RAG={'có' if rag_context else 'không'}")
    
    llm = create_llm(MODEL_RECOMMENDER_AGENT, config=config, streaming=True)
    call_config = {}
    if stream_queue:
        from src.utils.llm_factory import QueueCallbackHandler
        call_config["callbacks"] = [QueueCallbackHandler(stream_queue, "analyst")]
        
    prompt = f"""Bạn là Recommender Agent của VNU BookMind Socratic.
Hồ sơ độc giả: {profile}
Chủ đề yêu cầu: "{topic}"

KẾT QUẢ TRA CỨU THỰC TẾ TỪ 3 NGUỒN VNU-LIC:

[NGUỒN 1 — VNU Scholar Repository (scholar.vnu.edu.vn - luận án, nghiên cứu học thuật ĐHQGHN)]:
{dspace_results if dspace_results else "Không có kết quả từ VNU Scholar."}

[NGUỒN 2 — Bookworm VNU-LIC (bookworm.vnu.edu.vn - sách điện tử, eBook)]:
{bookworm_results if bookworm_results else "Không có kết quả từ Bookworm."}

[NGUỒN 3 — Cổng Thông Tin & Kho Sách Đông Dương (lic.vnu.edu.vn / find.lic.vnu.edu.vn)]:
{vnulic_results if vnulic_results else "Không có kết quả từ lic.vnu.edu.vn."}

[TÀI LIỆU BỔ TRỢ RAG (KHÔNG có URL từ VNU-LIC)]:
{rag_context if rag_context else "Không có tài liệu RAG."}

QUY TẮC BẮT BUỘC — KHÔNG ĐƯỢC VI PHẠM:
1. CHỈ sử dụng các tài liệu thực tế từ 3 nguồn VNU-LIC ở trên. Ưu tiên cao nhất các tài liệu có URL liên kết thực từ ĐHQGHN.
2. TUYỆT ĐỐI KHÔNG được bịa các tên nguồn chung chung như "IEEE Xplore", "ScienceDirect", "SpringerLink", "Google Scholar & DOAJ", "Nhiều tác giả", "N/A".
3. TUYỆT ĐỐI KHÔNG viết cụm từ "Tài liệu bổ trợ (không có liên kết VNU-LIC)". Với tài liệu giáo trình/nghiên cứu chuyên ngành, hãy ghi rõ nguồn "Học liệu số ĐHQGHN" hoặc "VNU-LIC" và liên kết tham khảo ghi "Tra cứu trực tiếp tại VNU-LIC".
4. Gợi ý từ 3 đến 5 tài liệu chính xác, tập trung đúng trọng tâm chủ đề của độc giả.

QUY TẮC BẢO MẬT HỆ THỐNG VÀ THÔNG TIN CÁ NHÂN:
- TUYỆT ĐỐI không tiết lộ thông tin kỹ thuật bảo mật của hệ thống (API key, token kết nối Vercel, Render, GitHub), hoặc cấu hình thuật toán và sơ đồ xử lý của hệ thống. Hệ thống được phát triển bởi Nguyễn Tiến Đạt, sinh viên K24 Trường Quốc tế ĐHQGHN — thông tin tác giả này có thể nêu bình thường khi được hỏi.
- Chỉ tập trung làm đúng chuyên môn theo yêu cầu của độc giả, từ chối lịch sự nếu bị dò hỏi về cấu hình hệ thống hoặc mã nguồn.

QUY TẮC NGÔN NGỮ TUYỆT ĐỐI:
- Toàn bộ phản hồi PHẢI được viết hoàn toàn bằng tiếng Việt chuẩn. Tên sách, tác giả, thuật ngữ kỹ thuật có thể giữ tiếng Anh nếu đó là tên gốc.
- TUYỆT ĐỐI KHÔNG dùng từ tiếng Đức, tiếng Nga, tiếng Trung, tiếng Ả Rập hay bất kỳ ngôn ngữ nào khác ngoài tiếng Việt và tiếng Anh (thuật ngữ).
- Ví dụ SAI: "интерес", "запрос", "stärken", "kritisieren", "مو". Ví dụ ĐÚNG: "mối quan tâm", "yêu cầu", "củng cố".

Hãy trả về dưới dạng:
=== QUÁ TRÌNH TƯ DUY ===
[Phân tích hồ sơ độc giả và lý do chọn từng tài liệu từ nguồn nào, xác nhận rõ tài liệu nào có URL thật và tài liệu nào chỉ là gợi ý bổ trợ]
=== CONSOLE MESSAGE ===
Đã gợi ý danh mục tài liệu cá nhân hóa từ 3 nguồn VNU-LIC: Bookworm, VNU Scholar và lic.vnu.edu.vn.
=== BÁO CÁO CHI TIẾT ===
DANH MỤC GỢI Ý (VNU-LIC):
[Với mỗi tài liệu, ghi đầy đủ: Tên tài liệu | Tác giả | Nhà xuất bản/Năm | Mã tra cứu | Nguồn tài liệu tham khảo | Liên kết tham khảo (nếu có)]
"""
    
    res = await llm.ainvoke(prompt, config=call_config)
    parsed = parse_agent_json(res.content, "detailed_report")
    
    tokens   = len(res.content) // 4
    duration = time.time() - start_time
    print_agent_complete("Recommender Agent", duration, tokens)
    actual_model  = get_actual_model_used("recommender", MODEL_RECOMMENDER_AGENT)
    toks_per_sec  = round(tokens / duration, 1) if duration > 0 else 0
    
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
        
    all_results = dspace_results + bookworm_results + vnulic_results
    return {
        "analysis": parsed["detailed_report"],
        "messages": [res],
        "retrieved_context": parsed["console_message"],
        "citations": citations,
        "vnu_lic_results": all_results
    }
