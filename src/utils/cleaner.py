import re

FILENAME_MAP = {
    "agentvista_testvista.md": "Tài liệu Khảo sát AgentVista & TestVista",
    "ai_first_challenges.md": "Báo cáo Thách thức Chiến lược AI-First",
    "codevista_features.md": "Tài liệu Tính năng CodeVista",
    "coding_standards.md": "Quy chuẩn Phát triển Phần mềm FPT Software",
    "flezi_foundry_adlc.md": "Báo cáo Quy trình Vận hành Flezi Foundry ADLC",
    "flezipt_architecture.md": "Kiến trúc Nền tảng Flezi Platform (FlezIPT)",
    "fpt_academic_publications.md": "Các Công trình Nghiên cứu Khoa học FPT Software",
    "fpt_agentic_ai_2026.md": "Báo cáo Phát triển Agentic AI FPT Software 2026",
    "fpt_ai_initiatives_2026.md": "Sáng kiến Chiến lược AI FPT Software 2026",
    "fpt_ai_research_lab_2026.md": "Tài liệu Phòng Nghiên cứu Trí tuệ Nhân tạo FPT AI Research Lab",
    "fpt_ai_strategy_advisory_2026.md": "Báo cáo Tư vấn Chiến lược AI FPT Software 2026",
    "fpt_architecture_consulting_2026.md": "Quy trình Tư vấn Kiến trúc Công nghệ FPT Software 2026",
    "fpt_enterprise_products_2026.md": "Danh mục Sản phẩm Doanh nghiệp FPT Software 2026",
    "fpt_financial_growth_2026.md": "Báo cáo Phát triển Tài chính FPT Software 2026",
    "fpt_flezi_ecosystem.md": "Tài liệu Hệ sinh thái Flezi Ecosystem FPT",
    "fpt_global_presence_2026.md": "Báo cáo Năng lực Toàn cầu FPT Software 2026",
    "fpt_global_verticals_2026.md": "Tài liệu Lĩnh vực Kinh doanh Toàn cầu FPT Software 2026",
    "fpt_research.md": "Báo cáo Nghiên cứu và Phát triển Công nghệ FPT Software",
    "fpt_risk_compliance_2026.md": "Tài liệu Quản trị Rủi ro & Tuân thủ FPT Software 2026",
    "fpt_software_overview_2026.md": "Tài liệu Tổng quan FPT Software 2026",
    "sdlc_evolution.md": "Tài liệu Tiến trình Phát triển Phần mềm SDLC FPT",
    "security_best_practices.md": "Quy chuẩn Bảo mật Thông tin FPT Software",
}

def clean_internal_filenames(text: str) -> str:
    """Replace all raw internal markdown/txt filenames with professional titles in Vietnamese."""
    if not text:
        return ""
    
    # 1. Remove phrases like "Truy xuất dữ liệu từ kho tri thức nội bộ (file1.md, file2.md...)" or with translated names
    # Match the prefix and any list of .md/.txt files or translated names in parentheses
    prefix_pat = r'(?:Truy\s+xuất\s+dữ\s+liệu|Truy\s+xuất\s+tri\s+thức|Nguồn\s+dữ\s+liệu|Tham\s+khảo)\s+từ\s+(?:kho\s+)?(?:tri\s+thức|dữ\s+liệu)\s+nội\s+bộ'
    
    # Remove things like "Truy xuất dữ liệu từ kho tri thức nội bộ (flezipt_architecture.md, ...)"
    # or "Truy xuất dữ liệu từ kho tri thức nội bộ: flezipt_architecture.md, ..."
    text = re.sub(prefix_pat + r'\s*(?:\([^)]*\)|:[^\n.]*|)', '', text, flags=re.IGNORECASE)
    
    # Also look for standalone lists of filenames in parentheses, e.g. (flezipt_architecture.md, ai_first_challenges.md)
    # We can match parentheses containing .md or .txt files and remove the entire parenthesis block
    text = re.sub(r'\(\s*[^)]*\.(?:md|txt)[^)]*\)', '', text, flags=re.IGNORECASE)
    
    # 2. Translate filenames if any standalone mentions remain, though agents are instructed not to output them
    sorted_filenames = sorted(FILENAME_MAP.keys(), key=len, reverse=True)
    for filename in sorted_filenames:
        title = FILENAME_MAP[filename]
        pattern = re.compile(re.escape(filename), re.IGNORECASE)
        text = pattern.sub(title, text)
        
    for filename in sorted_filenames:
        title = FILENAME_MAP[filename]
        name_no_ext = filename.rsplit('.', 1)[0]
        pattern = re.compile(r'\b' + re.escape(name_no_ext) + r'\b', re.IGNORECASE)
        text = pattern.sub(title, text)
        
    # Double check if any raw markdown extension files leak (chỉ khớp tên file nội bộ đã biết, không khớp URL hay README.md hợp lệ)
    text = re.sub(r'\b(?!README|CHANGELOG|LICENSE|CONTRIBUTING|requirements)[a-z0-9_-]+\.(?:md|txt)\b', '', text)
    
    return text
