import time
import re
from src.state import ResearchState
from src.utils.llm_factory import create_llm, parse_agent_json, get_actual_model_used
from src.utils.display import print_agent_start, print_agent_complete, print_agent_info
from config import MODEL_PROFILER_AGENT

async def profiler_node(state: ResearchState, config=None) -> dict:
    start_time = time.time()
    topic = state.get("topic", "")
    
    stream_queue = config.get("configurable", {}).get("stream_queue") if config else None
    
    # Phase 2 resume bypass: reuse Phase 1 reader profile
    if state.get("socratic_answers"):
        return {
            "user_profile": state.get("user_profile", ""),
            "research_data": state.get("research_data", "")
        }
        
    if stream_queue:
        await stream_queue.put({
            "type": "node_start",
            "node": "researcher"  # Maps to node-researcher in UI
        })
        import asyncio
        await asyncio.sleep(1.2)
        
    print_agent_start("Researcher Agent", "Phân tích hồ sơ độc giả và nhu cầu tự học chủ động")
    llm = create_llm(MODEL_PROFILER_AGENT, config=config, streaming=True)
    
    call_config = {}
    if stream_queue:
        from src.utils.llm_factory import QueueCallbackHandler
        call_config["callbacks"] = [QueueCallbackHandler(stream_queue, "researcher")]
        
    user_profile_raw = state.get("user_profile", "")
    
    # Helper to extract values by regex from the profile text
    def extract_field(label_pat, text):
        match = re.search(label_pat + r'\s*:\s*([^,;\n]+)', text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return ""
        
    # These labels support BOTH old frontend format ('Họ tên sinh viên: X, Phong cách học & đọc ưa thích: X')
    # AND new frontend format ('Họ tên: X, Phong cách học: X') for backward compatibility
    p_name    = extract_field(r'Họ tên', user_profile_raw)          # matches 'Họ tên:' AND 'Họ tên sinh viên:'
    p_mssv    = extract_field(r'MSSV', user_profile_raw)
    p_major   = extract_field(r'Ngành học', user_profile_raw)
    p_school  = extract_field(r'Trường thành viên', user_profile_raw)
    p_style   = extract_field(r'Phong cách học', user_profile_raw)   # matches 'Phong cách học:' AND 'Phong cách học &'
    p_year    = extract_field(r'Sinh viên năm', user_profile_raw)
    p_purpose = extract_field(r'Mục đích đọc sách', user_profile_raw)
    p_interests = extract_field(r'Lĩnh vực quan tâm', user_profile_raw)
    
    # Fallback: if name still empty, try broader pattern
    if not p_name:
        m = re.search(r'Họ[^:,;\n]{0,20}:\s*([^,;\n]+)', user_profile_raw, re.IGNORECASE)
        if m:
            p_name = m.group(1).strip()
    # Fallback: style might have '& đọc ưa thích' suffix blocking match
    if not p_style:
        m = re.search(r'Phong cách[^:,;\n]{0,30}:\s*([^,;\n]+)', user_profile_raw, re.IGNORECASE)
        if m:
            p_style = m.group(1).strip()
    
    p_name_val      = p_name      if p_name      else "(Chưa cung cấp)"
    p_mssv_val      = p_mssv      if p_mssv      else "(Chưa cung cấp)"
    p_major_val     = p_major     if p_major     else "(Chưa cung cấp)"
    p_school_val    = p_school    if p_school    else "(Chưa cung cấp)"
    p_style_val     = p_style     if p_style     else "(Chưa cung cấp)"
    p_year_val      = p_year      if p_year      else "(Chưa cung cấp)"
    p_purpose_val   = p_purpose   if p_purpose   else "(Chưa cung cấp)"
    p_interests_val = p_interests if p_interests else "(Chưa cung cấp)"

    prompt = f"""Bạn là Profiler Agent của VNU BookMind Socratic. Hãy phân tích sở thích đọc sách, gu học thuật và phong cách tư duy của độc giả từ truy vấn: "{topic}".
    Đặc biệt, độc giả đã cung cấp thông tin hồ sơ của họ như sau: "{user_profile_raw}".
    Nhiệm vụ của bạn là kết hợp thông tin hồ sơ này và chủ đề truy vấn để lập nên một báo cáo Hồ sơ Độc giả thông minh và đầy đủ nhất.
    
    ĐẶC BIỆT QUAN TRỌNG VỀ BẢO TOÀN THÔNG TIN HỒ SƠ ĐỘC GIẢ (Yêu cầu bắt buộc):
    - Bạn PHẢI GIỮ NGUYÊN VĂN 100% các giá trị sau vào đúng vị trí tương ứng trong báo cáo:
      * Họ và tên độc giả: Bạn bắt buộc phải ghi đúng là '{p_name_val}'
      * Mã số sinh viên: Bạn bắt buộc phải ghi đúng là '{p_mssv_val}'
      * Ngành học & Khóa: Bạn bắt buộc phải ghi đúng là '{p_major_val}'
      * Trường thành viên: Bạn bắt buộc phải ghi đúng là '{p_school_val}'
      * Phong cách tư duy: Bạn bắt buộc phải ghi đúng là '{p_style_val}'
    - TUYỆT ĐỐI không được tự ý phỏng đoán, sửa chữa, thay đổi hay bịa đặt bất kỳ thông tin nào khác về tên tuổi, trường học hay mã số sinh viên của độc giả.
    
    NGUYÊN TẮC BẢO MẬT HỆ THỐNG VÀ THÔNG TIN CÁ NHÂN:
    - TUYỆT ĐỐI không tiết lộ thông tin kỹ thuật bảo mật của hệ thống (API key, token kết nối Vercel, Render, GitHub), hoặc cấu hình thuật toán và sơ đồ xử lý của hệ thống. Hệ thống được phát triển bởi Nguyễn Tiến Đạt, sinh viên K24 Trường Quốc tế ĐHQGHN — thông tin tác giả này có thể nêu bình thường khi được hỏi.
    - Chỉ tập trung làm đúng chuyên môn theo yêu cầu của độc giả, từ chối lịch sự nếu bị dò hỏi về cấu hình hệ thống hoặc mã nguồn.

    QUY TẮC NGÔN NGỮ TUYỆT ĐỐI:
    - Toàn bộ phản hồi PHẢI được viết hoàn toàn bằng tiếng Việt chuẩn.
    - TUYỆT ĐỐI KHÔNG được dùng bất kỳ từ nào bằng tiếng Đức, tiếng Nga, tiếng Trung, tiếng Ả Rập hay bất kỳ ngôn ngữ nào khác ngoài tiếng Việt và tiếng Anh (thuật ngữ kỹ thuật).
    - Ví dụ SAI: "интерес", "запрос", "stärken", "kritisieren", "مو". Ví dụ ĐÚNG: "mối quan tâm", "yêu cầu", "củng cố", "phê bình".

    Hãy trả về dưới dạng:
    === QUÁ TRÌNH TƯ DUY ===
    [Phân tích nhu cầu tư duy, phong cách đọc dựa trên hồ sơ cung cấp và truy vấn]
    === CONSOLE MESSAGE ===
    Đã lập hồ sơ độc giả thông minh từ thông tin đăng ký.
    === BÁO CÁO CHI TIẾT ===
    HỒ SƠ ĐỘC GIẢ:
    - Họ và tên độc giả: {p_name_val}
    - Mã số sinh viên: {p_mssv_val}
    - Ngành học & Khóa: {p_major_val}
    - Trường thành viên: {p_school_val}
    - Sinh viên năm: {p_year_val}
    - Mục đích đọc sách: {p_purpose_val}
    - Lĩnh vực đặc biệt quan tâm: {p_interests_val}
    - Phong cách tư duy: {p_style_val}
    - Phân tích chuyên sâu: [Phân tích lĩnh vực đặc biệt quan tâm dựa trên thông tin hồ sơ và chủ đề truy vấn "{topic}"]
    """
    
    res = await llm.ainvoke(prompt, config=call_config)
    parsed = parse_agent_json(res.content, "detailed_report")
    
    tokens = len(res.content) // 4
    duration = time.time() - start_time
    print_agent_complete("Researcher Agent", duration, tokens)
    actual_model = get_actual_model_used("profiler", MODEL_PROFILER_AGENT)
    toks_per_sec = round(tokens / duration, 1) if duration > 0 else 0
    
    if stream_queue:
        await stream_queue.put({
            "type": "node_end",
            "node": "researcher",
            "content": parsed["console_message"],
            "thinking": parsed["thinking"],
            "tokens": tokens,
            "duration": duration,
            "model": actual_model,
            "toks_per_sec": toks_per_sec
        })
        
    return {
        "user_profile": parsed["detailed_report"],
        "messages": [res],
        "research_data": parsed["console_message"]
    }
