# Dữ liệu dùng thử LAN-LMS

## Bộ kiểm thử toàn hệ thống

Chạy `KIEM_THU_TOAN_BO.bat` ở thư mục gốc để mở môi trường riêng tại
**http://127.0.0.1:8081**. Admin: `testadmin / 111111`; sinh viên chính:
`DEMO001 / 111111`. Bộ dữ liệu đã được tạo trong `full-system/`.

Xem [hướng dẫn tài khoản, tệp và checklist từng chức năng](FULL_SYSTEM_TEST_GUIDE.md)
và [liên kết trực tiếp theo tình huống](full-system/SCENARIOS.md).
Môi trường này không thay thế dữ liệu đang sử dụng ở cổng 8080.

## Bản chụp dữ liệu cũ

`lan-lms-data.zip` chứa bản chụp SQLite, tài liệu, đề và các file bài nộp tại thời điểm xuất. Bản chụp có tài khoản và dữ liệu khóa học; phiên đăng nhập, bộ đếm đăng nhập và nhật ký kiểm toán đã được xóa khỏi bản chia sẻ.

Trên máy mới, dừng server, sao lưu các thư mục dữ liệu hiện có nếu cần, rồi giải nén file ZIP vào thư mục gốc project. Các đường dẫn `data`, `learning-files`, `de-thi`, `submissions` và `programming-submissions` trong file ZIP phải nằm trực tiếp dưới thư mục project. Thao tác giải nén có thể ghi đè dữ liệu hiện có. Sau đó chạy lại server và đăng nhập.
