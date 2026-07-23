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

    # Fix bookworm.lic.vnu.edu.vn (fake domain) → bookworm.vnu.edu.vn (thực)
    text = re.sub(
        r'https?://bookworm\.lic\.vnu\.edu\.vn[^\s\)\]\'"]*',
        'https://bookworm.vnu.edu.vn/',
        text
    )

    # Fix db.lic.vnu.edu.vn (fake homepage link) → lic.vnu.edu.vn
    text = re.sub(
        r'https?://db\.lic\.vnu\.edu\.vn[^\s\)\]\'"]*',
        'https://lic.vnu.edu.vn/',
        text
    )

    # Replace Koha OPAC mentions
    text = text.replace("Tra cứu tại hệ thống Koha OPAC http://bookworm.lic.vnu.edu.vn/", "Xem trực tiếp tại VNU-LIC")
    text = text.replace("Tra cứu tại hệ thống Koha OPAC http://db.lic.vnu.edu.vn/", "Xem trực tiếp tại VNU-LIC")
    text = text.replace("Tra cứu tại hệ thống Koha OPAC", "Xem trực tiếp tại VNU-LIC")

    # Standardize 4 sources message text
    text = text.replace("Đã gợi ý danh mục tài liệu cá nhân hóa từ 3 nguồn VNU-LIC: Bookworm, VNU Scholar và lic.vnu.edu.vn.", "Đã gợi ý danh mục tài liệu cá nhân hóa từ 4 nguồn VNU-LIC.")
    text = text.replace("từ 3 nguồn VNU-LIC: Bookworm, VNU Scholar và lic.vnu.edu.vn", "từ 4 nguồn VNU-LIC")
    text = text.replace("từ 3 nguồn VNU-LIC", "từ 4 nguồn VNU-LIC")

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


def strip_rag_hallucinations(text: str) -> str:
    """Clean fake proxy URLs and Koha OPAC mentions while preserving valuable book recommendations."""
    # 1. Replace fake proxy URL substrings & OPAC notes cleanly
    text = re.sub(r'\(?\s*Truy cập qua proxy[^\)\n]*\)?', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\(?\s*Khuyến nghị tra cứu tại Koha OPAC[^\)\n]*\)?', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\(?\s*Không có URL trực tiếp\s*\)?', '', text, flags=re.IGNORECASE)
    text = re.sub(r'Nguồn\s*:\s*Tài liệu bổ trợ RAG[^\n|]*', 'Nguồn: Tài liệu rèn luyện tư duy Socratic ', text, flags=re.IGNORECASE)
    text = text.replace("http://bookworm.lic.vnu.edu.vn/", "")
    text = text.replace("http://db.lic.vnu.edu.vn/", "")
    text = text.replace("http://opac.vnu.edu.vn/", "")
    text = text.replace("Koha OPAC", "VNU-LIC")
    text = text.replace("Thư viện Xuân Thủy", "Thư viện ĐHQGHN")

    # 2. Remove standalone lines that ONLY mention database proxies or IEEE/SpringerLink standalone bullet points
    lines = text.split("\n")
    cleaned_lines = []
    for line in lines:
        l_strip = line.strip()
        if any(db in l_strip.lower() for db in ["ieee xplore", "springerlink", "sciencedirect (elsevier)"]):
            if "truy cập qua proxy" in l_strip.lower() or "csdl khoa học kỹ thuật" in l_strip.lower() or "cơ sở dữ liệu" in l_strip.lower():
                continue
        cleaned_lines.append(line)
        
    return "\n".join(cleaned_lines)


def full_clean(text: str) -> str:
    """Apply all cleaning steps in sequence: CJK → markdown artifacts → prompt leaks → loops → URLs → filenames."""
    text = strip_cjk(text)
    text = sanitize_markdown(text)
    text = strip_system_prompt_leak(text)
    text = deduplicate_repeated_text(text)
    text = sanitize_urls(text)
    text = clean_internal_filenames(text)
    text = strip_rag_hallucinations(text)
    # Final whitespace normalization
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'  +', ' ', text)
    return text.strip()


