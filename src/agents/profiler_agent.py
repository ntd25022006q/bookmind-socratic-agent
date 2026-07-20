import time
import re
from src.state import ResearchState
from src.utils.llm_factory import create_llm, parse_agent_json, get_actual_model_used
from src.utils.display import print_agent_start, print_agent_complete, print_agent_info
from config import MODEL_RESEARCHER_AGENT

async def profiler_node(state: ResearchState, config=None) -> dict:
    start_time = time.time()
    topic = state.get("topic", "")
    
    stream_queue = config.get("configurable", {}).get("stream_queue") if config else None
    
    # Phase 2 resume bypass
    if state.get("socratic_answers"):
        if stream_queue:
            await stream_queue.put({
                "type": "node_start",
                "node": "researcher"
            })
            await stream_queue.put({
                "type": "node_end",
                "node": "researcher",
                "content": state.get("research_data", ""),
                "thinking": "",
                "tokens": 0,
                "duration": 0.0,
                "model": "bypass",
                "toks_per_sec": 0.0
            })
        return {
            "user_profile": state.get("user_profile", ""),
            "research_data": state.get("research_data", "")
        }
        
    if stream_queue:
        await stream_queue.put({
            "type": "node_start",
            "node": "researcher"  # Maps to node-researcher in UI
        })
        
    print_agent_start("Researcher Agent", "Phân tích hồ sơ độc giả và nhu cầu tự học chủ động")
    llm = create_llm(MODEL_RESEARCHER_AGENT, config=config, streaming=True)
    
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
        
    p_name = extract_field("Họ tên", user_profile_raw) or extract_field("Họ và tên", user_profile_raw)
    p_mssv = extract_field("MSSV", user_profile_raw) or extract_field("Mã số sinh viên", user_profile_raw)
    p_major = extract_field("Ngành", user_profile_raw) or extract_field("Ngành học", user_profile_raw)
    p_school = extract_field("Trường", user_profile_raw) or extract_field("Trường thành viên", user_profile_raw)
    p_style = extract_field("Phong cách", user_profile_raw) or extract_field("Phong cách học", user_profile_raw)
    
    p_name_val = p_name if p_name else "(Không cung cấp)"
    p_mssv_val = p_mssv if p_mssv else "(Không cung cấp)"
    p_major_val = p_major if p_major else "(Không cung cấp)"
    p_school_val = p_school if p_school else "(Không cung cấp)"
    p_style_val = p_style if p_style else "(Không cung cấp)"

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
    - Phong cách tư duy: {p_style_val}
    - Lĩnh vực đặc biệt quan tâm: [Phân tích lĩnh vực đặc biệt quan tâm dựa trên thông tin hồ sơ và chủ đề truy vấn "{topic}"]
    """
    
    res = await llm.ainvoke(prompt, config=call_config)
    parsed = parse_agent_json(res.content, "detailed_report")
    
    tokens = len(res.content) // 4
    duration = time.time() - start_time
    print_agent_complete("Researcher Agent", duration, tokens)
    actual_model = get_actual_model_used("profiler", MODEL_RESEARCHER_AGENT)
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
