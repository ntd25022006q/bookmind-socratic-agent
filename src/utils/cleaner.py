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
    "https://lic.vnu.edu.vn/",
    "https://bookworm.vnu.edu.vn/",
    "https://bookworm.lic.vnu.edu.vn/",
    "https://opac.lic.vnu.edu.vn/cgi-bin/koha/",
    "http://opac.lic.vnu.edu.vn/cgi-bin/koha/",
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
    """Remove all CJK (Chinese/Japanese/Korean) characters from text."""
    if not text:
        return ""
    # Remove CJK characters using compiled pattern
    cleaned = re.sub(
        r'[\u4E00-\u9FFF\u3400-\u4DBF\uF900-\uFAFF\u2E80-\u2EFF'
        r'\u2F00-\u2FDF\u3040-\u309F\u30A0-\u30FF\u3000-\u303F]',
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
        'https://lic.vnu.edu.vn/',
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


def full_clean(text: str) -> str:
    """Apply all cleaning steps in sequence: CJK → markdown artifacts → URLs → filenames."""
    text = strip_cjk(text)
    text = sanitize_markdown(text)
    text = sanitize_urls(text)
    text = clean_internal_filenames(text)
    # Final whitespace normalization
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'  +', ' ', text)
    return text.strip()


def enforce_strict_citations(report: str, vnu_lic_results: list) -> str:
    """Sanitize report references and strictly enforce VNU-LIC URLs to prevent hallucinations."""
    if not vnu_lic_results:
        return report
    
    # Map from lowercase clean titles to correct book dicts
    title_to_book = {}
    for b in vnu_lic_results:
        if isinstance(b, dict) and b.get("title") and b.get("url"):
            title_to_book[b["title"].lower().strip()] = b
            
    lines = report.split("\n")
    for idx, line in enumerate(lines):
        # Case A: Table rows
        if line.strip().startswith("|") and line.strip().endswith("|"):
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 7:
                title_cell = parts[2].lower()
                link_cell = parts[6]
                
                matched_book = None
                for t, b in title_to_book.items():
                    if t in title_cell or title_cell in t:
                        matched_book = b
                        break
                    # Fuzzy match: shared significant words (>3 chars)
                    words_t = set(w for w in t.split() if len(w) > 3)
                    words_cell = set(w for w in title_cell.split() if len(w) > 3)
                    intersection = words_t.intersection(words_cell)
                    if len(intersection) >= 2 or (words_t and len(intersection) / len(words_t) >= 0.5):
                        matched_book = b
                        break
                
                if matched_book:
                    # Update all details to match the real book record exactly
                    parts[2] = matched_book.get("title", parts[2])
                    parts[3] = matched_book.get("author") or "Không rõ tác giả"
                    parts[4] = matched_book.get("date") or "2024"
                    parts[5] = matched_book.get("source") or "VNU-LIC"
                    
                    real_url = matched_book.get("url", "")
                    if "[" in link_cell and "]" in link_cell:
                        disp_match = re.search(r'\[([^\]]+)\]', link_cell)
                        disp_text = disp_match.group(1) if disp_match else "Liên kết"
                        parts[6] = f"[{disp_text}]({real_url})"
                    else:
                        parts[6] = real_url
                else:
                    # Clear out hallucinated/fabricated VNU links for general recommendations
                    if any(prefix in link_cell for prefix in ["vnu.edu.vn", "opac.", "repository.", "bookworm."]) or "[" in link_cell:
                        parts[6] = "Tài liệu bổ trợ (không có liên kết VNU-LIC)"
                
                lines[idx] = " | ".join(parts)
                continue
                
        # Case B: Inline markdown links
        links = re.findall(r'\[([^\]]+)\]\((https?://[^\s\)]+)\)', line)
        for text, url in links:
            is_vnu_url = any(p in url for p in ["vnu.edu.vn", "opac.", "repository.", "bookworm."])
            if is_vnu_url:
                matched_url = None
                for t, b in title_to_book.items():
                    if t in text.lower() or text.lower() in t or t in line.lower():
                        matched_url = b.get("url")
                        break
                
                if matched_url:
                    line = line.replace(url, matched_url)
                else:
                    line = line.replace(f"({url})", "(https://lic.vnu.edu.vn/)")
        lines[idx] = line
        
    return "\n".join(lines)

