<h1 align="center">Hệ thống phân tích chiến lược kiến trúc và tự động hóa báo cáo doanh nghiệp dựa trên Multi-Agent</h1>

<p align="center">
  <img src="https://img.shields.io/badge/License-MIT-blue" alt="License">
  <img src="https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.110%2B-009688?logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/LangGraph-orchestrator-121212" alt="LangGraph">
  <img src="https://img.shields.io/badge/BM25-RAG%20Search-orange" alt="BM25">
  <img src="https://img.shields.io/badge/KaTeX-LaTeX%20rendering-4285f4" alt="KaTeX">
  <img src="https://img.shields.io/badge/Mermaid-diagram%20engine-ff6f00" alt="Mermaid">
</p>

<p align="center">
  Giải pháp tự động hóa tư vấn công nghệ thông tin và chuyển đổi số cho doanh nghiệp sử dụng kiến trúc đa tác nhân (Multi-Agent) thông minh kết hợp cơ chế truy xuất tri thức (BM25 RAG) và định tuyến động. Dự án giải quyết bài toán tối ưu hóa quy trình tiền khả thi (Pre-sales), phá vỡ các rào cản thông tin nội bộ và tự động hóa việc biên soạn báo cáo kỹ thuật chuẩn chỉnh.
</p>

---

<h2 align="center">Kiến trúc hệ thống và luồng điều phối đa tác nhân</h2>

<p align="center">
  Hệ thống được thiết kế theo mô hình phân tách độc lập giữa dịch vụ máy chủ Backend (FastAPI xử lý đồ thị AI) và giao diện người dùng Frontend (Dashboard hiển thị trực quan). Mọi luồng tính toán đều được điều khiển bởi đồ thị trạng thái tuần tự LangGraph, cho phép quản lý trạng thái phiên làm việc (Stateful Session) thông qua cấu trúc dữ liệu chung <code>ResearchState</code>.
</p>

### 1. Cơ chế định tuyến động (Dynamic Routing)

```mermaid
flowchart TD
    Input(["Câu hỏi đầu vào"]) --> Guardrail["Tác nhân Lọc Ngữ Cảnh"]
    Guardrail --> Decision{"Kết quả phân loại"}
    Decision -- "Irrelevant" --> End1(["END - Từ chối<br/>1/6 Tác nhân"])
    Decision -- "Relevant + Đơn giản" --> Researcher1["Tác nhân Nghiên Cứu"]
    Decision -- "Relevant + Phức tạp" --> Researcher2["Tác nhân Nghiên Cứu"]
    Researcher1 --> Reporter1["Tác nhân Biên Soạn"]
    Reporter1 --> End2(["END - Q&A Flow<br/>3/6 Tác nhân"])
    Researcher2 --> Analyst["Tác nhân Phân Tích"]
    Analyst --> Risk["Tác nhân Kiểm Soát Rủi Ro"]
    Risk --> Recommender["Tác nhân Đề Xuất"]
    Recommender --> Reporter2["Tác nhân Biên Soạn"]
    Reporter2 --> End3(["END - Strategic Flow<br/>6/6 Tác nhân"])

    style Input fill:#ffffff,stroke:#333333,color:#1a1a1a
    style Guardrail fill:#ffffff,stroke:#e91e63,color:#1a1a1a
    style Decision fill:#ffffff,stroke:#333333,color:#1a1a1a
    style End1 fill:#ffebee,stroke:#ef4444,color:#1a1a1a
    style End2 fill:#e8f5e9,stroke:#4caf50,color:#1a1a1a
    style End3 fill:#e3f2fd,stroke:#2196f3,color:#1a1a1a
    style Researcher1 fill:#ffffff,stroke:#2196f3,color:#1a1a1a
    style Researcher2 fill:#ffffff,stroke:#2196f3,color:#1a1a1a
    style Analyst fill:#ffffff,stroke:#9c27b0,color:#1a1a1a
    style Risk fill:#ffffff,stroke:#ff9800,color:#1a1a1a
    style Recommender fill:#ffffff,stroke:#4caf50,color:#1a1a1a
    style Reporter1 fill:#ffffff,stroke:#00bcd4,color:#1a1a1a
    style Reporter2 fill:#ffffff,stroke:#00bcd4,color:#1a1a1a
```

