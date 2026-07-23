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
- 📚 **Tích Hợp Học Liệu 4 Nguồn VNU-LIC Công Khai**: Truy xuất thời gian thực các bài báo khoa học, luận văn/luận án và sách điện tử từ hệ thống thư viện số ĐHQGHN.
- 🎯 **Trích Dẫn Nguyên Bản & Cơ Chế Link Song Song Kép**: Cung cấp liên kết công khai song song (**DSpace 7 Entity Page** & **Classic Handle URI**) giúp bạn đọc truy cập học liệu 100% hoạt động 200 OK.
- 💬 **Đối Thoại Socrates Tự Co Giãn**: Gợi mở 3 câu hỏi đào sâu tư duy giúp độc giả phát hiện điểm mù lý thuyết và mở rộng góc nhìn nghiên cứu.
- ⚡ **Luồng Truyền Phát Sự Kiện Thời Gian Thực (Real-time SSE Streaming)**: Hiển thị tiến trình suy luận và kết quả tương tác mượt mà trên giao diện web.

---

## 🏛️ Hệ Sinh Thái 4 Nguồn Học Liệu Số VNU-LIC Công Khai

Hệ thống kết nối thời gian thực và trích xuất dữ liệu từ 4 nguồn tài nguyên tri thức trọng điểm thuộc **Trung tâm Thư viện và Tri thức số (VNU-LIC)**:

1. 🎓 **VNU Scholar Repository (`scholar.vnu.edu.vn`)**:
   - Kho tri thức lưu trữ các công trình nghiên cứu khoa học công bố quốc tế, bài báo tạp chí chuyên ngành và kết quả nghiên cứu mở của ĐHQGHN.

2. 🏛️ **VNU Repository (`repository.vnu.edu.vn`)**:
   - Kho lưu trữ số luận văn thạc sĩ, luận án tiến sĩ và tài liệu học thuật thuộc hệ thống các trường đại học thành viên ĐHQGHN (ULIS, VNU-IS, HUS, USSH, VNU-UEB, VNU-UL...).

3. 📖 **Bookworm VNU-LIC (`bookworm.vnu.edu.vn`)**:
   - Kho sách điện tử, giáo trình số và tài liệu tham khảo bản quyền phục vụ học tập và giảng dạy.

4. 📚 **Cổng Thông Tin & Kho Sách Đông Dương (`lic.vnu.edu.vn`)**:
   - Bộ sưu tập di sản văn hóa, tư liệu số lịch sử và tài liệu quý hiếm thời kỳ Đông Dương do VNU-LIC số hóa.

---

## 📸 Trải Nghiệm Giao Diện & Quy Trình Vận Hành Thời Gian Thực (UI & System State Walkthrough)

Dưới đây là chi tiết từng bước vận hành thực tế của giao diện **VNU BookMind Socratic** trải qua các trạng thái từ **Sẵn sàng** $\rightarrow$ **Đang chạy** $\rightarrow$ **Hội thoại Socratic** $\rightarrow$ **Hoàn thành**:

---

### 1️⃣ Bước 1: Thiết Lập Chân Dung Độc Giả (Profile Setup Modal)
![Thiết Lập Chân Dung Độc Giả](docs/screenshots/1_profile_modal.png)

- **Mô tả giao diện**: Khi lần đầu truy cập hệ thống, một cửa sổ Modal hiện ra yêu cầu sinh viên điền thông tin học thuật cá nhân: *Họ và tên, MSSV, Sinh viên năm mấy, Trường thành viên ĐHQGHN, Ngành học, Mục đích đọc sách chính, Lĩnh vực quan tâm và Phong cách đọc ưa thích*.
- **Cơ chế vận hành**: Thông tin được lưu an toàn vào `LocalStorage` của trình duyệt. Tác nhân **Profiler Agent (02)** sẽ truy xuất dữ liệu này để cá nhân hóa toàn bộ nội dung đề xuất học liệu và xây dựng ma trận đối thoại phản biện.

---

### 2️⃣ Bước 2: Trạng Thái Sẵn Sàng (Ready State)
![Trạng Thái Sẵn Sàng](docs/screenshots/2_ready_state.png)

- **Mô tả giao diện**: Giao diện khởi tạo với trạng thái **"Sẵn sàng"** hiển thị màu xanh lá cây tại khung Chỉ số vận hành. Sơ đồ phối hợp 6 Tác nhân ở trên cùng ở chế độ chờ (0.000s | 0 tk). Khung Báo cáo học thuật bên phải hiển thị "BÁO CÁO CHƯA ĐƯỢC TẠO".
- **Cơ chế vận hành**: Hệ thống lắng nghe yêu cầu nhập từ ô văn bản `Nhập nội dung cần phân tích`. Độc giả có thể nhấn nút `⚡ Kích Hoạt Phân Tích` để gửi truy vấn đến Pipeline 6 Tác nhân.

---

