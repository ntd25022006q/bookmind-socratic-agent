import time
from src.state import ResearchState
from src.utils.llm_factory import create_llm, parse_agent_json, get_actual_model_used
from src.utils.display import print_agent_start, print_agent_complete, print_agent_info
from src.utils.cleaner import full_clean
from config import MODEL_RESEARCHER_AGENT

async def reporter_node(state: ResearchState, config=None) -> dict:
    start_time = time.time()
    topic = state.get("topic", "")
    profile = state.get("user_profile", "")
    books = state.get("analysis", "")
    questions = state.get("risks", "")
    citations = state.get("citations", [])
    
    stream_queue = config.get("configurable", {}).get("stream_queue") if config else None
    if stream_queue:
        await stream_queue.put({
            "type": "node_start",
            "node": "reporter"
        })
        
    print_agent_start("Reporter Agent", "Tổng hợp toàn bộ báo cáo và xây dựng sơ đồ Mermaid")
    llm = create_llm(MODEL_RESEARCHER_AGENT, config=config, streaming=True)
    
    call_config = {}
    if stream_queue:
        from src.utils.llm_factory import QueueCallbackHandler
        call_config["callbacks"] = [QueueCallbackHandler(stream_queue, "reporter")]
        
    prompt = f"""Bạn là Reporter Agent của VNU BookMind Socratic. Nhiệm vụ: Biên soạn một báo cáo đọc sách học thuật chi tiết, đẹp, chuyên nghiệp bằng Markdown để người dùng có thể in hoặc lưu trữ.

QUY TẮC NGHIÊM NGẶT KHI VIẾT BÁO CÁO:
1. VIẾT ĐẦY ĐỦ từng phần, KHÔNG được rút gọn, KHÔNG dùng placeholder như "(đã có ở trên)", "(xem thêm)", "(không lặp lại)", hoặc bất kỳ cụm từ lười biếng nào.
2. TUYỆT ĐỐI KHÔNG dùng ký hiệu ** trong báo cáo. Thay vào đó sử dụng đúng cú pháp Markdown: dùng # ## ### cho tiêu đề, dùng > cho trích dẫn, dùng | cho bảng, dùng - cho danh sách.
3. TUYỆT ĐỐI KHÔNG dùng chữ Hán, chữ Kanji, chữ Hiragana, chữ Katakana hay bất kỳ ký tự tiếng Trung/Nhật/Hàn nào trong báo cáo. Chỉ dùng tiếng Việt và tiếng Anh.
4. Báo cáo bắt buộc phải chứa một BẢNG TÀI LIỆU THAM KHẢO gồm đúng 6 cột: STT, tên tài liệu, tác giả, năm, nguồn, link.
   - Bạn PHẢI chèn chính xác 10 cuốn sách tham khảo sau vào bảng (đặc biệt giữ nguyên các liên kết WorldCat click được):
     | STT | Tên tài liệu | Tác giả | Năm | Nguồn | Liên kết |
     | 1 | Tư duy phản biện | Richard Paul, Linda Elder | 2021 | NXB Lao Động | [WorldCat](https://www.worldcat.org/) |
     | 2 | 21 bài học cho thế kỷ 21 | Yuval Noah Harari | 2020 | NXB Thế Giới | [ISBN 9786047754329](https://www.worldcat.org/isbn/9786047754329) |
     | 3 | Sapiens: Lược sử loài người | Yuval Noah Harari | 2017 | NXB Thế Giới | [ISBN 9786047736041](https://www.worldcat.org/isbn/9786047736041) |
     | 4 | Good to Great | Jim Collins | 2001 | HarperBusiness | Học liệu tự học bổ trợ (Chưa có liên kết trực tuyến) |
     | 5 | Competitive Strategy | Michael Porter | 1980 | Free Press | Học liệu tự học bổ trợ (Chưa có liên kết trực tuyến) |
     | 6 | The Lean Startup | Eric Ries | 2011 | Crown Business | Học liệu tự học bổ trợ (Chưa có liên kết trực tuyến) |
     | 7 | Crossing the Chasm | Geoffrey Moore | 1991 | HarperBusiness | Học liệu tự học bổ trợ (Chưa có liên kết trực tuyến) |
     | 8 | The Innovator's Dilemma | Clayton Christensen | 1997 | Harvard Business Review Press | Học liệu tự học bổ trợ (Chưa có liên kết trực tuyến) |
     | 9 | AI Superpowers | Kai-Fu Lee | 2018 | Houghton Mifflin Harcourt | Học liệu tự học bổ trợ (Chưa có liên kết trực tuyến) |
     | 10 | Prediction Machines | Ajay Agrawal, Joshua Gans, Avi Goldfarb | 2018 | Harvard Business Press | Học liệu tự học bổ trợ (Chưa có liên kết trực tuyến) |
5. QUY TẮC PHÂN BIỆT ĐƯỜNG DẪN (LINK) TRONG BẢNG: Đối với 10 cuốn sách trên, giữ nguyên các liên kết được cung cấp. Đối với tài liệu từ RAG/Koha/Bookworm, điền link thật (nếu có) hoặc điền "Học liệu tự học bổ trợ (Chưa có liên kết trực tuyến)".
6. TÍCH HỢP KATEX: Nếu chủ đề hoặc các tài liệu có liên quan đến khoa học, công nghệ, toán học hoặc định lượng, hãy hiển thị các công thức toán học/thuật toán bằng cú pháp KaTeX (dùng $...$ cho công thức nội dòng và $$...$$ cho công thức khối riêng biệt) để giao diện hiển thị chuyên nghiệp.
7. TUYỆT ĐỐI KHÔNG ghi "Ngày:" hay bất kỳ ngày tháng nào vào tên tổ chức hay footer báo cáo.
8. Phần TÀI LIỆU THAM KHẢO cuối báo cáo PHẢI liệt kê đầy đủ URL thực tế của từng tài liệu (nếu có).

Chủ đề: {topic}
Hồ sơ: {profile}
Sách gợi ý (bao gồm tên, tác giả, URL): {books}
Câu hỏi Socrates & Phản biện: {questions}
Tài liệu trích nguồn: {citations}

Hãy trả về ĐÚNG theo định dạng sau (không thêm bớt ký tự === nào khác):
=== QUÁ TRÌNH TƯ DUY ===
[Phân tích cách bạn sẽ cấu trúc báo cáo — không quá 5 dòng]
=== CONSOLE MESSAGE ===
Đã biên soạn xong báo cáo đọc sâu Socratic VNU BookMind.
=== DETAILED REPORT ===
# Báo Cáo Đọc Sâu — VNU BookMind Socratic
*Trung tâm Thư viện và Tri thức số, Đại học Quốc gia Hà Nội*

[Toàn bộ nội dung báo cáo chi tiết — đầy đủ, không placeholder, không **, không chữ Hán/Kanji, không ghi ngày tháng vào dòng tên tổ chức]
=== MERMAID DIAGRAM ===
[Vẽ sơ đồ Mermaid flowchart LR phản ánh NỘI DUNG THỰC TẾ của báo cáo trên. LƯU Ý NGHIÊM NGẶT VỀ CÚ PHÁP: Tuyệt đối không dùng nét đứt sai cú pháp `-.-->` hoặc `--.>`. Chỉ sử dụng nét đứt có mũi tên duy nhất là `-.->` (chỉ có 1 dấu chấm ở giữa 2 dấu gạch ngang, ví dụ: A -.-> B hoặc A -. Text .-> B). KHÔNG vẽ sơ đồ quy trình agent. KHÔNG dùng ký tự đặc biệt Hán/Kanji trong nhãn nút.]
=== DIAGRAM EXPLANATION ===
[Giải thích chi tiết sơ đồ bằng tiếng Việt, dựa trên nội dung báo cáo — mô tả từng nút và mối liên hệ, giúp người đọc hiểu rõ cấu trúc tư duy. Tối thiểu 3 đoạn văn hoàn chỉnh. Không dùng ** và không dùng chữ Hán.]
"""
    
    res = await llm.ainvoke(prompt, config=call_config)
    parsed = parse_agent_json(res.content, "detailed_report")
    
    # Apply full post-processing: strip CJK, fix URLs, remove stray **, clean filenames
    parsed["detailed_report"] = full_clean(parsed.get("detailed_report", ""))
    parsed["diagram_explanation"] = full_clean(parsed.get("diagram_explanation", ""))
    
    # Auto-heal Mermaid syntax errors (broken dotted links commonly generated by LLMs)
    mermaid_code = full_clean(parsed.get("mermaid_diagram", ""))
    mermaid_code = mermaid_code.replace("-.-->", "-.->")
    mermaid_code = mermaid_code.replace("--.>", "-.->")
    mermaid_code = mermaid_code.replace("-.--", "-.-")
    parsed["mermaid_diagram"] = mermaid_code
    
    # Save diagram
    from config import OUTPUT_DIR
    from pathlib import Path
    Path(OUTPUT_DIR).mkdir(exist_ok=True)
    (Path(OUTPUT_DIR) / "diagram.mermaid").write_text(parsed["mermaid_diagram"], encoding="utf-8")
    (Path(OUTPUT_DIR) / "diagram_explanation.txt").write_text(parsed["diagram_explanation"], encoding="utf-8")
    
    tokens = len(res.content) // 4
    duration = time.time() - start_time
    print_agent_complete("Reporter Agent", duration, tokens)
    actual_model = get_actual_model_used("reporter", MODEL_RESEARCHER_AGENT)
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
        "report": parsed["detailed_report"],
        "messages": [res],
        "csv_data": parsed["console_message"]
    }
