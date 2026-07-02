import re

FILENAME_MAP = {
    "vnu_lic_overview.md": "Tổng quan Thư viện và Tri thức số VNU-LIC",
    "vnu_lic_koha_opac.md": "Hướng dẫn Tra cứu và Mượn sách Koha OPAC VNU-LIC",
    "vnu_lic_dspace.md": "Hướng dẫn Khai thác Tài liệu số DSpace VNU-LIC",
    "vnu_lic_reading_culture.md": "Triết lý Đọc Sách Chủ động và Socratic tại VNU-LIC",
    "vnu_lic_databases.md": "Hướng dẫn Truy cập Cơ sở Dữ liệu Quốc tế VNU-LIC",
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
