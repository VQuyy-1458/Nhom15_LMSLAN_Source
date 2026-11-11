# Đường dẫn kiểm thử theo bộ dữ liệu đã tạo

Tạo lúc: 2026-11-12T00:11:03+07:00. Mật khẩu mẫu: `111111`.

Chạy `KIEM_THU_TOAN_BO.bat` từ thư mục gốc. Đăng nhập Admin và sinh viên bằng hai trình duyệt hoặc cửa sổ riêng tư.

| Tình huống | Đường dẫn / tài khoản |
|---|---|
| Đăng nhập quản trị | http://127.0.0.1:8081/login · `testadmin` |
| Khóa chính, có đủ nội dung | http://127.0.0.1:8081/admin/courses?course=demo-v1-network |
| Nội dung theo tuần | http://127.0.0.1:8081/student/courses?course=demo-v1-network&tab=weekly · `DEMO001` |
| Khóa đã tổng kết | http://127.0.0.1:8081/student/courses?course=demo-v1-completed&tab=grades · `DEMO001` |
| Khóa rỗng | http://127.0.0.1:8081/admin/courses?course=ca758d67761c511ab996 |
| Đã hết 3 lượt nộp | http://127.0.0.1:8081/student/assignments?course=demo-v1-network · `DEMO004`, bài `Bài tập 04 – Truyền file an toàn trong mạng LAN` |
| Editor kỳ thi code đang mở | http://127.0.0.1:8081/student/exams?exam=dd3985c51f4d4faaa761e61059a71110 · `DEMO001` |
| Lịch sử code dựng sẵn | http://127.0.0.1:8081/admin?section=exam&exam=e8aa9c6449e2426b8d579467db7d6225 |
| Điểm 0, tên dài, dữ liệu rỗng | `TESTZERO`, `TESTLONG`, `TESTEMPTY` |

Tệp nộp, mã nguồn, dữ liệu import hợp lệ/không hợp lệ ở `test-inputs/`.
Xem hướng dẫn đầy đủ tại `../FULL_SYSTEM_TEST_GUIDE.md`.

Thời gian tiếp tục chạy theo server thật: phiên thi khoảng 3 giờ, điểm danh khoảng 2 giờ; sau đó trở thành trạng thái hết hạn. Muốn một lượt hoàn toàn mới, chạy module với `--root` trỏ một thư mục mới.