Tùy thuộc vào câu hỏi đầu vào của người dùng, bộ định tuyến có điều kiện (Conditional Router) sẽ tự động phân tích độ phức tạp để phân nhánh xử lý:
- **Nhánh từ chối (Rejection Flow)**: Chặn ngay lập tức tại tác nhân lọc ngữ cảnh nếu câu hỏi không thuộc phạm vi công nghệ hoặc vận hành doanh nghiệp — chỉ sử dụng 1/6 tác nhân.
- **Nhánh Hỏi-Đáp đơn giản (Q&A Flow)**: Bỏ qua các bước phân tích sâu và đi thẳng từ Tác nhân Nghiên cứu đến Tác nhân Biên soạn báo cáo nhằm rút ngắn thời gian xử lý và tiết kiệm chi phí vận hành API — chỉ sử dụng 3/6 tác nhân.
- **Nhánh phân tích chiến lược (Strategic Flow)**: Kích hoạt tuần tự toàn bộ 6 tác nhân AI để tiến hành so sánh đối chiếu kiến trúc, đánh giá rủi ro an ninh mạng và lập lộ trình triển khai chi tiết kèm KPI — sử dụng 6/6 tác nhân.

### 2. Vai trò của các tác nhân chuyên biệt trong quy trình tư vấn

| Tác nhân | Vai trò | Màu nhận diện |
|----------|---------|---------------|
| Lọc Ngữ Cảnh (Guardrail Agent) | Xác thực ngữ cảnh câu hỏi đầu vào, lập luận và phân loại tính hợp lệ, định tuyến luồng xử lý phù hợp | Hồng |
| Nghiên Cứu (Researcher Agent) | Truy xuất tri thức qua BM25 Search, tổng hợp tài liệu thực tế từ cơ sở dữ liệu nội bộ | Xanh dương |
| Phân Tích (Analyst Agent) | Phân tích ưu và nhược điểm, xây dựng ma trận đánh đổi đa chiều, so sánh phương án kiến trúc | Tím |
| Kiểm Soát Rủi Ro (Risk Assessor Agent) | Nhận diện rủi ro kỹ thuật và vận hành, thiết lập ma trận phân loại mức độ rủi ro theo chuẩn FPT Secure-First | Cam |
| Đề Xuất (Recommender Agent) | Hoạch định kế hoạch triển khai chi tiết qua từng giai đoạn, xác định các chỉ số KPI đo lường hiệu quả | Xanh lá |
| Biên Soạn (Reporter Agent) | Tổng hợp dữ liệu từ các tác nhân trước, biên soạn báo cáo hoàn chỉnh Markdown + LaTeX, kết xuất sơ đồ kiến trúc Mermaid tự động | Xanh lục |

---

<h2 align="center">Sơ đồ cơ chế kỹ thuật cốt lõi</h2>

### 1. Cơ chế truy xuất tri thức (BM25 RAG)

```mermaid
flowchart LR
    Query(["Câu hỏi"]) --> Tokenize["Tách từ khóa"]
    Tokenize --> BM25[("CustomBM25<br/>In-Memory Search")]
    BM25 --> Rank["Xếp hạng relevance"]
    Rank --> Context["Ngữ cảnh tối ưu"]
    Context --> Agent["Tác nhân Nghiên Cứu"]

    style Query fill:#ffffff,stroke:#333333,color:#1a1a1a
    style Tokenize fill:#ffffff,stroke:#2196f3,color:#1a1a1a
    style BM25 fill:#ffffff,stroke:#ff9800,color:#1a1a1a
    style Rank fill:#ffffff,stroke:#9c27b0,color:#1a1a1a
    style Context fill:#ffffff,stroke:#4caf50,color:#1a1a1a
    style Agent fill:#ffffff,stroke:#2196f3,color:#1a1a1a
```

