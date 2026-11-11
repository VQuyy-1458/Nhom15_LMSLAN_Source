# Kiểm thử toàn bộ LAN-LMS bằng dữ liệu mẫu

## Chạy ngay trên Windows

1. Mở `KIEM_THU_TOAN_BO.bat` trong thư mục gốc project, giữ cửa sổ này mở.
2. Truy cập **http://127.0.0.1:8081** sau khi server in `Local URL`.
3. Đăng nhập `testadmin` và `DEMO001` bằng hai trình duyệt hoặc cửa sổ riêng tư.

Tất cả tài khoản mẫu có mật khẩu **`111111`**. Dữ liệu nằm riêng trong
`sample-data/full-system/`; server cổng 8080 và dữ liệu gốc không bị ghi đè.
Muốn thử qua LAN, dùng địa chỉ LAN mà server in ra với cổng 8081.

| Tài khoản | Tình huống |
|---|---|
| `testadmin`, `testadmin2` | Hai quản trị viên, thử quản lý và tạo tài khoản |
| `DEMO001` | Nội dung dày, nhiều khóa, bài nộp, lịch sử và thông báo đã đọc/chưa đọc |
| `DEMO002`–`DEMO007` | Lịch sử code lần lượt WA, CE, TLE, MLE, RE, SYSTEM_ERROR; DEMO001 có AC |
| `DEMO004` | Một bài đang mở đã đủ 3 lượt nộp, xem tên bài trong `full-system/SCENARIOS.md` |
| `DEMO020` | Có khóa riêng rỗng học liệu để thử trạng thái chưa có nội dung |
| `DEMO021`–`DEMO045` | Danh sách đông để thử tìm kiếm, chọn nhiều và phân trang |
| `TESTEMPTY` | Chưa tham gia khóa; danh sách khóa, bài tập, thi và điểm rỗng |
| `TESTZERO` | Điểm 0 hợp lệ, phân biệt với chưa có điểm |
| `TESTLONG` | Họ tên dài và nhiều dấu tiếng Việt |
| `TESTLOCKED` | Tài khoản bị khóa; dùng Admin mở khóa rồi đăng nhập lại |
| `TESTTHROTTLE` | Khóa đăng nhập tạm 15 phút từ lúc tạo; dùng Admin gỡ khóa tạm |
| `TESTNEWPASS` | Có cờ yêu cầu đổi mật khẩu, thử luồng bảo mật mà ứng dụng hỗ trợ |

## Nội dung có sẵn

- 12 khóa: khóa chính đủ nội dung, khóa CSDL, khóa đã tổng kết và các khóa
  trống để thao tác thử; có tên dài, học kỳ khác nhau và phân trang.
- 47 bài tập: còn hạn, gần hạn, quá hạn, đã đóng, chưa nộp, đã nộp,
  nộp nhiều lần, hết lượt, đã chấm và đang chờ chấm.
- 14 học liệu: TXT, mã nguồn C++, PDF, PNG, DOCX, ZIP; có tệp thật để tải/xem trước.
- 14 phiên điểm danh có liên kết buổi học; có mặt, muộn, về sớm, vắng,
  không tính điểm, chưa ghi nhận, phiên đang mở và đã đóng.
- 6 tuần học có bài đọc, tài liệu, bài tập và hoạt động code được liên kết.
- 20 câu trong kho: code/file, tự luyện/thực hành/thi, đã công bố, bản nháp,
  lưu trữ; có Java dạng class và chương trình hoàn chỉnh.
- 5 đề tái sử dụng: công bố, bản sao nháp và lưu trữ. Có 3 phiên thực hành:
  code nháp, nộp file đang mở và đã kết thúc.
- Kỳ thi file đang mở; các cấu hình nháp, giữa kỳ, cuối kỳ, lịch tương lai;
  code đang mở theo lịch tự động, code đã kết thúc và cấu hình đã hủy lịch.
- 167 bản ghi kho bài nộp: 144 bài tập, 16 lượt thi file, 7 bài code;
  toàn bộ tệp gốc tồn tại, có thể xem, tải xuống và dùng để thử chấm/lịch sử.