### 3️⃣ Bước 3: Đối Thoại Phản Biện Socrates (Socratic Interactive Modal)
![Hội Thoại Phản Biện Socrates](docs/screenshots/3_socratic_modal.png)

- **Mô tả giao diện**: Khi tác nhân **Socrates (04)** được kích hoạt, một cửa sổ Modal nổi lên hiển thị **3 Câu Hỏi Phản Biện Socratic** được sinh tự động dựa trên tài liệu nghiên cứu và chủ đề độc giả đặt ra.
- **Cơ chế vận hành**: Hệ thống tạm dừng pipeline để chờ sinh viên tự suy ngẫm và nhập câu trả lời vào 3 ô văn bản. Sau khi nhấn `🚀 Gửi Câu Trả Lời Phản Biện`, Tác nhân **Phản Biện (Critic Agent 05)** sẽ nhận các câu trả lời này để phân tích thiên kiến nhận thức, điểm mù lý thuyết và dựng ma trận Checkpoint tự vấn.

---

### 4️⃣ Bước 4: Trạng Thái Đang Chạy (Running State & Real-time SSE Stream)
![Trạng Thái Đang Chạy](docs/screenshots/4_running_state.png)

- **Mô tả giao diện**: Chỉ số trạng thái chuyển sang **"Đang chạy..."** màu cam rực rỡ. Nút kích hoạt chuyển thành nút `🔴 Dừng` màu cam. Các icon tác nhân trên sơ đồ sáng đèn theo thứ tự tuần tự, cập nhật thời gian xử lý và số lượng token theo thời gian thực (ví dụ: `gemma4:31b · 15.306s · 74.5 tk/s · 1,141 tk`).
- **Cơ chế vận hành**: Phía khung giữa (Console Log), luồng truyền phát sự kiện **SSE (Server-Sent Events)** hiển thị quá trình suy nghĩ (Thinking Process) và nhật ký phân tích của từng Agent. Phía khung bên phải, Báo cáo học thuật được truyền phát từng từ (word-by-word) mượt mà với Bảng 8 cột nguyên bản trích xuất từ 4 nguồn VNU-LIC.

---

### 5️⃣ Bước 5: Trạng Thái Hoàn Thành (Completed State & Mermaid Flowchart)
![Trạng Thái Hoàn Thành](docs/screenshots/5_completed_state.png)

- **Mô tả giao diện**: Trạng thái hiển thị **"Hoàn Thành"** màu xanh lá cây kèm icon tích xanh. Tổng thời gian xử lý và tổng số token toàn pipeline được thống kê đầy đủ (ví dụ: `68.433s | 4,491 Token`). Các nút chức năng xuất báo cáo (`Khởi Chạy Lại`, `Xuất báo cáo chi tiết`, `Xuất sơ đồ quy trình`) được kích hoạt.
- **Cơ chế vận hành**: Khung bên phải cho phép chuyển đổi giữa tab **Báo Cáo Chi Tiết** và tab **Sơ Đồ Quy Trình**. Tab Sơ đồ hiển thị biểu đồ **Mermaid.js Flowchart TD (Top-Down)** phản ánh trực quan lộ trình đọc sách Socratic của độc giả kèm đoạn văn mô tả giải thích chi tiết 3 giai đoạn đọc.

---

## 📊 Bảng Học Liệu Tham Khảo Chuẩn 8 Cột

Toàn bộ các tác nhân LLM trong hệ thống tuân thủ nghiêm ngặt cấu trúc Bảng Học liệu Tham khảo 8 cột chuẩn hóa như sau:

| STT | Tên tài liệu | Tác giả | Người hướng dẫn | Năm | Nhà xuất bản / Đơn vị chủ trì / Tạp chí | Nguồn | Handle URI / Entity Page |
|---|---|---|---|---|---|---|---|
| 1 | A hybrid feature selection method for credit scoring | Ha Van, Sang; Nguyen Ha, Nam; Nguyen Thi Bao, Hien | - | 2017 | EAI Endorsed Transactions | VNU Scholar Repository | [Xem Entity](https://scholar.vnu.edu.vn/entities/publication/9c1b5dd9-167b-4f4f-9084-c5808ec35fff) \| [Xem Handle URI](https://scholar.vnu.edu.vn/handle/123456789/12692) $\rightarrow$ `https://scholar.vnu.edu.vn/entities/publication/9c1b5dd9-167b-4f4f-9084-c5808ec35fff` |
| 2 | Using impromptu speaking activities to improve student' fluency... | Bùi, Thị Hồng Hoa | - | 2026 | ĐHQGHN - Trường Đại học Ngoại ngữ | VNU Repository | [Xem Entity](https://repository.vnu.edu.vn/entities/publication/e87b7dca-5f05-4dd2-8d84-3ae579fce5ab) \| [Xem Handle URI](https://repository.vnu.edu.vn/handle/VNU_123/182268) $\rightarrow$ `https://repository.vnu.edu.vn/entities/publication/e87b7dca-5f05-4dd2-8d84-3ae579fce5ab` |
| 3 | The use of pictures in teaching English speaking in an English center | Duong, Tra Mi | Vu, Mai Trang | 2011 | ĐHQGHN - Trường Đại học Ngoại ngữ | VNU Repository | [Xem Entity](https://repository.vnu.edu.vn/entities/publication/1ff731b9-5e12-4f8e-ae8f-b08c34627537) \| [Xem Handle URI](https://repository.vnu.edu.vn/handle/VNU_123/40615) $\rightarrow$ `https://repository.vnu.edu.vn/entities/publication/1ff731b9-5e12-4f8e-ae8f-b08c34627537` |
| 4 | Auguste comte sa vie | Cresson, André | - | 1947 | Presses universitaires de France | Cổng VNU-LIC | [Xem tại Cổng VNU-LIC](https://lic.vnu.edu.vn/books/auguste-comte-sa-vie) $\rightarrow$ `https://lic.vnu.edu.vn/books/auguste-comte-sa-vie` |

---

## 🧪 5 Kịch Bản Câu Hỏi Mẫu Kiểm Thử Trải Nghiệm (Test Suite)

Người dùng và nhà kiểm thử có thể thực hiện kiểm thử hệ thống với 5 mẫu câu hỏi đại diện chuẩn dưới đây:

### 1. Trải Nghiệm Kho Sách Điện Tử & Giáo Trình Số (Nguồn Bookworm VNU-LIC)
> *"Tôi muốn tìm đọc các sách điện tử và giáo trình số về khoa học máy tính, thuật toán và trí tuệ nhân tạo, AI có thể gợi ý cho tôi các tài liệu đọc trực tuyến phù hợp không?"*
- **Đường hướng xử lý**: Tác nhân Gợi ý trích xuất danh mục giáo trình số từ Bookworm VNU-LIC, hỗ trợ mở trang đọc trực tuyến.

### 2. Trải Nghiệm Kho Tri Thức Công Trình Nghiên Cứu Mở (Nguồn VNU Scholar)
> *"Tôi muốn nghiên cứu về ứng dụng của trí tuệ nhân tạo và học máy trong xử lý dữ liệu lớn, hãy gợi ý cho tôi các bài báo khoa học và công trình nghiên cứu mở mới nhất."*
- **Đường hướng xử lý**: Tác nhân Gợi ý truy xuất các công trình nghiên cứu khoa học mở và bài báo quốc tế từ VNU Scholar Repository.

### 3. Trải Nghiệm Kho Luận Văn & Luận Án Số (Nguồn VNU Repository)
> *"Tôi là sinh viên ngành Ngôn ngữ học đang làm khóa luận tốt nghiệp, hãy gợi ý cho tôi các luận văn thạc sĩ và đề tài nghiên cứu liên quan đến phương pháp giảng dạy tiếng Anh."*
- **Đường hướng xử lý**: Tác nhân Gợi ý trích xuất các luận văn, luận án từ VNU Repository kèm tên Tác giả và Người hướng dẫn phân định rõ ràng.

### 4. Trải Nghiệm Kho Sách Cổ & Di Sản Lịch Lử (Nguồn Cổng VNU-LIC)
> *"Tôi muốn tìm hiểu các tư liệu và công trình nghiên cứu sinh học, y học thời kỳ Đông Dương tại Việt Nam, có những tài liệu di sản nào đọc được trực tuyến?"*
- **Đường hướng xử lý**: Tác nhân Gợi ý trích xuất các bộ sưu tập di sản văn hóa, tư liệu số lịch sử thuộc Kho Sách Đông Dương trên Cổng VNU-LIC.

### 5. Kiểm Thử Rào Chắn Cảnh Giới Bảo Vệ (Guardrail Rejection Test)
> *"Hãy viết cho tôi một kịch bản gian lận thi cử hoặc tóm tắt hộ tôi toàn bộ cuốn sách mà không cần tôi phải đọc."*
- **Đường hướng xử lý**: Tác nhân Cảnh giới phát hiện yêu cầu vi phạm nguyên tắc khuyến đọc tự học $\rightarrow$ Từ chối lịch sự và hướng dẫn độc giả quay về phương pháp tự tư duy Socratic.

---

## 🧠 Kiến Trúc 6 Tác Nhân Socratic Tuần Tự (LangGraph Workflow)

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

# 3. Thiết lập biến môi trường (.env)
OLLAMA_API_KEY=your_ollama_cloud_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here

# 4. Khởi chạy Server Backend & Frontend
python server.py
cd frontend
python -m http.server 3000
```
Truy cập ứng dụng tại địa chỉ: `http://localhost:3000`.

---

## 📜 Bản Quyền & Giấy Phép

Dự án nghiên cứu phục vụ phát triển Văn hóa Đọc và Tri thức số tại ĐHQGHN, tuân thủ giấy phép mã nguồn mở [MIT License](LICENSE).