Nhằm khắc phục hiện tượng ảo tưởng của mô hình ngôn ngữ lớn (LLM Hallucination), hệ thống sử dụng cơ chế truy xuất tri thức dựa trên thuật toán BM25 (Best Matching 25) chạy hoàn toàn trong bộ nhớ. Tài liệu nội bộ FPT được chia nhỏ (chunking) bằng RecursiveCharacterTextSplitter, sau đó lập chỉ mục và tìm kiếm theo từ khóa với hỗ trợ tiếng Việt. Phương pháp này đảm bảo tốc độ truy xuất nhanh chóng, không phụ thuộc dịch vụ bên ngoài, và hoạt động ổn định kể cả khi không có kết nối mạng.

### 2. Luồng streaming dữ liệu thời gian thực (FastAPI SSE)

```mermaid
sequenceDiagram
    participant Client as Giao diện Dashboard
    participant Server as FastAPI SSE Server
    participant Graph as LangGraph Engine
    participant LLM as Mô hình ngôn ngữ

    Client->>Server: POST /api/run (JSON body)
    Server->>Graph: Khởi tạo đồ thị trạng thái
    loop Mỗi tác nhân hoạt động
        Graph->>LLM: Gửi prompt + ngữ cảnh
        loop Từng token sinh ra
            LLM-->>Graph: Trả token
            Graph-->>Server: SSE: node_start + token
            Server-->>Client: SSE event (text/event-stream)
            Client->>Client: Hiển thị real-time từng ký tự
        end
        Graph-->>Server: SSE: node_end (thời gian, token, tok/s)
        Server-->>Client: Cập nhật chỉ số tác nhân
    end
    Graph-->>Server: SSE: done (báo cáo + sơ đồ)
    Server-->>Client: Hoàn tất - Xuất báo cáo & sơ đồ
```

Hệ thống sử dụng giao thức Server-Sent Events (SSE) thông qua yêu cầu POST (bảo mật — không lộ dữ liệu trong URL) để truyền tải trực tiếp kết quả suy luận của từng Agent dưới dạng luồng dữ liệu thời gian thực về Frontend. Khác với các chatbot thông thường trả kết quả một lần, hệ thống hiển thị từng ký tự khi mô hình sinh ra, cho phép người dùng theo dõi tiến trình xử lý ngay lập tức mà không cần chờ đợi.

### 3. Cơ chế dự phòng mô hình tự động (Fast Fallback)

```mermaid
flowchart TD
    Start(["Bắt đầu Node"]) --> Primary["Mô hình chính"]
    Primary --> Check1{"Phản hồi thành công?"}
    Check1 -- "Thành công" --> Done(["Hoàn thành<br/>Lưu trạng thái"])
    Check1 -- "Lỗi / Timeout" --> CheckHealth{"Kiểm tra sức khỏe<br/>mô hình dự phòng"}
    CheckHealth -- "Ưu tiên độ trễ thấp" --> Fallback1["Mô hình dự phòng 1<br/>Độ trễ thấp nhất"]
    CheckHealth -- "Ưu tiên thứ 2" --> Fallback2["Mô hình dự phòng 2"]
    CheckHealth -- "Ưu tiên thứ 3" --> Fallback3["Mô hình dự phòng 3"]
    Fallback1 --> Done
    Fallback2 --> Done
    Fallback3 --> Done

    style Start fill:#ffffff,stroke:#333333,color:#1a1a1a
    style Primary fill:#ffffff,stroke:#2196f3,color:#1a1a1a
    style Check1 fill:#ffffff,stroke:#333333,color:#1a1a1a
    style CheckHealth fill:#ffffff,stroke:#333333,color:#1a1a1a
    style Done fill:#e8f5e9,stroke:#4caf50,color:#1a1a1a
    style Fallback1 fill:#ffffff,stroke:#ff9800,color:#1a1a1a
    style Fallback2 fill:#ffffff,stroke:#ff9800,color:#1a1a1a
    style Fallback3 fill:#ffffff,stroke:#ff9800,color:#1a1a1a
```