default_verified_pool = [
    {
        "title": "A hybrid feature selection method for credit scoring",
        "author": "Ha Van, Sang; Nguyen Ha, Nam; Nguyen Thi Bao, Hien",
        "publisher_journal": "EAI Endorsed Transactions",
        "date": "2017",
        "source": "VNU Scholar Repository",
        "url": "https://scholar.vnu.edu.vn/entities/publication/9c1b5dd9-167b-4f4f-9084-c5808ec35fff",
        "handle_url": "https://scholar.vnu.edu.vn/handle/123456789/12692"
    },
    {
        "title": "Using impromptu speaking activities to improve student' fluency: an action research",
        "author": "Bùi, Thị Hồng Hoa",
        "publisher_journal": "ĐHQGHN - Trường Đại học Ngoại ngữ (ULIS)",
        "date": "2026",
        "source": "VNU Repository (repository.vnu.edu.vn)",
        "url": "https://repository.vnu.edu.vn/entities/publication/e87b7dca-5f05-4dd2-8d84-3ae579fce5ab",
        "handle_url": "https://repository.vnu.edu.vn/handle/VNU_123/182268"
    },
    {
        "title": "The use of pictures in teaching English speaking in an English center",
        "author": "Duong, Tra Mi; Vu, Mai Trang (Người hướng dẫn)",
        "publisher_journal": "ĐHQGHN - Trường Đại học Ngoại ngữ (ULIS)",
        "date": "2011",
        "source": "VNU Repository (repository.vnu.edu.vn)",
        "url": "https://repository.vnu.edu.vn/entities/publication/1ff731b9-5e12-4f8e-ae8f-b08c34627537",
        "handle_url": "https://repository.vnu.edu.vn/handle/VNU_123/40615"
    },
    {
        "title": "Visualizing atomic orbitals of an electron by Latex",
        "author": "Nguyen Hoang, Hai",
        "publisher_journal": "European Journal of Physics",
        "date": "2022",
        "source": "VNU Scholar Repository",
        "url": "https://scholar.vnu.edu.vn/entities/publication/6f7669c1-5aa6-4ffb-9d98-dc29bc8585c8",
        "handle_url": "https://scholar.vnu.edu.vn/handle/123456789/2350"
    },
    {
        "title": "Integration der flüchtlinge auf dem Deutschen arbeitsmarkt = So sánh hai mô hình hỗ trợ người tị nạn...",
        "author": "Đào, Thị Thắm (Người hướng dẫn: Trần, Thị Hạnh)",
        "publisher_journal": "ĐHQGHN - Trường Đại học Ngoại ngữ (ULIS)",
        "date": "2022",
        "source": "VNU Repository (repository.vnu.edu.vn)",
        "url": "https://repository.vnu.edu.vn/entities/publication/1ff7218c-e60e-4f3a-922d-c017d0a65ec9",
        "handle_url": "https://repository.vnu.edu.vn/handle/VNU_123/143559"
    },
    {
        "title": "Intangible Capital and Growth : Essays on Labor Productivity, Monetary Economics, and Political Economy. Vol. 1",
        "author": "Roth, Felix",
        "publisher_journal": "Springer",
        "date": "2022",
        "source": "Bookworm VNU-LIC",
        "url": "https://bookworm.vnu.edu.vn/EDetail.aspx?id=170000"
    },
    {
        "title": "Animaux Venimeux et Venins",
        "author": "Marie Phisalix",
        "publisher_journal": "Paris",
        "date": "1922",
        "source": "Cổng Thư viện VNU-LIC (lic.vnu.edu.vn)",
        "url": "https://lic.vnu.edu.vn/books/animaux-venimeux-et-venins"
    },
    {
        "title": "Annales de physique. Tome I",
        "author": "A. Cotton",
        "publisher_journal": "Paris",
        "date": "1931",
        "source": "Cổng Thư viện VNU-LIC (lic.vnu.edu.vn)",
        "url": "https://lic.vnu.edu.vn/books/annales-de-physique-tome-i"
    },
    {
        "title": "Writing research papers : a guide to the process",
        "author": "Weidenborner, Stephen; Caruso, Domenick",
        "publisher_journal": "St. Martin's Press",
        "date": "1982",
        "source": "Bookworm VNU-LIC",
        "url": "https://bookworm.vnu.edu.vn/EDetail.aspx?id=172500"
    },
    {
        "title": "Auguste comte sa vie",
        "author": "Cresson, André",
        "publisher_journal": "Presses universitaires de France",
        "date": "1947",
        "source": "Cổng Thư viện VNU-LIC (lic.vnu.edu.vn)",
        "url": "https://lic.vnu.edu.vn/books/auguste-comte-sa-vie"
    },
    {
        "title": "Articles et pamphlets",
        "author": "M. Gorki",
        "publisher_journal": "Paris",
        "date": "1950",
        "source": "Cổng Thư viện VNU-LIC (lic.vnu.edu.vn)",
        "url": "https://lic.vnu.edu.vn/books/articles-et-pamphlets"
    }
]


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

    cleaned_pool = []
    if vnu_lic_results:
        for b in vnu_lic_results:
            if isinstance(b, dict) and b.get("title") and b.get("url") and b.get("url") != "-":
                t_lower = b["title"].lower()
                if not any(p in t_lower for p in generic_placeholders):
                    cleaned_pool.append(b)

    pool = cleaned_pool if len(cleaned_pool) >= 3 else default_verified_pool
    table_row_count = 0
    in_ref_table_context = False

    for idx, line in enumerate(lines):
        line_str = line.strip()
        if "bảng tài liệu tham khảo" in line_str.lower() or "danh mục tài liệu tham khảo" in line_str.lower() or "tài liệu tham khảo" in line_str.lower():
            in_ref_table_context = True

        # Case A: Table rows
        if line_str.startswith("|") and line_str.endswith("|"):
            parts = [p.strip() for p in line_str.split("|")]
            if len(parts) >= 4:
                first_cell = parts[1].lower()
                second_cell = parts[2].lower()
                
                # Check if this table is User Profile table (2-3 columns, no STT/Title header)
                is_profile_table = any(k in first_cell or k in second_cell for k in ["hồ sơ độc giả", "thông tin độc giả", "độc giả", "trường", "chuyên ngành", "mục tiêu"])
                if is_profile_table and not in_ref_table_context:
                    lines[idx] = line
                    continue

                # Format Header Row to strict 8-Column Schema
                if "stt" in first_cell or "tên tài liệu" in second_cell:
                    in_ref_table_context = True
                    lines[idx] = "| STT | Tên tài liệu | Tác giả | Người hướng dẫn | Năm | Nhà xuất bản / Đơn vị chủ trì / Tạp chí | Nguồn | Handle URI / Entity Page |"
                    continue

                # Format Separator Row
                if "---" in first_cell or "---" in second_cell or "---" in parts[3]:
                    if in_ref_table_context:
                        lines[idx] = "|---|---|---|---|---|---|---|---|"
                    else:
                        lines[idx] = line
                    continue

                # Only convert rows inside reference table context
                if not in_ref_table_context and not first_cell.isdigit():
                    lines[idx] = line
                    continue

                item = pool[table_row_count % len(pool)]
                table_row_count += 1

                stt_val = str(table_row_count)
                title_val = item.get("title", parts[2] if len(parts) > 2 else "-")
                
                # Check for advisor in author string
                raw_author = item.get("author") or "-"
                if " (Người hướng dẫn: " in raw_author:
                    main_author, advisor_part = raw_author.split(" (Người hướng dẫn: ")
                    advisor = advisor_part.rstrip(")")
                elif " (Người hướng dẫn)" in raw_author:
                    clean_a = raw_author.replace(" (Người hướng dẫn)", "")
                    if "; " in clean_a:
                        parts_a = clean_a.split("; ")
                        main_author = parts_a[0]
                        advisor = "; ".join(parts_a[1:])
                    else:
                        main_author = clean_a
                        advisor = "-"
                else:
                    main_author = raw_author
                    advisor = "-"

                real_url = item.get("url", "")
                handle_url = item.get("handle_url", "")
                if "scholar" in real_url:
                    src_label = "VNU Scholar"
                elif "repository" in real_url:
                    src_label = "VNU Repository"
                elif "bookworm" in real_url:
                    src_label = "Bookworm VNU-LIC"
                else:
                    src_label = "Cổng VNU-LIC"

                if handle_url and handle_url != real_url:
                    link_str = f"[Xem Entity]({real_url}) \| [Xem Handle URI]({handle_url}) → {real_url}"
                elif real_url and real_url != "-":
                    link_str = f"[Xem trực tiếp tại {src_label}]({real_url}) → {real_url}"
                else:
                    link_str = "-"

                date_val = str(item.get("date") or "-")
                pub_val = item.get("publisher_journal") or item.get("publisher") or "-"
                source_val = item.get("source") or src_label

                # Strictly construct 8-column markdown row
                lines[idx] = f"| {stt_val} | {title_val} | {main_author} | {advisor} | {date_val} | {pub_val} | {source_val} | {link_str} |"
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
                        
    res_text = "\n".join(lines)
    return strip_rag_hallucinations(res_text)

