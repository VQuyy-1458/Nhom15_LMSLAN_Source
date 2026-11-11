# Bài mẫu chạy thử Docker

Kho câu hỏi của khóa **Lập trình mạng nâng cao** có 5 bài nháp bắt đầu bằng `[Docker mẫu]`. Mỗi bài có 3 test: 1 test mẫu và 2 test ẩn. Lời giải nằm trong các file `.txt` cùng thư mục này để sao chép vào ô Answer, không phải chạy trực tiếp trên máy chủ.

| Bài | Ngôn ngữ | Dạng | Lời giải |
| --- | --- | --- | --- |
| Tổng hai số | C++ | program | [cpp_program.txt](cpp_program.txt) |
| Product | Java | class | [java_class.txt](java_class.txt) |
| add | Java | method | [java_method.txt](java_method.txt) |
| Counter | C++ | class | [cpp_class.txt](cpp_class.txt) |
| factorial | Python | method | [python_method.txt](python_method.txt) |

1. Mở Docker Desktop, chờ engine sẵn sàng. Cần có image `classroom-judge:1` theo hướng dẫn bộ chấm của dự án.
2. Đăng nhập tài khoản quản lý, mở khóa học → **Bài tập → Kho câu hỏi**.
3. Tìm `[Docker mẫu]`, mở sửa một bài. Trong editor bài toán bấm **Xem trước đề**.
4. Chọn ngôn ngữ tương ứng, sao chép nguyên lời giải từ file trên vào **Answer**, bấm **Chấm thử tất cả test**.
5. Kết quả mong đợi: **AC · 3/3 test · 100/100 điểm**. Lần tạo dữ liệu chỉ kiểm tra cấu hình và dựng wrapper, chưa khẳng định đã chấm Docker thành công.

Để thử WA, thay lời giải Java method bằng `long add(long a, long b) { return 0; }`. Để thử CE, dùng `long add(long a, long b) { return a + ; }`.

Các bài được lưu nháp để sửa và thử nghiệm; chưa phân phối cho sinh viên. Dùng luồng giao bài thực hành hoặc tạo đề thi nếu muốn kiểm tra thêm nộp bài chính thức.

Lệnh bổ sung dữ liệu nếu cần: `python scripts/seed_docker_samples.py`. Script không ghi đè các bài có mã mẫu đã tồn tại; sử dụng lớp lưu trữ của ứng dụng để ghi vào SQLite hiện tại.