Cấu hình kết nối mô hình được tích hợp cơ chế dự phòng nhanh để đảm bảo độ tin cậy và sẵn sàng cao. Hệ thống kiểm tra sức khỏe và độ trễ của các mô hình định kỳ mỗi 5 phút, tự động chọn mô hình khỏe nhất làm chính và sắp xếp thứ tự dự phòng theo độ trễ tăng dần. Khi mô hình chính gặp lỗi hoặc timeout, hệ thống ngay lập tức chuyển sang mô hình dự phòng tiếp theo mà không làm gián đoạn trải nghiệm người dùng.

---

<h2 align="center">Tính năng nổi bật của giao diện Dashboard</h2>

### 1. Báo cáo trực quan với LaTeX + Xuất HTML/SVG

<p align="center">
  Hệ thống tích hợp thư viện <strong>KaTeX</strong> để render công thức toán học LaTeX trực tiếp trong báo cáo, biến các biểu thức phức tạp thành nội dung trực quan ngay trên trình duyệt. Người dùng có thể xuất báo cáo hoàn chỉnh dưới dạng file <strong>HTML độc lập</strong> (kèm LaTeX, bảng biểu, định dạng chuyên nghiệp) hoặc xuất sơ đồ kiến trúc dưới dạng file <strong>SVG/PNG</strong> chất lượng cao để nhúng vào tài liệu.
</p>

### 2. Nút trạng thái kết nối Online/Offline

<p align="center">
  Do Frontend triển khai trên Vercel chỉ hiển thị giao diện tĩnh, hệ thống cần kết nối đến Backend API trên Render để xử lý AI. Chấm trạng thái kết nối tự động kiểm tra sức khỏe server: <strong>xanh lá (Online)</strong> khi máy chủ Render đang hoạt động, <strong>đỏ (Offline)</strong> khi không thể kết nối. Cơ chế auto-detect tự động phân biệt môi trường localhost và production.
</p>

### 3. Sơ Đồ Phối Hợp Tác Nhân — Hiệu ứng phát sáng theo thời gian thực

<p align="center">
  Sơ đồ trực quan hiển thị 6 tác nhân dưới dạng pipeline kết nối bằng mũi tên. Khi một tác nhân bắt đầu hoạt động, node tương ứng sẽ <strong>phát sáng (active)</strong> với màu đặc trưng; khi hoàn thành sẽ chuyển sang trạng thái <strong>đã xử lý (completed)</strong>. Mỗi tác nhân hiển thị chi tiết: <strong>mô hình sử dụng, thời gian xử lý (giây), tốc độ (tok/s), tổng token tiêu thụ</strong>. Các tác nhân không được kích hoạt sẽ ẩn đi hoặc hiển thị mờ, giúp người dùng nắm bắt ngay lập tức lộ trình xử lý.
</p>

### 4. Nhật Ký Xử Lý Thời Gian Thực — Streaming từng ký tự

<p align="center">
  Nhật ký hiển thị chi tiết quá trình làm việc của từng tác nhân theo thời gian thực. Khác với các chatbot thông thường trả kết quả một lần, hệ thống <strong>stream từng ký tự</strong> khi mô hình sinh ra, tạo trải nghiệm tương tác sống động. Mỗi tác nhân hiển thị riêng biệt: <strong>Quá trình suy nghĩ (Thinking Process)</strong> — phần lập luận nội bộ của mô hình, và <strong>Câu trả lời thực tế</strong> — nội dung chính thức được xuất ra. Cơ chế section detection tự động phân tách Thinking, Console Message, Detailed Report, Mermaid Diagram và Diagram Explanation.
