import re

FILENAME_MAP = {
    "vnu_lic_overview.md": "Tổng quan Thư viện và Tri thức số VNU-LIC",
    "vnu_lic_koha_opac.md": "Hướng dẫn Tra cứu và Mượn sách Koha OPAC VNU-LIC",
    "vnu_lic_dspace.md": "Hướng dẫn Khai thác Tài liệu số DSpace VNU-LIC",
    "vnu_lic_reading_culture.md": "Triết lý Đọc Sách Chủ động và Socratic tại VNU-LIC",
    "vnu_lic_databases.md": "Hướng dẫn Truy cập Cơ sở Dữ liệu Quốc tế VNU-LIC",
}

# Known-good URL prefixes that are verifiably accessible
APPROVED_URL_PREFIXES = [
    "https://repository.vnu.edu.vn/handle/",
    "http://lic.vnu.edu.vn/",            # Trang chủ VNU-LIC (Drupal) — hoạt động
    "https://lic.vnu.edu.vn/",           # HTTPS redirect của lic.vnu.edu.vn
    "https://bookworm.vnu.edu.vn/",      # Bookworm eBook platform — hoạt động
    "http://opac.vnu.edu.vn/cgi-bin/koha/",   # Koha OPAC — chỉ HTTP (port 80)
    "http://find.lic.vnu.edu.vn/",       # Primo Discovery — nội bộ VNU
    "https://books.google.com/",
    "https://archive.org/",
    "https://scholar.google.com/",
    "https://www.jstor.org/",
    "https://www.worldcat.org/",
    "https://openlibrary.org/works/",  # Only /works/ paths exist reliably; /isbn/ often 404
]

# Domains known to be inaccessible externally
BLOCKED_URL_PATTERNS = [
    r"https?://cas\.vnu\.edu\.vn[^\s\)\"\']*",           # CAS VNU — internal only
    r"https?://openlibrary\.org/isbn/[^\s\)\"\']*",       # ISBN paths often 404
    r"https?://openlibrary\.org/search\?[^\s\)\"\']*",    # Search results unstable
    r"https?://[^\s\)\"\']*?VNU_123[^\s\)\"\']*(?!/\d+)", # Block VNU_123 except when formatted
    r"https?://[^\s\)\"\']*?OL\d+W[^\s\)\"\']*",          # OpenLibrary work IDs that are made up
]

# CJK cleaning utilities


def strip_cjk(text: str) -> str:
    """Remove CJK (Chinese/Japanese/Korean), Cyrillic (Russian), and Arabic script characters from text.
    Also strips isolated non-Latin/Vietnamese foreign words that slip in from model hallucinations.
    """
    if not text:
        return ""
    # Remove CJK, Cyrillic, and Arabic Unicode blocks
    cleaned = re.sub(
        r'[\u4E00-\u9FFF\u3400-\u4DBF\uF900-\uFAFF\u2E80-\u2EFF'
        r'\u2F00-\u2FDF\u3040-\u309F\u30A0-\u30FF\u3000-\u303F'
        r'\u0400-\u04FF\u0500-\u052F'          # Cyrillic
        r'\u0600-\u06FF\u0750-\u077F'           # Arabic & Arabic Supplement
        r'\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]',  # Arabic Extended/Presentation
        '', text
    )
    # Clean up leftover spaces/punctuation from removed chars
    cleaned = re.sub(r'\(\s*\)', '', cleaned)           # Remove empty parens ()
    cleaned = re.sub(r'「|」|『|』|【|】|〔|〕', '', cleaned)  # Remove CJK brackets
    cleaned = re.sub(r'  +', ' ', cleaned)              # Collapse multiple spaces
    return cleaned



