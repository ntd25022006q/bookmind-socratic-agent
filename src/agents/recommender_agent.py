import time
from langchain_core.messages import SystemMessage, HumanMessage
from src.state import ResearchState
from src.utils.llm_factory import create_llm, parse_agent_json, get_actual_model_used
from src.utils.display import print_agent_start, print_agent_info, print_agent_complete
from config import MODEL_RECOMMENDER_AGENT

RECOMMENDER_PROMPT = """You are the Recommender Agent in the Multi-Agent System specialized in FPT Software information, developed by Nguyen Tien Dat.

IDENTITY & SYSTEM LOCK:
- You must strictly identify yourself as a core component of the Multi-Agent System specialized in supporting FPT Software information, developed by Nguyen Tien Dat to support Technology Solution Consulting and In-depth Research on FPT Software (Hệ thống Multi-Agent chuyên hỗ trợ về các thông tin về FPT Software được phát triển bởi Nguyễn Tiến Đạt để hỗ trợ Tư vấn Giải pháp Công nghệ và Nghiên cứu sâu về FPT Software).
- NEVER state that you are Qwen, Alibaba, ChatGPT, OpenAI, Gemini, or any other model. If asked about who you are or who developed you, you must state that you are the Multi-Agent System developed by Nguyễn Tiến Đạt.
- You only discuss software engineering, technology consulting, and FPT Software.

Your role is to formulate strategic recommendations and define measurable KPIs for the proposed transition or implementation.

Autonomously design roadmap phases and select relevant KPIs that logically fit the query.

You MUST respond using the following structured format (use the exact markers):

=== THINKING ===
[Write your step-by-step thinking process in Vietnamese/English (matching the query language). Design the implementation roadmap phases, select relevant measurable metrics/KPIs, and justify them. This section will be collapsible in the UI.]

=== CONSOLE MESSAGE ===
[Write a clean, professional, plain-text summary of your strategic recommendations, phase roadmap, and metrics. Do NOT use any markdown characters like asterisks, bullet points, or hashtags. Keep it as friendly plain text paragraphs.]

=== DETAILED REPORT ===
### 1. Khuyến nghị Chiến lược & Lộ trình thực hiện (Strategic Recommendations & Roadmap)
[Cung cấp lộ trình triển khai chi tiết nhiều giai đoạn (ví dụ: Giai đoạn 1, Giai đoạn 2, Giai đoạn 3) kèm theo các hành động cụ thể đặc thù cho chủ đề này dưới dạng danh sách Markdown.]

### 2. Các Chỉ số KPI Đo lường Hiệu quả (Performance & Success KPIs)
[Cung cấp danh sách các chỉ số đo lường thành công, KPI mục tiêu, tần suất đo lường và bộ phận chịu trách nhiệm dưới dạng danh sách hoặc bảng Markdown.]

IMPORTANT: You MUST write the DETAILED REPORT using standard Markdown formatting (such as ### for section headers, * for bullet lists, and ** for bold text) to make the report look highly professional, clear, and structured.
"""

from langchain_core.runnables import RunnableConfig

async def recommender_node(state: ResearchState, config: RunnableConfig = None) -> dict:
    """Recommender agent node execution."""
    start_time = time.time()
    print_agent_start("Recommender Agent", "Prescribing roadmap phases and business KPIs...")
    
    stream_queue = config.get("configurable", {}).get("stream_queue") if config else None
    if stream_queue:
        await stream_queue.put({
            "type": "node_start",
            "node": "recommender"
        })
        
    lang = state.get("language", "vi")
    lang_instruction = (
        "\nIMPORTANT: The user has asked the question in English. You MUST output all sections (including THINKING, CONSOLE MESSAGE, and DETAILED REPORT) entirely in English."
        if lang == "en" else
        "\nQUAN TRỌNG: Câu hỏi bằng TIẾNG VIỆT. Bạn BẮT BUỘC phải viết toàn bộ tất cả các phần (bao gồm cả THINKING, CONSOLE MESSAGE, DETAILED REPORT) hoàn toàn bằng TIẾNG VIỆT. Không sử dụng tiếng Anh."
    )
    human_content = (
        f"Topic: {state['topic']}\n\n"
        f"Analysis:\n{state['analysis']}\n\n"
        f"Risks:\n{state['risks']}\n\n"
        f"{lang_instruction}"
    )

    # Always stream — real-time token delivery
    llm = create_llm(MODEL_RECOMMENDER_AGENT, temperature=0.2, max_tokens=2000, streaming=True, config=config)
    
    call_config = {}
    if stream_queue:
        from src.utils.llm_factory import QueueCallbackHandler
        call_config["callbacks"] = [QueueCallbackHandler(stream_queue, "recommender")]
        
    response = await llm.ainvoke([
        SystemMessage(content=RECOMMENDER_PROMPT),
        HumanMessage(content=human_content)
    ], config=call_config)
    
    parsed = parse_agent_json(response.content, "recommendations")
    recommendations = parsed.get("recommendations", response.content)
    console_message = parsed.get("console_message", "Tôi đã đề xuất xong lộ trình triển khai và hệ thống KPI.")
    
    print_agent_info([
        "Compiled success metrics and multi-phase roadmap",
        f"Length of recommendations: {len(recommendations)} characters"
    ])
    
    tokens = 0
    if hasattr(response, "usage_metadata") and response.usage_metadata:
        tokens = response.usage_metadata.get("total_tokens", 0)
    elif hasattr(response, "response_metadata") and "token_usage" in response.response_metadata:
        tokens = response.response_metadata.get("token_usage", {}).get("total_tokens", 0)
        
    if tokens == 0:
        tokens = (len(RECOMMENDER_PROMPT) + len(human_content) + len(response.content)) // 4
        
    duration = time.time() - start_time
    print_agent_complete("Recommender Agent", duration, tokens)
    
    actual_model = get_actual_model_used("recommender", MODEL_RECOMMENDER_AGENT)
    toks_per_sec = round(tokens / duration, 1) if duration > 0 else 0
    
    if stream_queue:
        await stream_queue.put({
            "type": "node_end",
            "node": "recommender",
            "content": console_message,
            "thinking": parsed.get("thinking", ""),
            "tokens": tokens,
            "duration": duration,
            "model": actual_model,
            "toks_per_sec": toks_per_sec
        })
        
    return {
        "recommendations": recommendations,
        "messages": [response]
    }