</p>

### 5. Chỉ Số Vận Hành — Thống kê toàn diện

<p align="center">
  Bảng thống kê tổng hợp hiển thị 4 chỉ số cốt lõi: <strong>Thời gian xử lý tổng</strong>, <strong>Tổng token tiêu thụ</strong>, <strong>Tác nhân đã xử lý</strong> (x/6, tự động điều chỉnh theo luồng: 1/6, 3/6 hoặc 6/6), và <strong>Trạng thái</strong> (Sẵn sàng / Đang xử lý / Hoàn Thành / Bị Từ Chối). Các chỉ số cập nhật liên tục theo thời gian thực khi từng tác nhân hoàn thành công việc.
</p>

---

<h2 align="center">Hướng dẫn cài đặt và vận hành dành cho nhà phát triển</h2>

### 1. Thiết lập môi trường ảo và cài đặt thư viện
```bash
# Tạo môi trường ảo và kích hoạt trên Windows
python -m venv .venv
.venv\Scripts\activate

# Tạo môi trường ảo và kích hoạt trên Linux / macOS
python -m venv .venv
source .venv/bin/activate

# Cài đặt các thư viện phụ thuộc
pip install -r requirements.txt
```

### 2. Cấu hình biến môi trường
Tạo một tệp tin đặt tên là `.env` tại thư mục gốc của dự án với cấu trúc như sau:
```env
OLLAMA_API_KEY=thong_tin_api_key_cua_ban
OLLAMA_BASE_URL=https://ollama.com/v1
```
*(Tệp tin `.env` đã được cấu hình trong `.gitignore` để tránh đẩy lên các hệ thống quản lý mã nguồn công khai, giúp bảo vệ khóa truy cập).*

### 3. Khởi chạy máy chủ API
Khởi chạy dịch vụ backend FastAPI lắng nghe tại cổng `8000`:
```bash
python main.py --server
```

### 4. Chạy kiểm thử tự động (RAG Testing)
Hệ thống tích hợp sẵn kịch bản kiểm thử tự động giúp kiểm tra độ chính xác của cơ chế RAG (BM25 Search):
```bash
.venv\Scripts\python.exe tests/test_rag.py
```

### 5. Hướng dẫn triển khai đám mây (Vercel & Render)
Để hệ thống hoạt động 24/7 độc lập và gọi trực tiếp tới API Ollama mà không phụ thuộc vào máy tính cá nhân của bạn:

