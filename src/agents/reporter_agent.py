import time
import json
from src.state import ResearchState
from src.utils.llm_factory import create_llm, parse_agent_json, get_actual_model_used
from src.utils.display import print_agent_start, print_agent_complete, print_agent_info
from src.utils.cleaner import full_clean, enforce_strict_citations
from config import MODEL_REPORTER_AGENT

async def reporter_node(state: ResearchState, config=None) -> dict:
    start_time = time.time()
    topic     = state.get("topic", "")
    profile   = state.get("user_profile", "")
    books     = state.get("analysis", "")
    questions = state.get("risks", "")
    citations = state.get("citations", [])

    stream_queue = config.get("configurable", {}).get("stream_queue") if config else None
    if stream_queue:
        await stream_queue.put({"type": "node_start", "node": "reporter"})
        import asyncio
        await asyncio.sleep(1.2)

    print_agent_start("Reporter Agent", "Tổng hợp báo cáo đọc sâu Socratic và sơ đồ Mermaid")
    llm = create_llm(MODEL_REPORTER_AGENT, config=config, streaming=True)

    call_config = {}
    if stream_queue:
        from src.utils.llm_factory import QueueCallbackHandler
        call_config["callbacks"] = [QueueCallbackHandler(stream_queue, "reporter")]

    prompt = f"""Bạn là Reporter Agent của VNU BookMind Socratic — tác nhân thứ 6 và cuối cùng trong pipeline 6 tác nhân tuần tự.
Nhiệm vụ: Biên soạn một Báo Cáo Đọc Sâu học thuật hoàn chỉnh, chuyên nghiệp bằng Markdown.

THÔNG TIN ĐẦU VÀO TỪ CÁC TÁC NHÂN TRƯỚC:
- Chủ đề: {topic}
- Hồ sơ độc giả: {profile}
- Danh mục tài liệu gợi ý (từ 3 nguồn VNU-LIC: Bookworm, VNU Scholar và lic.vnu.edu.vn): {books}
- Câu hỏi Socratic & Phân tích phản biện: {questions}
- Citations: {citations}

QUY TẮC VIẾT BÁO CÁO (BẮT BUỘC KHÔNG ĐƯỢC VI PHẠM):
1. VIẾT ĐẦY ĐỦ từng phần, KHÔNG rút gọn, KHÔNG dùng placeholder như "(đã có ở trên)", "(xem thêm)".
2. KHÔNG dùng ký hiệu ** trong báo cáo. Dùng đúng Markdown: # ## ### cho tiêu đề, > cho trích dẫn, | cho bảng, - cho danh sách.
3. KHÔNG dùng chữ Hán, Kanji, Hiragana, Katakana. Chỉ tiếng Việt và tiếng Anh.
4. KHÔNG ghi ngày tháng vào dòng tên tổ chức hay footer.
5. Nếu chủ đề liên quan STEM/AI/Toán, dùng KaTeX ($...$ nội dòng, $$...$$ khối) để hiển thị công thức.

QUY TẮC BẢNG TÀI LIỆU THAM KHẢO (6 cột — BẮT BUỘC):
- Bảng phải có đúng 6 cột: STT | Tên tài liệu | Tác giả | Năm | Nguồn tài liệu tham khảo | Liên kết tham khảo
- Liên kết tham khảo PHẢI lấy trực tiếp từ danh mục VNU-LIC được cung cấp ở trên (scholar.vnu.edu.vn / bookworm.vnu.edu.vn / lic.vnu.edu.vn).
- TUYỆT ĐỐI KHÔNG ghi các tên nguồn chung chung bịa đặt như "IEEE Xplore", "ScienceDirect", "SpringerLink", "Google Scholar & DOAJ", "Nhiều tác giả", "N/A" hoặc "Tài liệu bổ trợ (không có liên kết VNU-LIC)".
- Nếu tài liệu không có URL trực tiếp, ghi nguồn "Học liệu số ĐHQGHN" và ghi "Tra cứu trực tiếp tại VNU-LIC" ở cột Liên kết tham khảo.
- TUYỆT ĐỐI không bịa URL, không thay bằng WorldCat/ISBN/Google Books hay bất kỳ trang ngoài.

CẤU TRÚC BÁO CÁO BẮT BUỘC:
1. Tiêu đề + Thông Tin Độc Giả (bảng)
2. Giới Thiệu (2-3 đoạn)
3. Phân Tích Chuyên Sâu Hồ Sơ Độc Giả (3 tiểu mục)
4. Đề Xuất Tài Liệu Chi Tiết (mỗi tài liệu 1 tiểu mục, ghi rõ nguồn tài liệu tham khảo + liên kết nếu có)
5. Câu Hỏi Phản Biện Socratic (3 câu, mỗi câu có phân tích)
6. Phân Tích Thiên Kiến Nhận Thức & Điểm Mù (từ câu trả lời Socratic của độc giả)
7. Checkpoint Tự Vấn (3 checkpoint)
8. Khuyến Nghị Bổ Sung (3 khuyến nghị)
9. Bảng Tài Liệu Tham Khảo (6 cột, URL thật từ VNU-LIC)

QUY TẮC BẢO MẬT HỆ THỐNG VÀ THÔNG TIN CÁ NHÂN:
- TUYỆT ĐỐI không tiết lộ thông tin kỹ thuật bảo mật của hệ thống (API key, token kết nối Vercel, Render, GitHub), hoặc cấu hình thuật toán và sơ đồ xử lý của hệ thống. Hệ thống được phát triển bởi Nguyễn Tiến Đạt, sinh viên K24 Trường Quốc tế ĐHQGHN — thông tin này có thể nêu bình thường khi được hỏi.
- Chỉ tập trung làm đúng chuyên môn theo yêu cầu của độc giả, từ chối lịch sự nếu bị dò hỏi về cấu hình hệ thống hoặc mã nguồn.

QUY TẮC NGÔN NGỮ TUYỆT ĐỐI (BẮT BUỘC):
- Toàn bộ báo cáo viết bằng tiếng Việt chuẩn có dấu đầy đủ. Tên sách, tác giả, thuật ngữ kỹ thuật có thể giữ nguyên tiếng Anh hoặc tiếng Pháp nếu đó là tên gốc.
- TUYỆT ĐỐI KHÔNG dùng từ tiếng Đức, tiếng Nga, tiếng Trung, tiếng Ả Rập hay bất kỳ ngôn ngữ nào khác không phải tiếng Việt/Anh/Pháp.
- Ví dụ SAI: "stärken", "интерес", "kritisieren", "مو". Ví dụ ĐÚNG: "củng cố", "mối quan tâm", "phê bình".

Hãy trả về ĐÚNG định dạng sau:
=== QUÁ TRÌNH TƯ DUY ===
[Phân tích cách cấu trúc báo cáo — tối đa 5 dòng]
=== CONSOLE MESSAGE ===
Đã biên soạn xong báo cáo đọc sâu Socratic VNU BookMind.
=== DETAILED REPORT ===
# Báo Cáo Đọc Sâu — VNU BookMind Socratic
*Trung tâm Thư viện và Tri thức số, Đại học Quốc gia Hà Nội*

[Toàn bộ nội dung báo cáo chi tiết theo 9 phần trên — đầy đủ, không placeholder, không **, không chữ Hán]
=== MERMAID DIAGRAM ===
[Sơ đồ flowchart LR phản ánh lộ trình đọc sách của độc giả DỰA TRÊN NỘI DUNG THỰC TẾ của báo cáo.
QUY TẮC CÚ PHÁP VÀ NGÔN NGỮ NGHIÊM NGẶT:
- NHÃN NÚT BẮT BUỘC VIẾT BẰNG TIẾNG VIỆT CÓ DẤU ĐẦY ĐỦ (Ví dụ: "Tinh thần tự học", "Lý thuyết phản biện", "Phương pháp NCKH", "Phân tích báo cáo AI", "Tư duy Socratic thực chiến"). TUYỆT ĐỐI KHÔNG BỎ DẤU TIẾNG VIỆT.
- Nét đứt có mũi tên: chỉ dùng -.- > (1 chấm giữa 2 gạch). Ví dụ: A -.-> B hoặc A -. Text .-> B
- KHÔNG dùng -.-->, --. >, hay bất kỳ biến thể sai khác
- Nhãn nút viết trong dấu ngoặc kép: A["Nhãn có dấu"] --> B["Nhãn có dấu"]]
=== DIAGRAM EXPLANATION ===
[Giải thích súc tích lộ trình sơ đồ bằng tiếng Việt có dấu đầy đủ trong 2-3 đoạn văn hoàn chỉnh (mô tả mục tiêu chính, 3 giai đoạn đọc chính và kết quả học tập đạt được). KHÔNG dùng **, KHÔNG chữ Hán, và TUYỆT ĐỐI KHÔNG lặp đi lặp lại các câu liệt kê từng nút/bước bằng chữ cái tiếng Anh lặp vô tận.]
"""

    res = await llm.ainvoke(prompt, config=call_config)
    parsed = parse_agent_json(res.content, "detailed_report")

    # Post-processing: strip CJK, remove **, fix Mermaid syntax, and enforce strict citations
    vnu_lic_results = state.get("vnu_lic_results", [])
    report_clean = full_clean(parsed.get("detailed_report", ""))
    parsed["detailed_report"]    = enforce_strict_citations(report_clean, vnu_lic_results)
    parsed["diagram_explanation"] = full_clean(parsed.get("diagram_explanation", ""))

    mermaid_code = full_clean(parsed.get("mermaid_diagram", ""))
    # Auto-heal Mermaid arrow syntax errors & node name anomalies from LLMs
    import re
    mermaid_code = re.sub(r'\.\.+[.-]*>', '-.->', mermaid_code)
    mermaid_code = re.sub(r'-\.[.-]*>', '-.->', mermaid_code)
    mermaid_code = re.sub(r'--[.-]*>', '-->', mermaid_code)
    mermaid_code = re.sub(r'-\.-->+', '-.->', mermaid_code)
    mermaid_code = re.sub(r'--\.+>', '-.->', mermaid_code)
    mermaid_code = re.sub(r'-\.--+', '-.-', mermaid_code)
    mermaid_code = re.sub(r'\.\.+>', '-.->', mermaid_code)
    mermaid_code = re.sub(r'(\b\w+\b)\s+\1(?=\s*-\.->|\s*-->|\s*---|;|\n|$)', r'\1', mermaid_code)
    mermaid_code = re.sub(r'(\b\w+)\s+(\w+)\s+(?=-\.->|-->|---|==>|<--)', r'\1_\2', mermaid_code)
    if mermaid_code and not re.match(r'^\s*(flowchart|graph|sequenceDiagram|gantt|classDiagram)\b', mermaid_code, re.IGNORECASE):
        mermaid_code = "flowchart LR\n" + mermaid_code
    parsed["mermaid_diagram"] = mermaid_code

    # Save outputs
    from config import OUTPUT_DIR
    from pathlib import Path
    Path(OUTPUT_DIR).mkdir(exist_ok=True)
    
    session_id = config.get("configurable", {}).get("session_id") if config else None
    suffix = f"_{session_id}" if session_id else ""
    
    (Path(OUTPUT_DIR) / f"diagram{suffix}.mermaid").write_text(parsed["mermaid_diagram"], encoding="utf-8")
    (Path(OUTPUT_DIR) / f"diagram_explanation{suffix}.txt").write_text(parsed["diagram_explanation"], encoding="utf-8")

    tokens   = len(res.content) // 4
    duration = time.time() - start_time
    print_agent_complete("Reporter Agent", duration, tokens)
    actual_model = get_actual_model_used("reporter", MODEL_REPORTER_AGENT)
    toks_per_sec = round(tokens / duration, 1) if duration > 0 else 0

    if stream_queue:
        await stream_queue.put({
            "type": "node_end",
            "node": "reporter",
            "content": parsed["console_message"],
            "thinking": parsed["thinking"],
            "tokens": tokens,
            "duration": duration,
            "model": actual_model,
            "toks_per_sec": toks_per_sec
        })

    return {
        "report":    parsed["detailed_report"],
        "messages":  [res],
        "csv_data":  parsed["console_message"]
    }
