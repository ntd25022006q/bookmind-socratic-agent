# VNU BookMind Socratic 🧠📚

> **Hệ thống Đa Tác Nhân (Multi-Agent) Hỗ Trợ Đọc Sâu & Phản Biện Sách Socratic Dành Cho Sinh Viên**
>
> 🚀 *Nền tảng trí tuệ nhân tạo thế hệ mới kết hợp triết lý Socratic và kho tri thức học thuật VNU-LIC*

[![Production Status](https://img.shields.io/badge/Production-Active-16a069?style=for-the-badge&logo=vercel)](https://bookmind-socratic-agent.vercel.app/)
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-orange?style=for-the-badge)](https://github.com/langchain-ai/langgraph)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

---

## 🌟 Giới Thiệu Dự Án

**VNU BookMind Socratic** là một ứng dụng Web thông minh dựa trên kiến trúc Đa Tác Nhân (Multi-Agent Architecture) được thiết kế nhằm nâng cao văn hóa đọc chủ động, khuyến khích tự học và thúc đẩy tư duy phản biện. 

Khác biệt hoàn toàn với các chatbot AI thông thường (thường tóm tắt hộ làm thui chột khả năng tự tư duy), BookMind áp dụng triết lý phương pháp Socrates: **AI không đọc hộ con người, AI định hướng và đặt câu hỏi mở để con người tự phản biện và tự ghi chép đọc sâu.**

Hệ thống kết nối thời gian thực đến các nguồn học liệu chính thống của **Trung tâm Thư viện và Tri thức số (VNU-LIC)** bao gồm:
- 🏛️ **VNU Repository (DSpace)**: Luận án, luận văn và nghiên cứu học thuật chính thống của ĐHQGHN (`repository.vnu.edu.vn`).
- 📖 **Bookworm VNU-LIC**: Sách điện tử và giáo trình đọc trực tuyến (`bookworm.vnu.edu.vn`).
- 🌐 **VNU-LIC Main Portal**: Cổng thông tin tra cứu tập trung VNU-LIC (`lic.vnu.edu.vn`).

Dữ liệu API được kết hợp cùng cơ chế **RAG (Retrieval-Augmented Generation)** để đề xuất các tài liệu chính xác có thật 100%, loại bỏ hoàn toàn hiện tượng ảo tưởng liên kết (hallucinated links) của LLM.

---

## 🧠 Kiến Trúc Đồ Thị 6 Tác Nhân Socratic (LangGraph Pipeline)

BookMind Socratic vận hành dựa trên kiến trúc Multi-Agent phối hợp tuần tự thông qua **LangGraph** nhằm chia nhỏ nhiệm vụ, tối ưu hóa ngữ cảnh và nâng cao độ chính xác:

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

### Chi Tiết Nhiệm Vụ Từng Tác Nhân:
1. **01. Cảnh Giới (Guardrail Agent)**:
   - Lọc và xác thực tính học thuật của câu hỏi đầu vào.
   - **Bảo vệ hệ thống (Prompt Injection Defense)**: Ngăn chặn triệt để các hành vi thăm dò system prompt, rò rỉ API Keys hoặc tokens kết nối Vercel/Render, từ chối thẳng thắn các chủ đề nằm ngoài phạm vi khuyến đọc.
2. **02. Hồ Sơ (Profiler Agent)**:
   - Phân tích thông tin độc giả (Trường, Ngành học, Mục đích đọc, Phong cách tư duy) để dựng nên chân dung nhận thức cá nhân hóa cho từng truy vấn.
3. **03. Gợi Ý Sách (Recommender Agent)**:
   - Truy xuất song song từ 3 nguồn học liệu số VNU-LIC (DSpace REST API, Bookworm eBook portal, VNU-LIC Main Portal) kết hợp ChromaDB Local RAG. Đề xuất từ 3-5 tài liệu chính xác có thật kèm đường dẫn liên kết.
4. **04. Đối Thoại Socrates (Socrates Questioner)**:
   - **Nguyên tắc Không tóm tắt hộ**: Từ chối viết tóm tắt thay độc giả. Đưa ra 3 câu hỏi đối thoại mở Socrates sâu sắc kích thích tự vấn dựa trên nội dung sách.
5. **05. Phản Biện (Critic Agent / Risk Assessor)**:
   - Phân tích thiên kiến xác nhận (confirmation bias), góc nhìn đối lập và phát hiện điểm mù nhận thức khi độc giả tiếp cận chủ đề.
6. **06. Biên Soạn (Reporter Agent)**:
   - Tổng hợp toàn bộ quy trình thành Báo cáo học thuật Markdown hoàn chỉnh, bảng tài liệu tham khảo 6 cột chuẩn, sơ đồ lộ trình đọc Mermaid và tích hợp **KaTeX** hiển thị công thức toán học/khoa học.

---

## ⚡ Động Cơ LLM Động & Mô Hình Tối Ưu Tốc Độ

Hệ thống được trang bị cơ chế **LLM Dynamic Model Switching & Auto-Fallback** nhằm đảm bảo tốc độ đáp ứng cực nhanh và độ tin cậy tuyệt đối:

- **Ưu tiên Mô hình Miễn phí & Tốc độ cao trên Ollama Cloud**:
  - `gemma4:31b` (Mô hình suy luận chính xác, tốc độ cao)
  - `nemotron-3-nano:30b` (Mô hình phản hồi nhanh)
  - `gpt-oss:20b` / `minimax-m3` / `gpt-oss:120b` / `nemotron-3-ultra`
- **Bộ kiểm tra Sức khỏe Mô hình Động (Health Daemon)**:
  - Tự động phát hiện và loại bỏ các mô hình bị giới hạn trả phí (HTTP 403 Subscription Required) hoặc hết quota (HTTP 429).
- **Chuỗi Dự phòng Đa Nền tảng (OpenRouter Fallback)**:
  - Tự động chuyển đổi sang các mô hình miễn phí của OpenRouter (`meta-llama/llama-3.3-70b-instruct:free`, `google/gemini-2.0-flash-exp:free`) nếu phát sinh sự cố kết nối Ollama Cloud. Tiến trình Multi-Agent không bao giờ bị dừng hay báo lỗi!

---

## 🛠️ Tính Năng Đột Phá & Độ Tin Cậy

- 🛡️ **Bảo Vệ Quyền Riêng Tư & Dữ Liệu**: Loại bỏ hoàn toàn mọi thông tin cá nhân nhạy cảm hay API keys trên kho mã nguồn GitHub.
- 🎨 **Bộ Xử Lý Sơ Đồ Tự Động (Mermaid Auto-Healer)**: Tích hợp cơ chế Fail-Safe Rendering 2 lớp. Tự động chuyển đổi cú pháp mũi tên lỗi từ LLM và đảm bảo sơ đồ quy trình luôn được hiển thị sắc nét, không bị vỡ giao diện.
- 🔗 **Chuẩn Hóa Trích Dẫn VNU-LIC 100%**: Hàm kiểm tra tiêu đề nghiêm ngặt đảm bảo các URL gán cho tài liệu đều là liên kết thật từ thư viện ĐHQGHN, nói không với link ảo.
- 🔄 **Khôi Phục Tiến Trình & Đồng Bộ Ngầm (Silent Polling)**: Tự động duy trì và khôi phục trạng thái khi ngắt kết nối mạng tạm thời mà không làm ảnh hưởng đến trải nghiệm người dùng.

---

## 💻 Hướng Dẫn Cài Đặt & Chạy Localhost

### 1. Cấu hình biến môi trường
Tạo tệp `.env` tại thư mục gốc của dự án (tham khảo mẫu `.env.example`):
```env
OLLAMA_API_KEY=your_ollama_cloud_api_key_here
OLLAMA_BASE_URL=https://ollama.com/v1

# Tùy chọn: Dự phòng OpenRouter khi Ollama hết quota
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

### 2. Khởi chạy Backend (FastAPI)
Yêu cầu Python 3.10 trở lên.
```bash
# Tạo môi trường ảo
python -m venv .venv

# Kích hoạt môi trường ảo
# Trên Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Trên macOS/Linux:
source .venv/bin/activate

# Cài đặt các thư viện phụ thuộc
pip install -r requirements.txt

# Khởi chạy API Server (Cổng mặc định 8000)
python server.py
```
Backend sẽ hoạt động tại địa chỉ: `http://127.0.0.1:8000`. Bạn có thể truy cập `/docs` để kiểm tra tài liệu API Swagger.

### 3. Khởi chạy Frontend (HTML/JS)
Frontend được đặt trong thư mục `frontend/`. Bạn có thể sử dụng bất kỳ công cụ serve tĩnh nào hoặc chạy trực tiếp bằng Python:
```bash
cd frontend
python -m http.server 3000
```
Mở trình duyệt tại `http://localhost:3000` để bắt đầu trải nghiệm.

---

## 🌐 Triển Khai Cloud (CI/CD)

Dự án được cấu hình tự động đồng bộ deploy từ nhánh `main` trên GitHub:
* 🌐 **Frontend (Vercel)**: Tự động deploy giao diện tại [bookmind-socratic-agent.vercel.app](https://bookmind-socratic-agent.vercel.app/).
* ⚙️ **Backend (Render)**: Python Web Service hoạt động tại Render (`https://bookmind-socratic-agent-5o4p.onrender.com`).
* *Lưu ý*: Khi thiết lập trên Dashboard của Vercel và Render, vui lòng bổ sung các biến môi trường `OLLAMA_API_KEY` và `OLLAMA_BASE_URL` tương ứng.

---

## 📜 Bản Quyền & Giấy Phép

- **Đơn vị phát triển**: Dự án nghiên cứu ứng dụng Multi-Agent hỗ trợ xây dựng Văn hóa Đọc hiện đại và tự học tích cực cho cộng đồng sinh viên ĐHQGHN.
- **Giấy phép**: Thấu hiểu và tuân thủ các quy định mã nguồn mở theo [MIT License](LICENSE).