#### A. Triển khai Frontend lên Vercel
1. Đăng nhập [Vercel](https://vercel.com) bằng tài khoản GitHub của bạn.
2. Tạo dự án mới, chọn repo `fpt-multi-agent-system`.
3. Chỉ định thư mục chạy chính (Root Directory) là thư mục `frontend/` của dự án.
4. Nhấn **Deploy** để nhận đường link giao diện HTTPS miễn phí.

#### B. Triển khai Backend lên Render
1. Tạo một **Web Service** mới trên [Render](https://render.com) liên kết với repo GitHub của bạn.
2. Cấu hình các thông số môi trường chuẩn xác:
   - **Language:** `Python`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn server:app --host 0.0.0.0 --port $PORT`
3. Thêm 2 biến môi trường tại mục **Environment Variables** để cấu hình API Key:
   - `OLLAMA_API_KEY`: *Khóa API của bạn*.
   - `OLLAMA_BASE_URL`: *Đường dẫn API Ollama của bạn* (mặc định: `https://ollama.com/v1`).
4. Chờ Render khởi chạy xong, hệ thống sẽ tự động kết nối tới địa chỉ Backend Render thông qua cơ chế auto-detect.

---

<h2 align="center">Quy trình xử lý thực tế qua các ảnh chụp màn hình</h2>

### Ảnh 1: Giao diện trạng thái Sẵn Sàng — Tab Báo Cáo Chi Tiết
<p align="center">
  Màn hình ghi nhận trạng thái ban đầu của hệ thống khi chưa nhận yêu cầu phân tích. Sơ Đồ Phối Hợp Tác Nhân hiển thị 6 tác nhân với chỉ số ban đầu (0.000s | 0 tk), Nhật Ký Xử Lý Thời Gian Thực hiển thị trạng thái "CHỜ LỆNH" kèm mô tả chi tiết chức năng từng tác nhân, Chỉ Số Vận Hành hiển thị trạng thái "Sẵn sàng" (0/6 tác nhân). Tab Báo Cáo Chi Tiết hiển thị thông báo "BÁO CÁO CHƯA ĐƯỢC TẠO", sẵn sàng nhận yêu cầu đầu vào.
</p>
<p align="center">
  <img src="docs/images/screenshot1.jpg" alt="Trạng thái Sẵn Sàng — Báo Cáo Chi Tiết" width="85%">
</p>

### Ảnh 2: Giao diện trạng thái Sẵn Sàng — Tab Sơ Đồ Quy Trình
<p align="center">
  Cùng trạng thái chờ lệnh, chuyển sang tab Sơ Đồ Quy Trình hiển thị thông báo "SƠ ĐỒ CHƯA ĐƯỢC TẠO". Nhật Ký Xử Lý mô tả chi tiết quy trình phối hợp 6 tác nhân chuyên biệt: từ xác thực đầu vào (Lọc Ngữ Cảnh), truy xuất tri thức qua BM25 Search (Nghiên Cứu), xây dựng ma trận so sánh đa chiều (Phân Tích), nhận diện rủi ro theo chuẩn FPT Secure-First (Kiểm Soát Rủi Ro), thiết lập lộ trình đa giai đoạn kèm KPI (Đề Xuất), đến biên soạn báo cáo học thuật và trực quan hóa sơ đồ Mermaid (Biên Soạn Báo Cáo).
</p>
<p align="center">
  <img src="docs/images/screenshot2.jpg" alt="Trạng thái Sẵn Sàng — Sơ Đồ Quy Trình" width="85%">
</p>

### Ảnh 3: Giao diện từ chối câu hỏi ngoài phạm vi (Rejection Flow) — Tab Báo Cáo Chi Tiết
<p align="center">
  Màn hình ghi nhận hành vi từ chối khi người dùng đặt câu hỏi không thuộc phạm vi chuyên môn: "Món phở nào ngon nhất ở Hà Nội?". Tác nhân Lọc Ngữ Cảnh xác định truy vấn không hợp lệ với chỉ số 9.878s | 105.0 tk/s | 1,036 token. Nhật Ký Xử Lý hiển thị nhãn "AGENT CẢNH GIỚI" kèm quá trình suy nghĩ (Thinking Process) giải thích chi tiết lý do từ chối. Cơ chế định tuyến thông minh tự động dừng xử lý ngay tại Guardrail Agent — chỉ 1/6 tác nhân hoạt động, trạng thái "Bị Từ Chối". Tab Báo Cáo Chi Tiết hiển thị thẻ từ chối với tiêu đề "BÁO CÁO KHÔNG ÁP DỤNG".
</p>
<p align="center">
  <img src="docs/images/screenshot3.jpg" alt="Từ chối câu hỏi ngoài phạm vi — Báo Cáo" width="85%">
</p>

### Ảnh 4: Giao diện từ chối câu hỏi ngoài phạm vi (Rejection Flow) — Tab Sơ Đồ Quy Trình
<p align="center">
  Cùng truy vấn bị từ chối, chuyển sang tab Sơ Đồ Quy Trình hiển thị thẻ từ chối với tiêu đề "SƠ ĐỒ KHÔNG ÁP DỤNG". Nhật Ký Xử Lý thể hiện rõ cơ chế Định Tuyến Thông Minh: hệ thống tự động phát hiện yêu cầu không thuộc phạm vi hỗ trợ nên toàn bộ 5 tác nhân tiếp theo không được sử dụng, giúp tối ưu hóa hiệu suất bằng cách xử lý ngay lập tức tại Lọc Ngữ Cảnh để tránh lãng phí tài nguyên. Sơ đồ phối hợp chỉ có Lọc Ngữ Cảnh phát sáng, 5 tác nhân còn lại đều hiển thị 0.000s | 0 tk.
</p>
<p align="center">
  <img src="docs/images/screenshot4.jpg" alt="Từ chối câu hỏi ngoài phạm vi — Sơ Đồ" width="85%">
</p>

### Ảnh 5: Giao diện luồng Hỏi-Đáp đơn giản (Q&A Flow) — Tab Báo Cáo Chi Tiết
<p align="center">
  Màn hình ghi nhận hành vi của hệ thống khi xử lý câu hỏi đơn giản thuộc luồng Hỏi-Đáp. Bộ định tuyến có điều kiện nhận diện truy vấn không yêu cầu phân tích chiến lược sâu, tự động rút gọn đồ thị chỉ kích hoạt 3/6 tác nhân (Lọc Ngữ Cảnh → Nghiên Cứu → Biên Soạn) thay vì toàn bộ 6 tác nhân. Điều này giúp rút ngắn thời gian xử lý xuống 69.6 giây và tiết kiệm chi phí vận hành API đáng kể. Tab Báo Cáo Chi Tiết hiển thị kết quả nghiên cứu dạng Q&A với nội dung trả lời trực tiếp, chính xác câu hỏi đầu vào.
</p>
<p align="center">
  <img src="docs/images/screenshot5.jpg" alt="Luồng Hỏi-Đáp đơn giản — Báo Cáo" width="85%">
</p>

### Ảnh 6: Giao diện luồng Hỏi-Đáp đơn giản (Q&A Flow) — Tab Sơ Đồ Quy Trình
<p align="center">
  Cùng truy vấn Hỏi-Đáp, chuyển sang tab Sơ Đồ Quy Trình hiển thị sơ đồ kiến trúc quy trình trực quan kèm mô tả chi tiết. Sơ đồ phối hợp tác nhân cho thấy rõ luồng dữ liệu đi qua 3 tác nhân đã kích hoạt (màu sắc nổi bật) so với 3 tác nhân bị bỏ qua (màu xám), minh họa trực quan cơ chế định tuyến động giúp người dùng nắm bắt ngay lập tức lộ trình xử lý của hệ thống.
</p>
<p align="center">
  <img src="docs/images/screenshot6.jpg" alt="Luồng Hỏi-Đáp đơn giản — Sơ Đồ" width="85%">
</p>

### Ảnh 7: Giao diện luồng phân tích chiến lược đầy đủ (Strategic Flow) — Tab Báo Cáo Chi Tiết
<p align="center">
  Màn hình ghi nhận toàn bộ quy trình phân tích chiến lược khi người dùng đặt câu hỏi phức tạp yêu cầu so sánh kiến trúc công nghệ và đề xuất lộ trình triển khai. Bộ định tuyến kích hoạt tuần tự toàn bộ 6/6 tác nhân AI: Lọc Ngữ Cảnh → Nghiên Cứu → Phân Tích → Kiểm Soát Rủi Ro → Đề Xuất → Biên Soạn. Sơ đồ phối hợp tác nhân hiển thị chi tiết thời gian xử lý, tốc độ token và số token tiêu thụ của từng tác nhân. Tab Báo Cáo Chi Tiết trình bày báo cáo chiến lược hoàn chỉnh bao gồm bối cảnh doanh nghiệp, phân tích rủi ro kỹ thuật, lộ trình triển khai 4 giai đoạn và KPI đo lường hiệu quả.
</p>
<p align="center">
  <img src="docs/images/screenshot7.jpg" alt="Luồng phân tích chiến lược — Báo Cáo" width="85%">
</p>

### Ảnh 8: Giao diện luồng phân tích chiến lược đầy đủ (Strategic Flow) — Tab Sơ Đồ Quy Trình
<p align="center">
  Cùng truy vấn phân tích chiến lược, chuyển sang tab Sơ Đồ Quy Trình hiển thị sơ đồ kiến trúc hệ thống trực quan kèm mô tả chi tiết từng thành phần. Sơ đồ phối hợp tác nhân cho thấy toàn bộ 6 tác nhân đều đã kích hoạt thành công với màu sắc phân biệt rõ ràng, minh họa luồng xử lý hoàn chỉnh từ lọc ngữ cảnh đến biên soạn báo cáo cuối cùng. Tổng thời gian xử lý 278.6 giây với 32,618 token tiêu thụ, phản ánh độ phức tạp và chiều sâu của phân tích chiến lược đa chiều.
</p>
<p align="center">
  <img src="docs/images/screenshot8.jpg" alt="Luồng phân tích chiến lược — Sơ Đồ" width="85%">
</p>

### Ảnh 9: Nội dung báo cáo chiến lược chi tiết — Tác nhân Biên Soạn xuất báo cáo hoàn chỉnh
<p align="center">
  Màn hình hiển thị nội dung báo cáo nghiên cứu chiến lược "FPT SOFTWARE AI-FIRST" do Tác nhân Biên Soạn tổng hợp từ kết quả của toàn bộ 5 tác nhân trước đó. Báo cáo được trình bày theo cấu trúc học thuật chuyên nghiệp bao gồm: phần giới thiệu chung và tổng hợp vai trò 6 tác nhân chuyên biệt, mô tả chi tiết từng tác nhân từ Lọc Ngữ Cảnh (Guardrail Agent) đến Đánh Giá Rủi Ro (Risk Assessor Agent) với giải thích rõ ràng chức năng và trách nhiệm của từng thành phần trong quy trình tư vấn tự động hóa. Công thức LaTeX và định dạng Markdown được render trực tiếp qua KaTeX, đảm bảo nội dung kỹ thuật hiển thị chính xác và trực quan trên trình duyệt.
</p>
<p align="center">
  <img src="docs/images/screenshot9.png" alt="Nội dung báo cáo chiến lược chi tiết" width="85%">
</p>

### Ảnh 10: Sơ đồ kiến trúc hiện đại hóa hệ thống Legacy — Xuất từ Tác nhân Biên Soạn
<p align="center">
  Màn hình hiển thị sơ đồ kiến trúc quy trình hiện đại hóa hệ thống Legacy (Monolithic) do Tác nhân Biên Soạn tự động tạo ra dưới dạng Mermaid diagram. Sơ đồ minh họa chi tiết lộ trình chuyển đổi qua 2 giai đoạn: (1) Đánh giá & Chuẩn bị (1-2 tháng) bao gồm Workshop DDD xác định Bounded Context, Phân tích Dependency Mapping và Đánh giá DevOps/SRE Maturity; (2) Triển khai Pilot (3-4 tháng) bao gồm Tách Service Độc Lập, Triển khai API Gateway (Kong) & Service Mesh (Istio) và CI/CD Pipeline (GitLab CI/ArgoCD). Sơ đồ bao gồm vòng lặp phản hồi (feedback loop) "Không" quay lại giai đoạn đánh giá khi pilot chưa đạt yêu cầu, thể hiện tính lặp và cải tiến liên tục của quy trình chuyển đổi.
</p>
<p align="center">
  <img src="docs/images/screenshot10.png" alt="Sơ đồ kiến trúc hiện đại hóa Legacy" width="85%">
</p>
