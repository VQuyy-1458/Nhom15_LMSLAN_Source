# Bộ dữ liệu thử LAN-LMS

Bộ hiện tại được tạo bằng `app.reset_demo` phiên bản `lan-lms-trial-v3`.
Tài khoản admin và mật khẩu admin hiện có được giữ nguyên. Sinh viên dùng
`SV001` đến `SV020`, mật khẩu ban đầu `111111`.

| Nội dung | Số lượng |
| --- | ---: |
| Khóa học | 4 (Lập trình mạng, Lập trình C++, Cơ sở dữ liệu, Python căn bản đã tổng kết) |
| Sinh viên | 20 |
| Buổi học | 44 |
| Tài liệu | 12 |
| Bài tập file/code | 15 |
| Câu hỏi/đề trong ngân hàng | 6/2 |
| Phiên điểm danh | 21 |
| Kỳ thi | 13 |
| Bản nộp bài tập/thi file | 108/8 |
| Bản code đã chấm thật bằng Docker | 7 |

Đăng nhập `SV001`, mở **Lập trình mạng**. Ở tab **Theo tuần**, chọn tuần để
xem buổi học và tài liệu/bài tập được gắn vào buổi. Câu **Tổng hai số** trong
**Luyện tập** được công khai và không tính điểm. Bài **Thực hành code · Tổng
hai số** có hạn nộp và chấm tự động; các bài tập file có lịch sử nộp/chấm.

Ba kỳ Test đang mở trong Lập trình mạng: nộp file TCP, chấm code stdin/stdout
(phát ngẫu nhiên một trong hai câu), và class/method Python. Hạn thi chung là
24 giờ từ lúc nạp bộ dữ liệu. Kỳ giữa kỳ đã có kết quả code thực tế; kỳ cuối
kỳ là bản nháp để thử cấu hình. Các khóa khác có kỳ thi và lịch sử riêng.

Thư mục `demo-inputs/` có mã nguồn đúng/sai/lỗi, file nộp mẫu, CSV test case,
`LAN_LMS_Test_Kit.zip`, và `demo-inputs/HUONG_DAN.md` với
các bước thử chi tiết. Sinh viên `SV001` chưa điểm danh buổi đang mở: đăng nhập
trong LAN sẽ được tự ghi nhận có mặt và trang giảng viên cập nhật theo phiên.

Để tạo lại bộ này, dừng server rồi chạy:

```powershell
.\.venv-windows\Scripts\python.exe -m app.reset_demo --prepare
.\.venv-windows\Scripts\python.exe -m app.reset_demo --apply <đường-dẫn-staging-vừa-tạo>
```

Lệnh `--apply` chuyển dữ liệu cũ sang `backups/before-trial-reset-*` trước khi
thay thế. Docker Desktop và image `classroom-judge:1` cần hoạt động để tạo các
kết quả chấm thật. Dữ liệu runtime, tài khoản và bài nộp không được đưa lên Git.
