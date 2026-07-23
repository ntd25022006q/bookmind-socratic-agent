# VNU BookMind Socratic 🧠📚

> **Nền Tảng Đa Tác Nhân (Multi-Agent Architecture) Hỗ Trợ Đọc Sâu & Phản Biện Socratic Dành Cho Sinh Viên**
>
> 🚀 *Giải pháp trí tuệ nhân tạo nâng cao văn hóa đọc chủ động, tích hợp triết lý Socratic và kho tri thức học thuật VNU-LIC*

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-orange?style=for-the-badge)](https://github.com/langchain-ai/langgraph)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

---

## 🌟 Giới Thiệu Dự Án & Triết Lý Socratic

**VNU BookMind Socratic** là hệ thống phần mềm trí tuệ nhân tạo chuyên biệt được xây dựng dựa trên kiến trúc Đa Tác Nhân (Multi-Agent System), hướng tới mục tiêu thúc đẩy tư duy phản biện, hỗ trợ nghiên cứu khoa học và phát triển thói quen tự học đọc sâu cho sinh viên Đại học Quốc gia Hà Nội (ĐHQGHN).

Khác biệt với các công cụ AI tóm tắt thụ động, BookMind tuân thủ chặt chẽ triết lý phương pháp Socrates: **AI không đọc hộ hay tóm tắt sẵn văn bản, mà đưa ra các câu hỏi gợi mở, phân tích điểm mù nhận thức và khuyến khích độc giả tự đối thoại, tự ghi chép và đưa ra kết luận.**

Tác giả dự án: **Nguyễn Tiến Đạt** (Sinh viên K24, Trường Quốc tế, Đại học Quốc gia Hà Nội).

---

## 🏛️ Danh Mục & Quy Chuẩn Phân Loại 4 Nguồn Học Liệu Số VNU-LIC Công Khai

Hệ thống kết nối thời gian thực và trích xuất dữ liệu từ các nguồn tài nguyên tri thức trọng điểm thuộc **Trung tâm Thư viện và Tri thức số (VNU-LIC)**:

### 🌐 Nguồn Mở Truy Cập Trực Tiếp Công Khai (Public Access Resources)

1. **VNU Scholar Repository (`scholar.vnu.edu.vn`)**:
   - **Mô tả**: Nền tảng quản trị tri thức số lưu trữ bài báo khoa học, công trình nghiên cứu công bố quốc tế, luận án tiến sĩ và kết quả nghiên cứu khoa học mở của ĐHQGHN.
   - **Cơ chế Link**: Hỗ trợ 2 link song song kép (**DSpace 7 Entity Page** & **Classic Handle URI**).

2. **VNU Repository (`repository.vnu.edu.vn`)**:
   - **Mô tả**: Kho lưu trữ số luận văn thạc sĩ, luận án tiến sĩ và công trình khoa học nguyên bản thuộc hệ thống các trường thành viên ĐHQGHN (ULIS, VNU-IS, HUS, USSH, VNU-UEB, VNU-UL...).
   - **Cơ chế Link**: Hỗ trợ 2 link song song kép (**Entity Page** & **Handle URI**).

3. **Bookworm VNU-LIC (`bookworm.vnu.edu.vn`)**:
   - **Mô tả**: Kho sách điện tử, giáo trình số và tài liệu tham khảo bản quyền. Cho phép bạn đọc tra cứu và đọc trực tiếp trên trình duyệt web.

4. **Cổng Thông Tin & Kho Sách Đông Dương (`lic.vnu.edu.vn`)**:
   - **Mô tả**: Bộ sưu tập di sản văn hóa, tư liệu số lịch sử và tài liệu quý hiếm thời kỳ Đông Dương do VNU-LIC số hóa.

---

### ⚠️ Ghi Chú Kỹ Thuật Về Koha OPAC (`opac.vnu.edu.vn`)

> [!IMPORTANT]
> **Tạm thời không sinh link Koha OPAC cho LLMs**:
> Máy chủ Koha OPAC (`opac.vnu.edu.vn`) quản lý sách in truyền thống yêu cầu kết nối Mạng nội bộ ĐHQGHN (VNU Campus Network / VNU VPN). Để đảm bảo sinh viên và người dùng truy cập từ mạng ngoài **không gặp lỗi liên kết chết (Dead Link / Connection Timeout)**, hệ thống AI Agent được thiết lập **tạm thời không sinh link Koha OPAC**.
> Thay vào đó, **VNU Scholar** và **VNU Repository** được sử dụng làm nguồn công khai thay thế trực tiếp, đảm bảo 100% tài liệu trích xuất có liên kết công khai hoạt động 200 OK.

---

## 📊 Định Dạng Bảng Tham Khảo Chuẩn 8 Cột Cho LLM Agent

Toàn bộ các tác nhân LLM trong hệ thống tuân thủ nghiêm ngặt cấu trúc Bảng Học liệu Tham khảo 8 cột chuẩn hóa như sau:

| STT | Tên tài liệu | Tác giả | Người hướng dẫn | Năm | Nhà xuất bản / Đơn vị chủ trì / Tạp chí | Nguồn | Handle URI / Entity Page |
|---|---|---|---|---|---|---|---|
| 1 | A hybrid feature selection method for credit scoring | Ha Van, Sang; Nguyen Ha, Nam; Nguyen Thi Bao, Hien | - | 2017 | EAI Endorsed Transactions | VNU Scholar | [Xem Entity](https://scholar.vnu.edu.vn/entities/publication/9c1b5dd9-167b-4f4f-9084-c5808ec35fff) \| [Xem Handle URI](https://scholar.vnu.edu.vn/handle/123456789/12692) $\rightarrow$ `https://scholar.vnu.edu.vn/entities/publication/9c1b5dd9-167b-4f4f-9084-c5808ec35fff` |
| 2 | Using impromptu speaking activities to improve student' fluency... | Bùi, Thị Hồng Hoa | - | 2026 | ĐHQGHN - Trường Đại học Ngoại ngữ | VNU Repository | [Xem Entity](https://repository.vnu.edu.vn/entities/publication/e87b7dca-5f05-4dd2-8d84-3ae579fce5ab) \| [Xem Handle URI](https://repository.vnu.edu.vn/handle/VNU_123/182268) $\rightarrow$ `https://repository.vnu.edu.vn/entities/publication/e87b7dca-5f05-4dd2-8d84-3ae579fce5ab` |
| 3 | Integration der flüchtlinge auf dem Deutschen arbeitsmarkt... | Đào, Thị Thắm | Trần, Thị Hạnh | 2022 | ĐHQGHN - Trường Đại học Ngoại ngữ | VNU Repository | [Xem Entity](https://repository.vnu.edu.vn/entities/publication/1ff7218c-e60e-4f3a-922d-c017d0a65ec9) \| [Xem Handle URI](https://repository.vnu.edu.vn/handle/VNU_123/143559) $\rightarrow$ `https://repository.vnu.edu.vn/entities/publication/1ff7218c-e60e-4f3a-922d-c017d0a65ec9` |
| 4 | Auguste comte sa vie | Cresson, André | - | 1947 | Presses universitaires de France | Cổng VNU-LIC | [Xem tại Cổng VNU-LIC](https://lic.vnu.edu.vn/books/auguste-comte-sa-vie) $\rightarrow$ `https://lic.vnu.edu.vn/books/auguste-comte-sa-vie` |

### 🛠️ Quy Tắc Trình Bày Dữ Liệu Bắt Buộc:
1. **Thiếu thông tin**: Khi một ô dữ liệu không có thông tin (ví dụ: bài báo/sách không có Người hướng dẫn), phải điền duy nhất một dấu gạch ngang `-`. Không tự bịa văn bản "Không có" hay điền sai thông tin.
2. **Link song song**: Đối với các tài liệu VNU Scholar và VNU Repository, Cột 8 phải hiển thị đồng thời link **DSpace Entity Page** và link **Classic Handle URI**, kèm URL RAW dạng văn bản để người dùng copy trực tiếp.

---

## 🔗 Thông Số Kỹ Thuật API Endpoint Chính Thức

Hệ thống truy xuất dữ liệu nguyên bản thông qua 4 API Endpoint đã được kiểm xác:

1. **VNU Scholar REST API**:
   - `GET https://scholar.vnu.edu.vn/server/api/core/items/{uuid}`
   - Trích xuất: `dc.title`, `dc.contributor.author`, `dc.date.issued`, `dc.relation.ispublishedin`, `dc.identifier.uri`

2. **VNU Repository REST API**:
   - `GET https://repository.vnu.edu.vn/server/api/discover/search/objects?dsoType=item`
   - Trích xuất: `dc.title`, `dc.contributor.author`, `dc.contributor.advisor`, `dc.publisher`, `dc.identifier.uri`

3. **Bookworm VNU-LIC API**:
   - `GET https://bookworm.vnu.edu.vn/EDetail.aspx?id={id}`
   - Trích xuất mã EDetail sách điện tử bản quyền.

4. **Cổng Thư viện VNU-LIC API**:
   - `GET https://lic.vnu.edu.vn/books/{slug}`
   - Trích xuất sách cổ di sản Đông Dương theo Slug kiểm định `200 OK`.

---

## 🧠 Kiến Trúc 6 Tác Nhân Socratic Tuần Tự (LangGraph Engine)

```mermaid
flowchart TD
    Input(["Câu hỏi & Yêu cầu độc giả"]) --> FormCheck{"Đã điền Hồ sơ?"}
    FormCheck -- "Chưa" --> ShowForm["Bắt buộc điền Chân dung độc giả"]
    ShowForm --> SaveProfile["Lưu LocalStorage"]
    FormCheck -- "Rồi" --> Guardrail["01. Tác Nhân Cảnh Giới"]
    SaveProfile --> Guardrail
    
    Guardrail --> InjectionCheck{"Prompt Injection / Ngoài phạm vi?"}
    InjectionCheck -- "Có" --> RejectEnd(["Từ Chối Trả Lời Học Thuật"])
    InjectionCheck -- "Không" --> Profiler["02. Tác Nhân Hồ Sơ"]
    
    Profiler --> Recommender["03. Tác Nhân Gợi Ý Sách"]
    Recommender --> Questioner["04. Đối Thoại Socrates"]
    Questioner --> Critic["05. Tác Nhân Phản Biện"]
    Critic --> Reporter["06. Tác Nhân Biên Soạn"]
    Reporter --> ReportEnd(["Xuất Báo Cáo Học Thuật & Sơ Đồ Quy Trình"])
```

---

## 💻 Hướng Dẫn Cài Đặt & Vận Hành Localhost

```bash
# 1. Tạo và kích hoạt môi trường ảo Python 3.10+
python -m venv .venv
.venv\Scripts\Activate.ps1   # Windows

# 2. Cài đặt thư viện phụ thuộc
pip install -r requirements.txt

# 3. Khởi chạy Server Backend & Frontend
python server.py
cd frontend
python -m http.server 3000
```
Truy cập ứng dụng tại địa chỉ: `http://localhost:3000`.

---

## 📜 Bản Quyền & Giấy Phép

Dự án nghiên cứu phục vụ phát triển Văn hóa Đọc và Tri thức số tại ĐHQGHN, tuân thủ giấy phép mã nguồn mở [MIT License](LICENSE).
