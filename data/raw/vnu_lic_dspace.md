# Kho lưu trữ học thuật DSpace VNU — Tra cứu Luận văn và Nghiên cứu

## DSpace VNU là gì?
DSpace là hệ thống lưu trữ tài liệu học thuật nội sinh (Institutional Repository) của ĐHQGHN, bao gồm:
- Luận văn thạc sĩ, luận án tiến sĩ
- Đề tài nghiên cứu khoa học cấp ĐHQGHN, cấp Nhà nước
- Kỷ yếu hội thảo khoa học
- Bài báo nghiên cứu do tác giả VNU tự lưu trữ (self-archiving)

## Truy cập
- URL giao diện người dùng: https://repository.vnu.edu.vn/
- REST API (DSpace 7): https://repository.vnu.edu.vn/server/api/

## Phân loại tài liệu

### Tài liệu Công cộng (Open Access)
- Truy cập tự do, không cần đăng nhập
- Bao gồm: đề tài NCKH công bố, luận văn được cho phép công khai
- Định dạng: PDF, Word, ZIP

### Tài liệu Có Bản quyền (Restricted Access)
- Yêu cầu đăng nhập qua VNU CAS (Central Authentication Service)
- Sử dụng tài khoản email VNU (username@vnu.edu.vn)
- URL đăng nhập SSO: https://cas.vnu.edu.vn/

## Cách tìm tài liệu

### Tìm bằng giao diện web
1. Truy cập https://repository.vnu.edu.vn/
2. Nhập từ khoá, tên tác giả, hoặc tên tổ chức
3. Dùng bộ lọc: Loại tài liệu, Năm, Đơn vị/Khoa

### Tìm bằng Handle (định danh tài liệu)
- Format: `https://repository.vnu.edu.vn/handle/VNU_123/[ID]`
- Ví dụ hợp lệ:
  - https://repository.vnu.edu.vn/handle/VNU_123/17617
  - https://repository.vnu.edu.vn/handle/VNU_123/18413
- **Lưu ý**: Handle prefix là `VNU_123`, không phải `11122` hay các prefix khác

### Tìm bằng REST API
```
GET https://repository.vnu.edu.vn/server/api/discover/search/objects?query={từ_khoá}&size=5
```
- Trả về JSON chứa metadata tài liệu: title, author, date, handle, uuid
- Trường `dc.identifier.uri` chứa URL handle trực tiếp

## Ghi chú quan trọng
- Trang landing page của handle luôn truy cập được (không cần đăng nhập) để xem metadata
- File PDF full-text có thể yêu cầu xác thực VNU CAS nếu tài liệu bị restrict
- Nếu tài liệu hiển thị "Không tìm thấy tài liệu nào" → handle ID không tồn tại; dùng API search để tìm handle đúng