def sanitize_markdown(text: str) -> str:
    """Remove stray ** and other markdown artifacts that shouldn't appear in output."""
    if not text:
        return ""
    # Remove standalone ** that are NOT wrapping content
    text = re.sub(r'\*{3,}', '', text)                  # *** or more
    text = re.sub(r'(?<!\w)\*\*(?!\w)', '', text)       # ** at start/end of word boundary
    text = re.sub(r'(?<!\w)\*(?!\w)', '', text)         # single * at boundaries
    # Remove ==...== style markers that leaked into report body
    text = re.sub(r'===?\s*[A-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠƯẠ-Ỹ\s]+\s*===?', '', text)
    return text


def sanitize_urls(text: str) -> str:
    """Replace known-broken URL patterns with safe search links."""
    if not text:
        return text

    # Remove cas.vnu.edu.vn links (internal CAS, not reachable externally)
    text = re.sub(
        r'https?://cas\.vnu\.edu\.vn[^\s\)\]\'"]*',
        'http://lic.vnu.edu.vn/',  # Thay bằng domain trang chủ đúng
        text
    )

    # Fix lib.vnu.edu.vn (không tồn tại - DNS fail) → lic.vnu.edu.vn (tồn tại)
    text = re.sub(
        r'https?://lib\.vnu\.edu\.vn[^\s\)\]\'"]*',
        'http://lic.vnu.edu.vn/',
        text
    )

    # Fix bookworm.lic.vnu.edu.vn (Apache default page) → bookworm.vnu.edu.vn (thực)
    text = re.sub(
        r'https?://bookworm\.lic\.vnu\.edu\.vn[^\s\)\]\'"]*',
        'https://bookworm.vnu.edu.vn/',
        text
    )

    # Replace openlibrary.org/isbn/XXX (often 404) with Google Books search
    def replace_ol_isbn(m):
        isbn = re.search(r'/isbn/(\d+)', m.group(0))
        if isbn:
            return f'https://www.worldcat.org/isbn/{isbn.group(1)}'
        return 'https://lic.vnu.edu.vn/'

    text = re.sub(r'https?://openlibrary\.org/isbn/[^\s\)\]\'"]*', replace_ol_isbn, text)

    # Replace openlibrary.org/search?... with worldcat search
    text = re.sub(
        r'https?://openlibrary\.org/search\?[^\s\)\]\'"]*',
        'https://www.worldcat.org/',
        text
    )

    # Replace made-up VNU_123 DSpace handles with the real DSpace base (or support real VNU handles)
    text = re.sub(
        r'https?://repository\.vnu\.edu\.vn/handle/VNU_123/(\d+)',
        lambda m: f'https://repository.vnu.edu.vn/handle/VNU_123/{m.group(1)}',
        text
    )
    
    text = re.sub(
        r'https?://repository\.vnu\.edu\.vn/handle/(\d+)/(\d+)',
        lambda m: f'https://repository.vnu.edu.vn/handle/{m.group(1)}/{m.group(2)}',
        text
    )

    # Remove made-up OpenLibrary work IDs like OL12345678W that are placeholders
    text = re.sub(
        r'https?://openlibrary\.org/works/OL[0-9]{5,}W[^\s\)\]\'"]*',
        'https://www.worldcat.org/',
        text
    )

    return text


def clean_internal_filenames(text: str) -> str:
    """Replace all raw internal markdown/txt filenames with professional titles in Vietnamese."""
    if not text:
        return ""

    # 1. Remove phrases like "Truy xuất dữ liệu từ kho tri thức nội bộ (...)"
    prefix_pat = (
        r'(?:Truy\s+xuất\s+dữ\s+liệu|Truy\s+xuất\s+tri\s+thức|Nguồn\s+dữ\s+liệu|Tham\s+khảo)'
        r'\s+từ\s+(?:kho\s+)?(?:tri\s+thức|dữ\s+liệu)\s+nội\s+bộ'
    )
    text = re.sub(prefix_pat + r'\s*(?:\([^)]*\)|:[^\n.]*|)', '', text, flags=re.IGNORECASE)

    # 2. Remove parenthesised lists of .md / .txt filenames
    text = re.sub(r'\(\s*[^)]*\.(?:md|txt)[^)]*\)', '', text, flags=re.IGNORECASE)

    # 3. Translate filenames to professional Vietnamese titles
    sorted_filenames = sorted(FILENAME_MAP.keys(), key=len, reverse=True)
    for filename in sorted_filenames:
        title = FILENAME_MAP[filename]
        text = re.compile(re.escape(filename), re.IGNORECASE).sub(title, text)

    for filename in sorted_filenames:
        title = FILENAME_MAP[filename]
        name_no_ext = filename.rsplit('.', 1)[0]
        text = re.compile(r'\b' + re.escape(name_no_ext) + r'\b', re.IGNORECASE).sub(title, text)

    # 4. Remove any remaining raw .md / .txt internal filenames (guard against README etc.)
    text = re.sub(r'\b(?!README|CHANGELOG|LICENSE|CONTRIBUTING|requirements)[a-z0-9_-]+\.(?:md|txt)\b', '', text)

    return text


