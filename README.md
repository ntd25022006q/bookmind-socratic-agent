# 🧠📚 VNU BookMind Socratic

> **Nền Tảng AI Đa Tác Nhân (Multi-Agent Architecture) Hỗ Trợ Đọc Sâu & Phản Biện Socratic Dành Cho Sinh Viên**
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

- **Tác giả dự án**: **Nguyễn Tiến Đạt** (Sinh viên K24, Trường Quốc tế, Đại học Quốc gia Hà Nội).

---

## ✨ Tính Năng Nổi Bật

- 🤖 **Kiến trúc Đa Tác Nhân 6 Tầng (LangGraph Sequential Engine)**: Phối hợp 6 AI Agent chuyên biệt xử lý từ cảnh giới bảo mật, dựng chân dung độc giả, gợi ý học liệu đến phản biện và xuất báo cáo.
- 📚 **Tích Hợp Kho Tri Thức Học Thuật VNU-LIC**: Truy xuất thời gian thực các bài báo khoa học, luận văn thạc sĩ/luận án tiến sĩ và sách điện tử từ hệ thống thư viện số ĐHQGHN.
- 🎯 **Trích Dẫn Nguyên Bản & Cơ Chế Link Song Song Kép**: Cung cấp liên kết công khai song song (**DSpace 7 Entity Page** & **Classic Handle URI**) giúp bạn đọc truy cập học liệu không bị gián đoạn.
- 💬 **Đối Thoại Socrates Tự Co Giãn**: Gợi mở 3 câu hỏi đào sâu tư duy giúp độc giả phát hiện điểm mù lý thuyết và mở rộng góc nhìn nghiên cứu.
- ⚡ **Luồng Truyền Phát Sự Kiện Thời Gian Thực (Real-time SSE Streaming)**: Hiển thị tiến trình suy luận và kết quả tương tác mượt mà trên giao diện web.

---

## 🏛️ Hệ Sinh Thái Học Liệu Số VNU-LIC Tích Hợp

Hệ thống kết nối thời gian thực và trích xuất dữ liệu từ các nguồn tài nguyên tri thức trọng điểm thuộc **Trung tâm Thư viện và Tri thức số (VNU-LIC)**:

1. 🎓 **VNU Scholar Repository (`scholar.vnu.edu.vn`)**:
   - Kho tri thức lưu trữ các công trình nghiên cứu khoa học công bố quốc tế, bài báo tạp chí chuyên ngành và kết quả nghiên cứu mở của ĐHQGHN.

2. 🏛️ **VNU Repository (`repository.vnu.edu.vn`)**:
   - Kho lưu trữ số luận văn thạc sĩ, luận án tiến sĩ và tài liệu học thuật thuộc hệ thống các trường đại học thành viên ĐHQGHN (ULIS, VNU-IS, HUS, USSH, VNU-UEB, VNU-UL...).

3. 📖 **Bookworm VNU-LIC (`bookworm.vnu.edu.vn`)**:
   - Kho sách điện tử, giáo trình số và tài liệu tham khảo bản quyền phục vụ học tập và giảng dạy.

4. 📚 **Cổng Thông Tin & Kho Sách Đông Dương (`lic.vnu.edu.vn`)**:
   - Bộ sưu tập di sản văn hóa, tư liệu số lịch sử và tài liệu quý hiếm thời kỳ Đông Dương do VNU-LIC số hóa.

---

## 🧠 Kiến Trúc 6 Tác Nhân Socratic (LangGraph Workflow)

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

### Chức Năng Chi Tiết Từng Tác Nhân:

1. **01. Cảnh Giới (Guardrail Agent)**:
   - Bảo mật hệ thống: Chặn đứng Prompt Injection, từ chối các yêu cầu ngoài phạm vi học thuật hoặc vi phạm nguyên tắc tự học.

2. **02. Hồ Sơ (Profiler Agent)**:
   - Dựng chân dung độc giả dựa trên ngành học, trường thành viên, mục tiêu nghiên cứu và phong cách nhận thức.

3. **03. Gợi Ý Sách (Recommender Agent)**:
   - Truy xuất danh mục tài liệu phù hợp nhất từ kho VNU-LIC kèm đầy đủ thông tin tác giả, người hướng dẫn, năm xuất bản và đường dẫn nguyên bản.

4. **04. Đối Thoại Socrates (Socrates Questioner)**:
   - Đặt 3 câu hỏi gợi mở sâu sắc thúc đẩy độc giả tự phân tích thay vì tiếp nhận thông tin một chiều.

5. **05. Phản Biện (Critic Agent)**:
   - Phân tích các góc nhìn đối lập, phát hiện thiên kiến xác nhận và chỉ ra các hạn chế lý thuyết.

6. **06. Biên Soạn (Reporter Agent)**:
   - Tổng hợp toàn bộ kết quả thành Báo cáo học thuật Markdown hoàn chỉnh, sơ đồ Mermaid và bảng học liệu tham khảo chuẩn mực.

---

## 💻 Hướng Dẫn Cài Đặt & Vận Hành Localhost

### 1. Khởi tạo môi trường
```bash
# Tạo và kích hoạt môi trường ảo Python 3.10+
python -m venv .venv
.venv\Scripts\Activate.ps1   # Windows PowerShell
# source .venv/bin/activate  # macOS/Linux

# Cài đặt thư viện phụ thuộc
pip install -r requirements.txt
```

### 2. Thiết lập biến môi trường (`.env`)
```env
OLLAMA_API_KEY=your_ollama_cloud_api_key_here
OLLAMA_BASE_URL=https://ollama.com/v1
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

### 3. Khởi chạy Ứng dụng
```bash
# Khởi chạy Backend API Server
python server.py

# Khởi chạy Frontend Web App
cd frontend
python -m http.server 3000
```
Truy cập ứng dụng tại địa chỉ: `http://localhost:3000`.

---

## 📜 Bản Quyền & Giấy Phép

Dự án nghiên cứu phục vụ phát triển Văn hóa Đọc và Tri thức số tại ĐHQGHN, tuân thủ giấy phép mã nguồn mở [MIT License](LICENSE).
