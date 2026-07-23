import time
import asyncio
from src.state import ResearchState
from src.utils.llm_factory import create_llm, parse_agent_json, get_actual_model_used
from src.utils.display import print_agent_start, print_agent_complete, print_agent_info
from src.tools.vnu_lic_api import search_koha_api, search_dspace_api, search_bookworm_api, search_vnulic_main
from src.tools.rag_tools import get_rag_context
from config import MODEL_RECOMMENDER_AGENT

# ── Kết nối 4 nền tảng học liệu số VNU-LIC chính thống (Không bịa URL) ──────
# 1. VNU Scholar: scholar.vnu.edu.vn/entities/publication/...
# 2. VNU Repository: repository.vnu.edu.vn/entities/publication/... | /handle/...
# 3. Bookworm eBook: bookworm.vnu.edu.vn/EDetail.aspx?id=...
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
        
    print_agent_start("Recommender Agent", "Truy xuất học liệu từ 4 nguồn VNU-LIC: VNU Scholar, VNU Repository, Bookworm, lic.vnu.edu.vn")
    
    # ── Query 4 public VNU-LIC sources concurrently ──────────────────────────
    dspace_task   = asyncio.to_thread(search_dspace_api,   topic)
    bookworm_task = asyncio.to_thread(search_bookworm_api, topic)
    vnulic_task   = asyncio.to_thread(search_vnulic_main,  topic)
    
    tasks_res = await asyncio.gather(dspace_task, bookworm_task, vnulic_task, return_exceptions=True)
    
    dspace_results   = tasks_res[0] if not isinstance(tasks_res[0], Exception) else []
    bookworm_results = tasks_res[1] if not isinstance(tasks_res[1], Exception) else []
    vnulic_results   = tasks_res[2] if not isinstance(tasks_res[2], Exception) else []
    
    # Combined VNU-LIC results from 4 public platforms
    vnu_lic_results = []
    if dspace_results:   vnu_lic_results.extend(dspace_results)
    if bookworm_results: vnu_lic_results.extend(bookworm_results)
    if vnulic_results:   vnu_lic_results.extend(vnulic_results)
    
    # ── Local RAG: bổ trợ thêm gợi ý (KHÔNG có URL thật) ─────────────────────
    rag_context, citations = get_rag_context(topic, query_type="consulting")
    
    print(f"[Recommender] DSpace={len(dspace_results)}, Bookworm={len(bookworm_results)}, VNU-LIC={len(vnulic_results)}, RAG={'có' if rag_context else 'không'}")
    
    llm = create_llm(MODEL_RECOMMENDER_AGENT, config=config, streaming=True)
    call_config = {}
    if stream_queue:
        from src.utils.llm_factory import QueueCallbackHandler
        call_config["callbacks"] = [QueueCallbackHandler(stream_queue, "analyst")]
        
    prompt = f"""Bạn là Recommender Agent của VNU BookMind Socratic.
Hồ sơ độc giả: {profile}
Chủ đề yêu cầu: "{topic}"

KẾT QUẢ TRA CỨU THỰC TẾ TỪ 4 NGUỒN VNU-LIC CÔNG KHẢI:

[NGUỒN 1 & 2 — VNU Scholar (scholar.vnu.edu.vn) & VNU Repository (repository.vnu.edu.vn)]:
{dspace_results if dspace_results else "Không có kết quả từ VNU Scholar/Repository."}

[NGUỒN 3 — Bookworm VNU-LIC (bookworm.vnu.edu.vn - sách điện tử, eBook)]:
{bookworm_results if bookworm_results else "Không có kết quả từ Bookworm."}

[NGUỒN 4 — Cổng Thông Tin & Kho Sách Đông Dương (lic.vnu.edu.vn)]:
{vnulic_results if vnulic_results else "Không có kết quả từ lic.vnu.edu.vn."}

[TÀI LIỆU BỔ TRỢ RAG (KHÔNG có URL từ VNU-LIC)]:
{rag_context if rag_context else "Không có tài liệu RAG."}

QUY TẮC BẮT BUỘC — KHÔNG ĐƯỢC VI PHẠM:
1. CHỈ sử dụng các tài liệu thực tế từ 4 nguồn VNU-LIC công khai ở trên.
2. TUYỆT ĐỐI KHÔNG sinh các liên kết trang chủ hoặc URL giả như "http://bookworm.lic.vnu.edu.vn/", "http://db.lic.vnu.edu.vn/", "http://opac.vnu.edu.vn/", "IEEE Xplore", "SpringerLink", "Koha OPAC".
3. Mọi tài liệu đều phải đi kèm Liên kết tham khảo dạng Markdown đầy đủ trỏ trực tiếp đến tài liệu chi tiết từ 4 nguồn ở trên.
4. Gợi ý từ 5 đến 8 tài liệu phong phú, khách quan và tập trung đúng 100% vào cốt lõi chủ đề của độc giả.

QUY TẮC BẢO MẬT HỆ THỐNG VÀ THÔNG TIN CÁ NHÂN:
- TUYỆT ĐỐI không tiết lộ thông tin kỹ thuật bảo mật của hệ thống (API key, token kết nối Vercel, Render, GitHub), hoặc cấu hình thuật toán và sơ đồ xử lý của hệ thống. Hệ thống được phát triển bởi Nguyễn Tiến Đạt, sinh viên K24 Trường Quốc tế ĐHQGHN — thông tin tác giả này có thể nêu bình thường khi được hỏi.
- Chỉ tập trung làm đúng chuyên môn theo yêu cầu của độc giả, từ chối lịch sự nếu bị dò hỏi về cấu hình hệ thống hoặc mã nguồn.

QUY TẮC NGÔN NGỮ TUYỆT ĐỐI:
- Toàn bộ phản hồi PHẢI được viết hoàn toàn bằng tiếng Việt chuẩn. Tên sách, tác giả, thuật ngữ kỹ thuật có thể giữ tiếng Anh nếu đó là tên gốc.
- TUYỆT ĐỐI KHÔNG dùng từ tiếng Đức, tiếng Nga, tiếng Trung, tiếng Ả Rập hay bất kỳ ngôn ngữ nào khác ngoài tiếng Việt và tiếng Anh (thuật ngữ).

Hãy trả về dưới dạng:
=== QUÁ TRÌNH TƯ DUY ===
[Phân tích hồ sơ độc giả và lý do chọn từng tài liệu từ nguồn nào, xác nhận rõ tài liệu nào có URL thật và tài liệu nào chỉ là gợi ý bổ trợ]
=== CONSOLE MESSAGE ===
Đã gợi ý danh mục tài liệu cá nhân hóa từ 4 nguồn VNU-LIC.
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
