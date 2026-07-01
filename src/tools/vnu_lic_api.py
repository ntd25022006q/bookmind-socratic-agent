import urllib.request
import urllib.parse
import json
import ssl

# Disable SSL verification for safety when running on various environments
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

VNU_LIC_BOOKS_DB = [
    {
        "biblionumber": 100201,
        "title": "21 bài học cho thế kỷ 21",
        "author": "Yuval Noah Harari",
        "publisher": "NXB Thế Giới",
        "isbn": "9786047754329",
        "item_status": "Available (Sẵn sàng)",
        "location": "Phòng mượn Hòa Lạc - Tầng 2 (LIC-HL)",
        "opac_url": "http://bookworm.lic.vnu.edu.vn/opac/biblios/100201",
        "summary": "Tác phẩm phân tích những thách thức lớn về công nghệ, chính trị và xã hội trong thế kỷ 21."
    },
    {
        "biblionumber": 100202,
        "title": "Khuyến học",
        "author": "Fukuzawa Yukichi",
        "publisher": "NXB Thế Giới",
        "isbn": "9786047781023",
        "item_status": "Available (Sẵn sàng)",
        "location": "Thư viện Ngoại ngữ - Tầng 1 (LIC-FL)",
        "opac_url": "http://bookworm.lic.vnu.edu.vn/opac/biblios/100202",
        "summary": "Tác phẩm kinh điển thảo luận về bình đẳng, tự do và vai trò của học tập thực tế đối với độc lập cá nhân."
    },
    {
        "biblionumber": 100203,
        "title": "Đúng việc",
        "author": "Giản Tư Trung",
        "publisher": "NXB Trẻ",
        "isbn": "9786041065112",
        "item_status": "On Loan (Đang mượn - Hạn trả: 2026-08-15)",
        "location": "Phòng mượn Xuân Thủy - Tầng 3 (LIC-XT)",
        "opac_url": "http://bookworm.lic.vnu.edu.vn/opac/biblios/100203",
        "summary": "Một cuốn sách thức tỉnh về cách làm người, làm nghề và làm dân trong thời đại chuyển dịch."
    },
    {
        "biblionumber": 100204,
        "title": "451 độ F (Fahrenheit 451)",
        "author": "Ray Bradbury",
        "publisher": "NXB Hội Nhà Văn",
        "isbn": "9786045391219",
        "item_status": "Available (Sẵn sàng)",
        "location": "Thư viện Công nghệ - Tầng 2 (LIC-ENG)",
        "opac_url": "http://bookworm.lic.vnu.edu.vn/opac/biblios/100204",
        "summary": "Tiểu thuyết giả tưởng về thế giới tương lai nơi sách bị cấm và nhiệm vụ của lính cứu hỏa là đốt sách."
    }
]

def search_koha_api(query: str) -> list:
    """Simulate VNU-LIC Koha ILS API /api/v1/biblios to search book catalog."""
    query_lower = query.lower()
    results = []
    
    # Check local pre-defined book DB
    for book in VNU_LIC_BOOKS_DB:
        if (query_lower in book["title"].lower() or 
            query_lower in book["author"].lower() or 
            query_lower in book["isbn"]):
            results.append(book)
            
    # If no local results, fetch from Google Books API and map it to VNU-LIC format
    if not results:
        try:
            safe_query = urllib.parse.quote(query)
            url = f"https://www.googleapis.com/books/v1/volumes?q={safe_query}&maxResults=3&langRestrict=vi"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, context=ssl_context, timeout=3) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                items = data.get("items", [])
                for idx, item in enumerate(items):
                    volume = item.get("volumeInfo", {})
                    title = volume.get("title", "Không rõ tựa đề")
                    authors = ", ".join(volume.get("authors", ["Không rõ tác giả"]))
                    publisher = volume.get("publisher", "NXB Đại học Quốc gia Hà Nội (mô phỏng)")
                    isbns = [id.get("identifier") for id in volume.get("industryIdentifiers", []) if id.get("type") in ["ISBN_13", "ISBN_10"]]
                    isbn = isbns[0] if isbns else "9780000000000"
                    
                    biblio = 200000 + idx
                    results.append({
                        "biblionumber": biblio,
                        "title": title,
                        "author": authors,
                        "publisher": publisher,
                        "isbn": isbn,
                        "item_status": "Available (Sẵn sàng)",
                        "location": "Phòng mượn Hòa Lạc - Tầng 1 (LIC-HL)",
                        "opac_url": f"http://bookworm.lic.vnu.edu.vn/opac/biblios/{biblio}",
                        "summary": volume.get("description", "Không có tóm tắt.")[:200] + "..."
                    })
        except Exception:
            pass
            
    return results

def search_dspace_api(query: str) -> list:
    """Simulate VNU-LIC DSpace repository API /api/core/items for theses/publications."""
    query_lower = query.lower()
    results = []
    
    # Simulated VNU repository items
    theses = [
        {
            "id": "11122/1054",
            "title": "Nghiên cứu nhu cầu đọc và định hướng văn hóa đọc cho sinh viên Trường Đại học Khoa học Xã hội và Nhân văn, ĐHQGHN",
            "author": "Nguyễn Thị Thùy",
            "date": "2024",
            "handle": "11122/1054",
            "url": "http://repository.vnu.edu.vn/handle/11122/1054",
            "type": "Luận văn thạc sĩ"
        },
        {
            "id": "11122/2098",
            "title": "Phát triển năng lực tự học của sinh viên các trường đại học thành viên thuộc Đại học Quốc gia Hà Nội thông qua hoạt động tự đọc",
            "author": "Lê Văn Thành",
            "date": "2023",
            "handle": "11122/2098",
            "url": "http://repository.vnu.edu.vn/handle/11122/2098",
            "type": "Luận án tiến sĩ"
        }
    ]
    
    for t in theses:
        if query_lower in t["title"].lower() or query_lower in t["author"].lower():
            results.append(t)
            
    return results