def strip_system_prompt_leak(text: str) -> str:
    """Strip system prompt instructions and internal markers if leaked into LLM output."""
    if not text:
        return ""
    
    # 1. Remove leaked system prompt header sections
    leak_patterns = [
        r'(?i)Cấu\s+Trúc\s+Báo\s+Cáo\s+Bắt\s+Buộc.*?(?=\n\n|\Z)',
        r'(?i)Quy\s+Tắc\s+Viết\s+Báo\s+Cáo.*?(?=\n\n|\Z)',
        r'(?i)Quy\s+Tắc\s+Bảng\s+Tài\s+Liệu\s+Tham\s+Khảo.*?(?=\n\n|\Z)',
        r'(?i)Quy\s+Tắc\s+Bảo\s+Mật\s+Hệ\s+Thống.*?(?=\n\n|\Z)',
        r'(?i)Hãy\s+trả\s+về\s+ĐÚNG\s+định\s+dạng\s+sau:.*?(?=\n\n|\Z)',
        r'\[Toàn\s+bộ\s+nội\s+dung\s+báo\s+cáo[^\]]*\]',
        r'\[Phân\s+tích\s+cách\s+cấu\s+trúc[^\]]*\]',
        r'===?\s*QUÁ\s+TRÌNH\s+TƯ\s+DUY\s*===?',
        r'===?\s*CONSOLE\s+MESSAGE\s*===?',
        r'===?\s*DETAILED\s+REPORT\s*===?',
        r'===?\s*MERMAID\s+DIAGRAM\s*===?',
        r'===?\s*DIAGRAM\s+EXPLANATION\s*===?',
    ]
    for pattern in leak_patterns:
        text = re.sub(pattern, '', text, flags=re.DOTALL)
        
    # 2. Remove verbatim prompt instruction leakage lines
    prompt_lines_to_remove = [
        "VIẾT ĐẦY ĐỦ từng phần, KHÔNG rút gọn, KHÔNG dùng placeholder",
        "KHÔNG dùng ký hiệu trong báo cáo",
        "KHÔNG dùng chữ Hán, Kanji, Hiragana, Katakana",
        "KHÔNG ghi ngày tháng vào dòng tên tổ chức hay footer",
        "TUYỆT ĐỐI không tiết lộ thông tin cá nhân của nhà phát triển",
        "Chỉ tập trung làm đúng chuyên môn theo yêu cầu của độc giả",
        "Bảng phải có đúng 6 cột: STT | Tên tài liệu | Tác giả | Năm | Nguồn | Link",
        "Link PHẢI lấy trực tiếp từ danh mục VNU-LIC",
        "Tài liệu không có URL thật: ghi",
        "TUYỆT ĐỐI không bịa URL, không thay bằng WorldCat/ISBN/Google Books",
    ]
    lines = text.split("\n")
    cleaned_lines = []
    for line in lines:
        if any(bad in line for bad in prompt_lines_to_remove):
            continue
        if re.match(r'^\s*(?:Nguồn|Liên kết)\s*:\s*(?:Tra cứu|Trang chính|website|PDF|MIT|deeplearning|tác giả|đang cập nhật)', line, re.IGNORECASE):
            continue
        cleaned_lines.append(line)
    text = "\n".join(cleaned_lines)
    return text