- Thông báo chung, riêng từng sinh viên, theo khóa; có đã đọc/chưa đọc.

Các kết quả code AC/WA/CE/TLE/MLE/RE/SYSTEM_ERROR là **lịch sử dựng sẵn**,
được ghi rõ trong mô tả và log, để kiểm tra cách hiển thị. Không phải kết quả
Docker đã chấm. Hệ thống vẫn kiểm tra Docker thật khi chạy test mẫu, gửi bài
chấm hoặc chấm lại. Không có hàng đợi giả hay trạng thái online giả.

## Checklist Admin

| Trang / khu vực | Thao tác kiểm thử |
|---|---|
| Tổng quan | Số liệu, danh sách khóa, việc chờ xử lý, liên kết sang từng khu vực |
| Khóa học | Tìm tên/mã, lọc học kỳ/trạng thái, phân trang, tạo/sửa, tên dài |
| Nhập/xuất khóa | Nhập `khoa-hoc-import.json`, xuất và nhập lại; thử gói sai định dạng |
| Nội dung theo tuần | Mở/thu gọn tuần, sửa bài đọc, gắn/bỏ học liệu và hoạt động |
| Tài liệu | Upload PDF/PNG/DOCX/TXT/ZIP, xem trước, tải xuống, thử tệp rỗng/sai đuôi |
| Bài tập | Tạo/sửa, hạn nộp, giới hạn lượt, đóng bài, xem/chấm bài và phản hồi |
| Lịch | Tháng/tuần, ngày hôm nay, các ngày có sự kiện; tạo buổi học và thông báo |
| Điểm danh | Mở phiên theo buổi học, xem QR/mã, sửa trạng thái, đóng phiên |
| Kho câu hỏi & đề | Lọc code/file, mục đích, công bố/ẩn/lưu trữ, sao chép, sửa đề nháp |
| Cấu hình thi | Xem các trạng thái, roster, lịch, phát đề, giới hạn file, nhiều mã đề |
| Giám sát | Đăng nhập sinh viên thật, vào thi; đổi tab/mất focus để có cảnh báo thật |
| Tài khoản sinh viên | Import hợp lệ/lỗi, tìm kiếm, chọn nhiều, khóa/mở, đặt lại mật khẩu |
| Bài nộp | Lọc khóa/loại/trạng thái, tải tệp, chấm/chấm lại, xem lịch sử, xuất CSV |
| Điểm | Điểm 0/chưa có, sửa trọng số, điểm ghi đè/tự động, lưu và tổng kết khóa thử |
| Thông báo | Gửi tất cả/chọn người, tìm tên rồi đổi lựa chọn, kiểm tra nhận đúng người |
| Địa chỉ LAN | Địa chỉ do server cung cấp, tải lại và truy cập từ máy khác |
| Tài khoản Admin | Tạo bằng `testadmin`, thử đăng nhập bằng tài khoản vừa tạo |

Kỳ thi file chỉ có một lượt hoạt động tại một thời điểm theo thiết kế backend.
Kết thúc lượt mẫu trước khi kích hoạt cấu hình file khác. Dùng khóa QA trống
để thử tổng kết/xóa mà không mất các tình huống mẫu khác.

## Checklist sinh viên

