# Dữ liệu dùng thử LAN-LMS

## Bộ kiểm thử toàn hệ thống

Chạy `KIEM_THU_TOAN_BO.bat` ở thư mục gốc để mở môi trường riêng tại
**http://127.0.0.1:8081**. Admin: `testadmin / 111111`; sinh viên chính:
`DEMO001 / 111111`. Bộ dữ liệu đã được tạo trong `full-system/`.

Xem [hướng dẫn tài khoản, tệp và checklist từng chức năng](FULL_SYSTEM_TEST_GUIDE.md)
và [liên kết trực tiếp theo tình huống](full-system/SCENARIOS.md).
Môi trường này không thay thế dữ liệu đang sử dụng ở cổng 8080.

## Bộ 4 khóa học mới (24/11/2026)

`lan-lms-data.zip` hiện chứa 4 lớp C++, Java OOP, Python và Lập trình mạng,
40 sinh viên, lịch và nội dung 7 tuần mỗi lớp, 70 câu trong kho, 12 kỳ thi,
29 phiên thực hành và 80 báo cáo mẫu. Các bài Java OOP hỗ trợ chấm cấu trúc
class/attribute/method và chương trình đầy đủ có `main`.

Tài khoản trong gói: `admin / 111111`; `SV001` đến `SV040 / 111111`.
Đây là tài khoản dùng thử; mật khẩu admin đang sử dụng trên máy xuất không được đưa vào gói.

Trên máy mới chưa có dữ liệu, giải nén ZIP vào thư mục gốc rồi chạy web.
Nếu đã có dữ liệu: dừng server, chuyển nguyên các thư mục `data`, `learning-files`,
`de-thi`, `submissions`, `programming-submissions`, `demo-inputs` vào một thư mục
sao lưu trước khi giải nén. Không giải nén đè lên SQLite cũ: hệ thống ưu tiên SQLite
và sẽ không nhập JSON mới nếu bản ghi cũ vẫn tồn tại.

Các kỳ thi đang mở trong bản chụp có mốc thời gian cố định và sẽ hết hạn.
Dùng các bài luyện tập, hoặc tạo/mở kỳ thi mới trong Cấu hình kỳ thi để thử lại.
Mã mẫu `Main.java`, `Counter.java` nằm trong `demo-inputs` sau khi giải nén.

## Định dạng gói dữ liệu

`lan-lms-data.zip` chứa bản chụp SQLite, tài liệu, đề và các file bài nộp tại thời điểm xuất. Bản chụp có tài khoản và dữ liệu khóa học; phiên đăng nhập, bộ đếm đăng nhập và nhật ký kiểm toán đã được xóa khỏi bản chia sẻ.

Trên máy mới, dừng server, sao lưu các thư mục dữ liệu hiện có nếu cần, rồi giải nén file ZIP vào thư mục gốc project. Các đường dẫn `data`, `learning-files`, `de-thi`, `submissions` và `programming-submissions` trong file ZIP phải nằm trực tiếp dưới thư mục project. Thao tác giải nén có thể ghi đè dữ liệu hiện có. Sau đó chạy lại server và đăng nhập.