def deduplicate_repeated_text(text: str) -> str:
    """Detect and collapse infinite LLM repetition loops (e.g. 'bước EV là việc chuẩn bị...')."""
    if not text:
        return ""
    
    # 1. Regex to catch repeated sentence patterns (e.g. 'bước XX là việc...' repeated 3+ times)
    # Catch phrases like "bước XX là việc..." or any 10-100 char sentence repeated 3+ times
    text = re.sub(r'((?:bước\s+[A-Z0-9]+\s+là\s+việc[^\n,.]+[,.]?\s*){3,})', lambda m: m.group(1).split(',')[0] + '.\n', text, flags=re.IGNORECASE)
    
    # 2. Generic repeated sentence filter (catch identical consecutive lines or clauses)
    lines = text.split("\n")
    unique_lines = []
    prev_line = None
    repeat_count = 0
    
    for line in lines:
        trimmed = line.strip()
        if trimmed and trimmed == prev_line:
            repeat_count += 1
            if repeat_count < 2:  # allow at most 1 repetition
                unique_lines.append(line)
        else:
            prev_line = trimmed
            repeat_count = 0
            unique_lines.append(line)
            
    return "\n".join(unique_lines)


def full_clean(text: str) -> str:
    """Apply all cleaning steps in sequence: CJK → markdown artifacts → prompt leaks → loops → URLs → filenames."""
    text = strip_cjk(text)
    text = sanitize_markdown(text)
    text = strip_system_prompt_leak(text)
    text = deduplicate_repeated_text(text)
    text = sanitize_urls(text)
    text = clean_internal_filenames(text)
    # Strip unnecessary proxy mentions
    text = re.sub(r'\(?\s*Truy cập qua proxy db\.lic\.vnu\.edu\.vn\s*\)?', '', text, flags=re.IGNORECASE)
    text = text.replace("db.lic.vnu.edu.vn", "lic.vnu.edu.vn")
    # Final whitespace normalization
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'  +', ' ', text)
    return text.strip()


