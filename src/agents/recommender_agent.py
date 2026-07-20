import time
import asyncio
from src.state import ResearchState
from src.utils.llm_factory import create_llm, parse_agent_json, get_actual_model_used
from src.utils.display import print_agent_start, print_agent_complete, print_agent_info
from src.tools.vnu_lic_api import search_koha_api, search_dspace_api, search_bookworm_api, search_vnulic_main
from src.tools.rag_tools import get_rag_context
from config import MODEL_RESEARCHER_AGENT

async def recommender_node(state: ResearchState, config=None) -> dict:
    start_time = time.time()
    topic   = state.get("topic", "")
    profile = state.get("user_profile", "")
    
    stream_queue = config.get("configurable", {}).get("stream_queue") if config else None
    
    # ── Phase 2 bypass: skip re-querying APIs, reuse Phase 1 results ──────────
    if state.get("socratic_answers"):
        if stream_queue:
            await stream_queue.put({"type": "node_start", "node": "analyst"})
            await stream_queue.put({
                "type": "node_end",
                "node": "analyst",
                "content": "Đã truy xuất danh mục sách từ Phase 1 — bỏ qua để tiếp tục Phản Biện.",
                "thinking": "",
                "tokens": 0,
                "duration": 0.0,
                "model": "bypass",
                "toks_per_sec": 0.0
            })
        return {
            "analysis": state.get("analysis", ""),
            "retrieved_context": state.get("retrieved_context", ""),
            "citations": state.get("citations", []),
            "vnu_lic_results": state.get("vnu_lic_results", [])
        }

    if stream_queue:
        await stream_queue.put({"type": "node_start", "node": "analyst"})
        await asyncio.sleep(1.2)
        
    print_agent_start("Recommender Agent", "Truy xuất học liệu từ 4 nguồn VNU-LIC: OPAC, DSpace, Bookworm, lib.vnu.edu.vn")
    
    # ── Query all 4 VNU-LIC sources concurrently ───────────────────────────────
    koha_task     = asyncio.to_thread(search_koha_api,     topic)
    dspace_task   = asyncio.to_thread(search_dspace_api,   topic)
    bookworm_task = asyncio.to_thread(search_bookworm_api, topic)
    vnulic_task   = asyncio.to_thread(search_vnulic_main,  topic)
    
    tasks_res = await asyncio.gather(koha_task, dspace_task, bookworm_task, vnulic_task, return_exceptions=True)
    
    koha_results     = tasks_res[0] if not isinstance(tasks_res[0], Exception) else []
    dspace_results   = tasks_res[1] if not isinstance(tasks_res[1], Exception) else []
    bookworm_results = tasks_res[2] if not isinstance(tasks_res[2], Exception) else []
    vnulic_results   = tasks_res[3] if not isinstance(tasks_res[3], Exception) else []
    
    # ── Local RAG: bổ trợ thêm gợi ý (KHÔNG có URL thật) ─────────────────────
    rag_context, citations = get_rag_context(topic, query_type="consulting")
    
    # Log API results
    print(f"[Recommender] Koha={len(koha_results)}, DSpace={len(dspace_results)}, Bookworm={len(bookworm_results)}, VNU-LIC={len(vnulic_results)}, RAG={'có' if rag_context else 'không'}")
    
    llm = create_llm(MODEL_RESEARCHER_AGENT, config=config, streaming=True)
    call_config = {}
    if stream_queue:
        from src.utils.llm_factory import QueueCallbackHandler
        call_config["callbacks"] = [QueueCallbackHandler(stream_queue, "analyst")]
        
    prompt = f"""Bạn là Recommender Agent của VNU BookMind Socratic.
Hồ sơ độc giả: {profile}
Chủ đề yêu cầu: "{topic}"

KẾT QUẢ TRA CỨU THỰC TẾ TỪ 4 NGUỒN VNU-LIC:

[NGUỒN 1 — VNU-LIC OPAC Koha (sách in thư viện)]:
{koha_results if koha_results else "Không có kết quả từ OPAC Koha."}

[NGUỒN 2 — VNU Repository DSpace (luận án, nghiên cứu)]:
{dspace_results if dspace_results else "Không có kết quả từ DSpace."}

[NGUỒN 3 — Bookworm VNU-LIC (sách điện tử)]:
{bookworm_results if bookworm_results else "Không có kết quả từ Bookworm."}

[NGUỒN 4 — VNU-LIC Trang chủ lib.vnu.edu.vn (federated search)]:
{vnulic_results if vnulic_results else "Không có kết quả từ lib.vnu.edu.vn."}

[TÀI LIỆU BỔ TRỢ RAG (KHÔNG có URL từ VNU-LIC)]:
{rag_context if rag_context else "Không có tài liệu RAG."}

QUY TẮC BẮT BUỘC — KHÔNG ĐƯỢC VI PHẠM:
1. CHỈ sử dụng các URL từ kết quả API thực tế ở trên. TUYỆT ĐỐI không bịa URL mới.
2. Mỗi tài liệu phải ghi rõ nguồn: OPAC Koha / DSpace / Bookworm / lib.vnu.edu.vn / Tài liệu bổ trợ (không có link).
3. Tài liệu từ RAG hoặc kiến thức của bạn không được gắn URL — ghi rõ "Nguồn: Tài liệu bổ trợ (không có liên kết VNU-LIC)".
4. Nếu tất cả 4 nguồn không có kết quả phù hợp, hãy gợi ý sách đúng chuyên ngành nhưng không gắn URL.
5. Gợi ý từ 3 đến 5 tài liệu, ưu tiên tài liệu có URL thật từ 4 nguồn VNU-LIC.

Hãy trả về dưới dạng:
=== QUÁ TRÌNH TƯ DUY ===
[Phân tích hồ sơ độc giả và lý do chọn từng tài liệu từ nguồn nào, xác nhận rõ tài liệu nào có URL thật và tài liệu nào chỉ là gợi ý bổ trợ]
=== CONSOLE MESSAGE ===
Đã gợi ý danh mục tài liệu cá nhân hóa từ 4 nguồn VNU-LIC: OPAC, DSpace, Bookworm và lib.vnu.edu.vn.
=== BÁO CÁO CHI TIẾT ===
DANH MỤC GỢI Ý (VNU-LIC):
[Với mỗi tài liệu, ghi đầy đủ: Tên tài liệu | Tác giả | Nhà xuất bản/Năm | Mã tra cứu | Nguồn | Link (nếu có từ API)]
"""
    
    res = await llm.ainvoke(prompt, config=call_config)
    parsed = parse_agent_json(res.content, "detailed_report")
    
    tokens   = len(res.content) // 4
    duration = time.time() - start_time
    print_agent_complete("Recommender Agent", duration, tokens)
    actual_model  = get_actual_model_used("recommender", MODEL_RESEARCHER_AGENT)
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
        
    all_results = koha_results + dspace_results + bookworm_results + vnulic_results
    return {
        "analysis": parsed["detailed_report"],
        "messages": [res],
        "retrieved_context": parsed["console_message"],
        "citations": citations,
        "vnu_lic_results": all_results
    }