| Trang | Thao tác kiểm thử |
|---|---|
| Tổng quan | Khóa đang học, việc gần hạn, lịch, thông báo, liên kết nhanh |
| Khóa học | Lọc/tìm, mở từng tab, đổi khóa, xem khóa đã tổng kết và khóa rỗng |
| Lịch học | Tháng trước/sau/hôm nay, chọn ngày, mở sự kiện và chi tiết |
| Điểm danh | Giữ kết nối khi phiên mở, kiểm tra kết quả server; so sánh tài khoản có/không ghi nhận |
| Bài tập | Nộp file hợp lệ, nộp lại, xem lịch sử; thử bài quá hạn, đóng, hết lượt |
| Kỳ thi file | Vào kỳ thi đang mở, xem đề, chọn tệp, nộp, xem biên nhận và lịch sử |
| Kỳ thi code | Vào kỳ thi code đang mở, chọn ngôn ngữ, editor, timer; gửi bài khi Docker sẵn sàng |
| Tự luyện | Tổng hai số và Java Product, test mẫu, gửi chấm, xem verdict; không tính điểm khóa |
| Lịch sử | Bài tập, file, code; xem tệp gốc và nhiều lần nộp |
| Kết quả | Khóa đã tổng kết, khóa chưa đủ điểm, `TESTZERO` có điểm 0 |
| Thông báo | Bell, dropdown, đã đọc/chưa đọc, thông báo riêng của đúng tài khoản |
| Tài khoản | Thông tin chỉ đọc, sai mật khẩu cũ, xác nhận không khớp, đổi mật khẩu đúng |

## Tệp nhập thử

Tất cả ở `full-system/test-inputs/`:

| Tệp | Dùng cho |
|---|---|
| `bao-cao.pdf`, `bao-cao.docx`, `so-do.png`, `bai-lam.txt`, `bai-lam.zip` | Upload, xem trước, tải và nộp file |
| `answer_ac.py`, `answer_ac.cpp`, `Main.java` | Đáp án đúng của đề Tổng hai số |
| `Product.java` | Đáp án Java dạng class của bài Product |
| `answer_wa.py`, `answer_ce.cpp`, `answer_tle.py`, `answer_re.py` | Thử chấm sai, biên dịch lỗi, timeout, runtime error bằng Docker thật |
| `testcases.csv`, `testcases-loi.csv` | Import test case đúng/sai |
| `import-tai-khoan.txt`, `import-tai-khoan-loi.txt` | Dán nội dung MSSV\|Ngày sinh\|Họ tên, kiểm tra lỗi theo dòng |
| `khoa-hoc-import.json`, `khoa-hoc-import-loi.json` | Nhập gói khóa học đúng/sai |
| `zip-bi-hong.zip`, `bai-lam-rong.txt`, `tep-khong-hop-le.exe` | Thử lỗi ZIP, nội dung rỗng, đuôi không cho phép; `.exe` chỉ là văn bản vô hại |

## Responsive và các trạng thái không thể tạo bằng dữ liệu tĩnh

Thử ở 1440, 1024, 768, 390px; kiểm tra drawer, cuộn bảng, tab, hộp thoại,
tên dài, focus bàn phím, trạng thái disabled và phóng to chữ.

Loading/chậm mạng/offline: dùng DevTools → Network → throttling/Offline,
rồi tải lại hoặc thao tác trong trang. Quyền camera cần thử trên thiết bị
thật nếu luồng hiện tại có sử dụng camera. Trạng thái queued/compiling/running
cần một lượt gửi code thật với Docker; dữ liệu tĩnh không thay thế được chúng.

## Thời gian, chạy lại và dữ liệu mới

Lịch dùng mốc tương đối lúc tạo. Thi đang mở khoảng 3 giờ, điểm danh khoảng
2 giờ; sau đó hết hạn theo server thật. Trạng thái khóa tạm hết sau 15 phút.
Chạy lại file BAT giữ nguyên thao tác đã thử, không nhân bản hoặc đặt lại mật khẩu.

Để tạo một lượt kiểm thử hoàn toàn mới ở thư mục mới:

```powershell
python -m scripts.seed_system_test --root sample-data/full-system-new --serve --port 8082
```

Kiểm tra tính toàn vẹn, không tạo lại dữ liệu:

```powershell
python -m scripts.seed_system_test --check
python -m unittest discover -s tests -p test_system_test_seed.py -v
```

Kiểm tra bố cục bằng dữ liệu này khi file BAT đã dừng:

```powershell
node tests/browser_ui_consistency.cjs --system-data
```

Ảnh ở `previews/system-data/after/`. Báo cáo số lượng ở
`full-system/verification.json`; ID/liên kết từng tình huống ở
`full-system/manifest.json` và `full-system/SCENARIOS.md`.