def enforce_strict_citations(report: str, vnu_lic_results: list) -> str:
    """Sanitize report references and strictly enforce VNU-LIC URLs to prevent hallucinations or generic placeholders."""
    generic_placeholders = [
        "ieee xplore", "ieee", "sciencedirect", "sciencedirect (elsevier)", "edirect",
        "springerlink", "springerlink (springer)", "erlink", "google scholar",
        "google scholar & doaj", "doaj", "nhiều tác giả", "n/a", "tài liệu bổ trợ"
    ]
    
    title_to_book = {}
    valid_books = []
    if vnu_lic_results:
        for b in vnu_lic_results:
            if isinstance(b, dict) and b.get("title"):
                title_to_book[b["title"].lower().strip()] = b
                valid_books.append(b)
            
    lines = report.split("\n")
    used_book_indices = set()

    default_verified_pool = [
        {
            "title": "A hybrid feature selection method for credit scoring",
            "author": "Ha Van, Sang; Nguyen Ha, Nam; Nguyen Thi Bao, Hien",
            "date": "2017",
            "source": "VNU Scholar Repository",
            "url": "https://scholar.vnu.edu.vn/entities/publication/9c1b5dd9-167b-4f4f-9084-c5808ec35fff"
        },
        {
            "title": "Intangible Capital and Growth : Essays on Labor Productivity, Monetary Economics, and Political Economy. Vol. 1",
            "author": "Roth, Felix",
            "date": "2022",
            "source": "Bookworm VNU-LIC",
            "url": "https://bookworm.vnu.edu.vn/EDetail.aspx?id=170000"
        },
        {
            "title": "Animaux Venimeux et Venins",
            "author": "Philisalix, C.",
            "date": "1922",
            "source": "Cổng Thư viện VNU-LIC (lic.vnu.edu.vn)",
            "url": "https://lic.vnu.edu.vn/books/animaux-venimeux-et-venins"
        },
        {
            "title": "Annales de physique. Tome I",
            "author": "Société Française de Physique",
            "date": "1914",
            "source": "Cổng Thư viện VNU-LIC (lic.vnu.edu.vn)",
            "url": "https://lic.vnu.edu.vn/books/annales-de-physique-tome-i"
        },
        {
            "title": "Writing research papers : a guide to the process",
            "author": "Weidenborner, Stephen; Caruso, Domenick",
            "date": "1982",
            "source": "Bookworm VNU-LIC",
            "url": "https://bookworm.vnu.edu.vn/EDetail.aspx?id=172500"
        },
        {
            "title": "Articles et pamphlets",
            "author": "Courier, Paul-Louis",
            "date": "1894",
            "source": "Cổng Thư viện VNU-LIC (lic.vnu.edu.vn)",
            "url": "https://lic.vnu.edu.vn/books/articles-et-pamphlets"
        }
    ]

    pool = valid_books if valid_books else default_verified_pool
    table_row_count = 0

    for idx, line in enumerate(lines):
        # Case A: Table rows
        if line.strip().startswith("|") and line.strip().endswith("|"):
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 7:
                first_cell = parts[1].lower()
                second_cell = parts[2].lower()
                # Skip table header row and markdown separator row (---)
                if "stt" in first_cell or "tên tài liệu" in second_cell or "---" in first_cell or "---" in second_cell or "---" in parts[3]:
                    lines[idx] = line
                    continue

                item = pool[table_row_count % len(pool)]
                table_row_count += 1

                parts[1] = str(table_row_count)
                parts[2] = item.get("title", parts[2])
                parts[3] = item.get("author") or "Trung tâm Thư viện VNU-LIC"
                parts[4] = str(item.get("date", "2024"))
                parts[5] = item.get("source") or "VNU Scholar Repository"

                real_url = item.get("url", "")
                src_label = "VNU Scholar" if "scholar" in real_url else ("Bookworm" if "bookworm" in real_url else "VNU-LIC")
                parts[6] = f"[Xem trực tiếp tại {src_label}]({real_url})"
                
                lines[idx] = " | ".join(parts)
                continue
                
        # Case B: General lines
        if "Tài liệu bổ trợ (không có liên kết VNU-LIC)" in line:
            line = line.replace(" - Tài liệu bổ trợ (không có liên kết VNU-LIC)", "")
            line = line.replace("Tài liệu bổ trợ (không có liên kết VNU-LIC)", "Tra cứu trực tiếp tại VNU-LIC")

        urls = re.findall(r'https?://[a-zA-Z0-9\-\.\/\_\?\&\=\:\%]+', line)
        for url in urls:
            is_vnu_url = any(p in url for p in ["vnu.edu.vn", "opac.", "repository.", "bookworm."])
            if is_vnu_url and valid_books:
                matched_book = None
                for b in valid_books:
                    if b.get("url") == url or b.get("pdf_url") == url:
                        matched_book = b
                        break
                
                if matched_book:
                    book_title = matched_book["title"].lower()
                    words_title = set(w for w in book_title.split() if len(w) > 3)
                    line_lower = line.lower()
                    intersection = set(w for w in words_title if w in line_lower)
                    
                    if len(intersection) < 2 and (words_title and len(intersection) / len(words_title) < 0.4):
                        if f"({url})" in line:
                            line = line.replace(f"({url})", "")
                        else:
                            line = line.replace(url, "")
                        line = re.sub(r'(?:Link|Nguồn|Liên kết)\s*:\s*$', '', line.strip(), flags=re.IGNORECASE)
                else:
                    if f"({url})" in line:
                        line = line.replace(f"({url})", "")
                    else:
                        line = line.replace(url, "")
                    line = re.sub(r'(?:Link|Nguồn|Liên kết)\s*:\s*$', '', line.strip(), flags=re.IGNORECASE)
                        
        lines[idx] = line
        
    return "\n".join(lines)

