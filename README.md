# VNU BookMind Socratic 🧠📚

> **Hệ thống Đa Tác Nhân (Multi-Agent) Hỗ Trợ Đọc Sâu & Phản Biện Socratic Dành Cho Sinh Viên**
>
> 🚀 *Nền tảng trí tuệ nhân tạo thế hệ mới kết hợp triết lý Socratic và kho tri thức học thuật VNU-LIC*

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-orange?style=for-the-badge)](https://github.com/langchain-ai/langgraph)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

---

## 🌟 Giới Thiệu Dự Án

**VNU BookMind Socratic** là ứng dụng Web thông minh dựa trên kiến trúc Đa Tác Nhân (Multi-Agent Architecture), hỗ trợ văn hóa đọc chủ động, tự học và tư duy phản biện cho sinh viên Đại học Quốc gia Hà Nội (ĐHQGHN).

Phương pháp tiếp cận dựa trên triết lý Socratic: **AI không đọc hộ hay tóm tắt thay con người, mà đóng vai trò người đối thoại đặt câu hỏi gợi mở để người đọc tự tư duy, phân tích và ghi chép đọc sâu.**

---

## 🏛️ Quy Chuẩn Trích Xuất & Phân Loại 5 Nguồn Học Liệu Số VNU-LIC

Hệ thống kết nối trực tiếp và phân loại minh bạch 5 nguồn tài nguyên tri thức số của **Trung tâm Thư viện và Tri thức số (VNU-LIC)**:

### 🌐 Group 1: Các Nguồn Mở Trực Tiếp Công Cộng (Không Cần VPN)

1. **Bookworm VNU-LIC (`bookworm.vnu.edu.vn`)**:
   - **Tài nguyên**: Giáo trình, sách điện tử và sách tham khảo đọc trực tuyến.
   - **Mẫu URL chuẩn**: `https://bookworm.vnu.edu.vn/EDetail.aspx?id={id}`

2. **VNU Scholar Repository (`scholar.vnu.edu.vn`)**:
   - **Tài nguyên**: Công trình nghiên cứu khoa học, bài báo tạp chí quốc tế, luận án tiến sĩ công khai.
   - **Mẫu URL chuẩn**: `https://scholar.vnu.edu.vn/entities/publication/{uuid}`

3. **Kho Sách Đông Dương & Cổng LIC (`lic.vnu.edu.vn`)**:
   - **Tài nguyên**: Bộ sưu tập sách cổ, di sản văn hóa và tài liệu số di sản VNU-LIC.
   - **Mẫu URL chuẩn**: `https://lic.vnu.edu.vn/books/{slug}`

---

### 🔒 Group 2: Các Nguồn Tra Cứu Nội Bộ (Mạng Nội Bộ ĐHQGHN / VNU VPN)

4. **Koha OPAC Catalog (`opac.vnu.edu.vn`)**:
   - **Tài nguyên**: CSDL tra cứu danh mục tài nguyên thư viện.
   - **Định dạng liên kết**: `-` (Yêu cầu kết nối mạng nội bộ ĐHQGHN / VNU VPN để truy cập trực tiếp).

5. **DSpace VNU Repository (`repository.vnu.edu.vn`)**:
   - **Tài nguyên**: Kho tài nguyên lưu trữ số nội bộ ĐHQGHN.
   - **Định dạng liên kết**: `-` (Yêu cầu kết nối mạng nội bộ ĐHQGHN / VNU VPN để truy cập trực tiếp).

---

## 🧠 Kiến Trúc 6 Tác Nhân Socratic (LangGraph Pipeline)

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

### Chi Tiết 6 Tác Nhân:
1. **01. Cảnh Giới (Guardrail Agent)**: Phân loại câu hỏi, chặn Prompt Injection và các yêu cầu nằm ngoài phạm vi khuyến đọc.
2. **02. Hồ Sơ (Profiler Agent)**: Phân tích chân dung độc giả (Trường, Ngành, Mục tiêu đọc).
3. **03. Gợi Ý Sách (Recommender Agent)**: Truy xuất song song từ Bookworm, VNU Scholar, và VNU-LIC Portal. Đề xuất link công khai hoặc ghi chú rõ yêu cầu VNU VPN cho nguồn nội bộ.
4. **04. Đối Thoại Socrates (Socrates Questioner)**: Đưa ra 3 câu hỏi gợi mở sâu sắc kích thích tự vấn dựa trên tài liệu.
5. **05. Phản Biện (Critic Agent)**: Phân tích điểm mù nhận thức và góc nhìn đối lập.
6. **06. Biên Soạn (Reporter Agent)**: Tổng hợp báo cáo Markdown hoàn chỉnh, bảng 6 cột chuẩn, sơ đồ Mermaid và KaTeX.

---

## 💻 Hướng Dẫn Cài Đặt & Chạy Localhost

### 1. Cấu hình môi trường
Tạo tệp `.env` tại thư mục gốc:
```env
OLLAMA_API_KEY=your_ollama_cloud_api_key_here
OLLAMA_BASE_URL=https://ollama.com/v1
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

### 2. Khởi chạy Backend (FastAPI)
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1   # Windows PowerShell
# source .venv/bin/activate  # macOS/Linux

pip install -r requirements.txt
python server.py
```
Backend chạy tại: `http://127.0.0.1:8000` (Swagger Docs: `http://127.0.0.1:8000/docs`).

### 3. Khởi chạy Frontend
```bash
cd frontend
python -m http.server 3000
```
Truy cập: `http://localhost:3000`.

---

## 🌐 Triển Khai Cloud & Tự Động Hóa (CI/CD)

- Hệ thống được cấu hình tự động đồng bộ xây dựng và triển khai từ nhánh `main` trên GitHub.
- **Frontend**: Nền tảng giao diện web tĩnh tương tác trực tiếp với người dùng.
- **Backend**: Dịch vụ API Web Service xử lý đa tác nhân và định tuyến dữ liệu thời gian thực.

---

## 📜 Bản Quyền & Giấy Phép
Dự án nghiên cứu phục vụ phát triển Văn hóa Đọc và Tri thức số tại ĐHQGHN, phát hành theo giấy phép [MIT License](LICENSE).
