# LAN-LMS — QUY CHUẨN THIẾT KẾ GIAO DIỆN TOÀN HỆ THỐNG

**Phiên bản:** 1.0 · **Nguồn đối chiếu:** `Nhom15_LMSLAN_Source-main.zip` được cung cấp ngày 11/11/2026.  
**Mục đích:** Tài liệu chuẩn để chỉnh sửa UI từng trang mà không thay đổi nghiệp vụ, URL, biểu mẫu, JavaScript hoặc hệ màu hiện có.

> **Nguyên tắc bất biến:** GIỮ NGUYÊN bảng màu hiện tại. Không tự ý chuyển sang một theme mới. Ưu tiên tái sử dụng `static/css/ui-polish.css`, `app.css`, `admin-sidebar.css`, các CSS theo chức năng và component hiện có. Mọi bố cục mô tả dưới đây là **chuẩn đề xuất để đồng bộ**, không khẳng định tất cả đã được triển khai.

## 1. Kết quả khảo sát mã nguồn

- Hệ thống hiện dùng **Python/Jinja2 HTML templates + CSS + JavaScript**, không phải giao diện React/Next.js. Template gốc: `templates/base.html`; các trang chính: `login.html`, `admin.html`, `student.html`; `learning_admin.html` là vùng nội dung tải động.
- `base.html` nạp `tailwind.css`, `app.css`, `exam-clock.css`, Font Awesome, `list-controls.css`, `course-select.css`, và cuối cùng `ui-polish.css`. Thứ tự cascade cần được bảo toàn.
- Admin sử dụng `admin-shell`, `main-sidebar`, `admin-content`, `topbar`, và điều hướng theo `section` hoặc route riêng. Student dùng cùng họ shell/sidebar với `student-shell`.
- Màu chính đang dùng: xanh `#245edb`, xanh đậm `#194bb9`, sidebar `#192e50`, chữ đậm `#1f3150`, chữ phụ `#40516b`, muted `#77869c`, đường viền `#e1e8f2`, nền card `#ffffff`, nền nhạt `#f8faff`. Đây là **giá trị đọc từ CSS hiện có**, không phải palette thay thế.
- Các chức năng sinh viên có route: `/student/dashboard`, `/student/courses`, `/student/calendar`, `/student/attendance`, `/student/assignments`, `/student/exams`, `/student/history`, `/student/grades`, `/student/notifications`, `/student/profile`.
- Các khu vực quản trị quan sát được: Dashboard, Khóa học, Giám sát, Thông báo, Kho bài tập & Đề, Cấu hình kỳ thi, Tài khoản sinh viên, Bài nộp, Địa chỉ LAN, Tài khoản Admin. Một số nội dung được dựng động bởi JavaScript; khi sửa UI phải rà soát cả `static/js/`.

## 2. Quy tắc bất biến và ưu tiên

1. Không thay đổi màu thương hiệu, gradient, màu phân loại hoạt động, màu verdict hay trạng thái hiện có; chỉ thống nhất **cách sử dụng** chúng.
2. Không sửa `id`, `name`, `action`, `method`, `data-*`, `href`, event listener, CSRF/session logic, điều kiện Jinja, quyền và kiểm tra backend chỉ để chỉnh giao diện.
3. Giữ nguyên dữ liệu, quy tắc thi, giới hạn nộp bài, thời gian server, import CSV, chấm code và phân quyền.
4. Giữ giao diện tiếng Việt, thuật ngữ nhất quán; tên trạng thái chấm có thể giữ mã kỹ thuật kèm nhãn Việt.
5. Component giống nhau phải dùng chung class và trạng thái, không sao chép CSS riêng cho từng trang.
6. Trang giảng viên và sinh viên dùng cùng hệ kích thước, typography, nút, card, bảng và phản hồi; chỉ khác menu và quyền thao tác.

## 3. Design tokens: sử dụng giá trị đang có

| Token hiện có                                        | Giá trị              | Phạm vi                                |
| ---------------------------------------------------- | -------------------- | -------------------------------------- |
| `--ui-blue`                                          | `#245edb`            | Nút chính, liên kết, trạng thái active |
| `--ui-blue-dark`                                     | `#194bb9`            | Hover nút chính                        |
| `--ui-blue-soft`                                     | `#edf4ff`            | Nền chọn / thông tin nhẹ               |
| `--ui-ink`                                           | `#1f3150`            | Tiêu đề                                |
| `--ui-text`                                          | `#40516b`            | Nội dung                               |
| `--ui-muted`                                         | `#77869c`            | Mô tả / nhãn phụ                       |
| `--ui-line`                                          | `#e1e8f2`            | Viền                                   |
| `--ui-line-strong`                                   | `#d5dfed`            | Viền nổi bật                           |
| `--ui-surface`                                       | `#ffffff`            | Card                                   |
| `--ui-surface-soft`                                  | `#f8faff`            | Vùng phụ                               |
| `--ui-radius-sm`                                     | `10px`               | Input, nút nhỏ                         |
| `--ui-radius`                                        | `15px`               | Card                                   |
| `--ui-radius-lg`                                     | `20px`               | Card nổi bật, dialog                   |
| `--ui-shadow-sm`, `--ui-shadow`, `--ui-shadow-hover` | Giữ khai báo CSS gốc | Độ nổi                                 |
| Sidebar admin                                        | `#192e50`            | Sidebar, giữ màu và active CSS gốc     |

**Không hardcode lại token** trong CSS mới. Không thay thế màu trạng thái trong `activity-colors.css`, `classification.css`, `programming.css` bằng màu chung nếu chúng đang mang ý nghĩa nghiệp vụ.

## 4. Khung bố cục áp dụng cho mọi trang

### 4.1. Trang đã đăng nhập

```text
┌──────── Sidebar cố định ────────┬──────────── Topbar ───────────────────────┐
│ Logo LAN-LMS                    │ Menu mobile | ngữ cảnh | tài khoản | thoát│
│ Thông tin người dùng            ├──────────────────────────────────────────┤
│ Nhóm menu                       │ Breadcrumb (nếu trang con)               │
│ • Mục đang chọn                 │ Tiêu đề trang + mô tả + hành động chính   │
│ • Các mục khác                  │ Thanh tab / bộ lọc / tìm kiếm (nếu có)    │
│                                 │ Nội dung: cards / bảng / form / biểu đồ    │
│ Trạng thái hệ thống (nếu có)    │ Phân trang / thông báo trạng thái         │
└─────────────────────────────────┴──────────────────────────────────────────┘
```

- Desktop: sidebar dùng chiều rộng hiện tại **244px** (`admin-sidebar.css`), không tự tạo sidebar khác. Nội dung dùng `admin-content`; container tuân theo max-width sẵn có của từng khu vực (ví dụ `max-w-7xl`).
- Topbar luôn ở trên nội dung, nút menu mobile nằm bên trái, tài khoản/đăng xuất bên phải. Không tạo hai topbar trên cùng một trang.
- Thứ tự bắt buộc: **breadcrumb → heading → toolbar → nội dung → phân trang/ghi chú**. Không đặt nút “Tạo mới” ở vị trí khác nhau giữa các trang danh sách.
- Khoảng cách đề xuất dựa trên bố cục hiện tại: 24px giữa các khối chính, 16px giữa card, 8–12px giữa thành phần liên quan. Tránh dùng margin tùy ý theo trang.
- Chỉ có một `h1` đại diện trang; `h2` cho khu vực, `h3` cho card. Không dùng kích thước chữ lớn để thay thế cấp heading.
- Responsive: desktop ≥1200px; tablet 768–1199px; mobile <768px. Ở màn hình nhỏ sidebar chuyển drawer; bảng cuộn ngang có nhãn cột; toolbar xuống dòng; nút quan trọng vẫn hiện nhãn hoặc có accessible label.

### 4.2. Trang đăng nhập / màn hình không có sidebar

- Giữ nền xanh-trắng và card căn giữa hiện có, logo ở trên, tên hệ thống, dòng mô tả, thông báo lỗi, form, nút đăng nhập.
- Card rộng tối đa khoảng 450px theo `app.css`; input full width; nhãn nằm trên ô nhập; không thêm sidebar.
- Không đổi luồng POST `/login`, trường `username`, `password`, `next`.

## 5. Bộ quy tắc thành phần dùng chung

| Thành phần      | Vị trí/hình thức                                      | Hành vi và trạng thái                                                                 |
| --------------- | ----------------------------------------------------- | ------------------------------------------------------------------------------------- |
| Nút chính       | Bên phải page heading hoặc cuối form, nền `--ui-blue` | Hover xanh đậm; disabled rõ; loading khóa nhấp lặp; chỉ một CTA chính cho mỗi khu vực |
| Nút phụ         | Kề nút chính, kiểu outline/ghost đang có              | Quay lại, hủy, làm mới; không cạnh tranh thị giác                                     |
| Nút nguy hiểm   | Chỉ ở thao tác xóa, kết thúc thi, hủy phiên           | Màu cảnh báo hiện có; dialog xác nhận và mô tả tác động                               |
| Nút icon        | Trong bảng/card khi thiếu không gian                  | `title` và `aria-label`; hit area tối thiểu 40×40px                                   |
| Search          | Đầu toolbar bên trái                                  | Placeholder `Tìm theo...`; debounce nếu dùng API; có xóa tìm kiếm                     |
| Filter / select | Cạnh search                                           | Nhãn rõ; giữ giá trị khi phân trang; có “Tất cả” nếu phù hợp                          |
| Tab             | Dưới heading, trên nội dung                           | Active xanh hiện có; một tab active; điều hướng không mất ngữ cảnh                    |
| Card            | Nền trắng, viền `--ui-line`, radius token             | Tiêu đề trái; action nhỏ bên phải; padding nhất quán                                  |
| Stat card       | Số lớn + nhãn + icon phụ                              | Click chỉ khi thực sự có đích; không dùng màu ngẫu nhiên                              |
| Data table      | Trong card hoặc table-wrap                            | Header rõ, căn phải số/điểm, action cột cuối; sticky header khi phù hợp               |
| Form field      | Label trên input; helper dưới input                   | Bắt buộc đánh dấu `*`; lỗi ngay dưới trường; giữ dữ liệu khi lỗi                      |
| Upload          | Vùng chọn file trong card                             | Hiển thị tên, dung lượng, định dạng; trạng thái uploading/success/error               |
| Badge           | Kích thước nhỏ, cạnh tên/trạng thái                   | Một trạng thái = một màu và một nhãn thống nhất                                       |
| Toast           | Vị trí toàn cục từ `base.html` (`#toast`)             | Thành công/lỗi ngắn; không thay thế lỗi inline quan trọng                             |
| Modal/dialog    | Chính giữa viewport, nền overlay                      | Tiêu đề, nội dung, Hủy trái / Xác nhận phải; focus trap, Esc khi an toàn              |
| Empty state     | Giữa vùng nội dung                                    | Icon nhẹ, thông điệp, CTA thích hợp nếu người dùng có quyền                           |
| Loading         | Skeleton hoặc spinner tại vùng dữ liệu                | Không làm nhảy bố cục; vô hiệu hóa hành động trùng                                    |
| Error           | Inline alert, có hướng khắc phục                      | Có Thử lại; không lộ stack trace, token, đường dẫn server                             |
| Pagination      | Dưới danh sách, căn phải                              | Hiển thị số bản ghi, trang hiện tại, Trước/Sau                                        |
| Countdown       | Khu vực kỳ thi dễ nhìn                                | Dùng thời gian server; cảnh báo khi sắp hết; không tự quyết định hết hạn ở client     |
| Code editor     | Bài thi lập trình                                     | Font monospace, dòng rõ, chọn ngôn ngữ, trạng thái lưu/nộp, không làm mất code        |

### 5.1. Từ vựng nút chuẩn

- Tạo: **Tạo khóa học**, **Tạo bài tập**, **Tạo kỳ thi**, **Tạo thông báo**.
- Lưu: **Lưu thay đổi**; tạo mới: **Tạo mới** chỉ khi ngữ cảnh đã rõ.
- Upload: **Chọn tệp** → **Tải lên**; nộp bài: **Nộp bài**; lập trình: **Gửi bài chấm**.
- Dữ liệu: **Tìm kiếm**, **Lọc**, **Làm mới**, **Xuất CSV**, **Tải xuống**, **Xem chi tiết**.
- Hủy: **Hủy**; rời trang: **Quay lại**; thao tác nguy hiểm: **Xóa**, **Kết thúc kỳ thi**, **Đóng phiên**.
- Tránh cùng một hành động lúc gọi “Submit”, lúc gọi “Gửi”, lúc gọi “Nộp”.

### 5.2. Thứ tự nút trong form

- Footer form: `Hủy` (secondary) → `Lưu/Tạo/Nộp` (primary), căn phải desktop; mobile có thể full width.
- Toolbar danh sách: `Tìm kiếm` → `Bộ lọc` bên trái; `Nhập CSV` / `Xuất` (secondary) → `Tạo mới` (primary) bên phải.
- Hành động từng dòng: `Xem` → `Sửa` → `Tải` (nếu có) → `Xóa` (cuối, phân tách rõ).
- Không đặt nút xóa sát nút xem khi icon không có nhãn.

## 6. Đặc tả từng trang ADMIN

### A01 — Dashboard (`/admin?section=dashboard`)

**Bố cục:** heading “Tổng quan” → các stat card → lưới 2 cột: hoạt động gần đây / khóa học hoặc kỳ thi → bảng việc cần xử lý.  
**Thành phần:** tổng khóa học, sinh viên, bài nộp, trạng thái kỳ thi và server (chỉ khi có dữ liệu).  
**Nút:** `Xem khóa học`, `Xem bài nộp`, `Giám sát`, `Làm mới`; link card phải dẫn đến trang tương ứng. Không đặt thao tác xóa trên Dashboard.

### A02 — Khóa học (`/admin/courses`)

**Bố cục:** breadcrumb → heading + `Tạo khóa học` → tìm kiếm/bộ lọc → card/grid khóa học hoặc bảng → phân trang. Khi mở khóa: header khóa học + các tab chức năng.  
**Thành phần:** mã, tên, mô tả, số thành viên, tình trạng, các khu vực học liệu/lịch/điểm danh/bài tập/kỳ thi/điểm (theo UI và quyền hiện có).  
**Nút:** `Tạo khóa học`, `Xem chi tiết`, `Chỉnh sửa`, `Quản lý sinh viên`, `Nhập CSV`, `Thêm tài liệu`, `Tạo hoạt động`; `Xóa` chỉ khi được backend hỗ trợ, có xác nhận.  
**Quy tắc:** các tab trong khóa học luôn giữ tên, thứ tự và active style; không biến một chức năng thành modal ở khóa A nhưng thành trang độc lập ở khóa B.

### A03 — Giám sát (`/admin?section=monitor`)

**Bố cục:** heading + nhãn thời gian cập nhật + `Làm mới` → bộ chọn kỳ thi → 4 stat card → bảng sinh viên/phiên thi → chi tiết.  
**Thành phần:** tổng số, online, đã nộp, cần chú ý; trạng thái kết nối, thời điểm gửi, trạng thái chấm.  
**Nút:** `Làm mới`, `Xem chi tiết`, thao tác quản trị phiên nếu thực sự có API/quyền.  
**Quy tắc:** cập nhật tự động không reset bộ lọc, không nhảy scroll; mất kết nối hiển thị “Dữ liệu có thể chưa mới”; không coi IP là bằng chứng gian lận.

### A04 — Thông báo (`/admin?section=notifications`)

**Bố cục:** heading → card soạn thông báo bên trái / card chọn người nhận bên phải (mobile xếp dọc) → phản hồi gửi.  
**Thành phần:** tìm sinh viên, danh sách checkbox, số đã chọn, nội dung thông báo, validation.  
**Nút:** `Chọn tất cả đang hiển thị`, `Bỏ chọn`, `Gửi thông báo`; chỉ gửi sau khi kiểm tra người nhận và nội dung.  
**Quy tắc:** phân biệt “chọn tất cả kết quả lọc” và “chọn toàn bộ hệ thống”; không tự xóa nội dung khi gửi thất bại.

### A05 — Kho bài tập & Đề (`/admin/question-bank`)

**Bố cục:** heading + CTA → tab/nhóm loại đề → tìm kiếm/lọc → danh sách tài nguyên → form tạo/sửa hoặc trang chi tiết.  
**Thành phần:** tên, loại, môn/khóa liên quan, mức độ/nhãn nếu có, thời điểm cập nhật, tệp và câu hỏi/test case.  
**Nút:** `Tạo mới`, `Xem`, `Sửa`, `Nhân bản` (nếu hỗ trợ), `Thêm câu hỏi`, `Nhập test CSV`, `Lưu`, `Xóa` (nếu hỗ trợ).  
**Quy tắc:** form dài chia section “Thông tin chung”, “Nội dung”, “Cấu hình chấm”, “Test case”; lỗi test phải chỉ ra dòng.

### A06 — Cấu hình kỳ thi (`/admin?section=exam`)

**Bố cục:** heading + trạng thái kỳ thi → các bước rõ: cấu hình → đối tượng → đề/phân phối → kiểm tra → bắt đầu/kết thúc.  
**Thành phần:** thời lượng, chính sách nộp, số lần nộp, ghi đè, mật khẩu, đuôi file; danh sách người tham gia; tải đề; quy tắc phân đề.  
**Nút:** `Lưu cấu hình`, `Chọn tất cả`, `Bỏ chọn`, `Lưu danh sách`, `Tải đề lên`, `Phân phối đề`, `Bắt đầu kỳ thi`, `Kết thúc kỳ thi`.  
**Quy tắc:** hành động bắt đầu/kết thúc luôn tách biệt, có xác nhận; hiển thị cấu hình đang hiệu lực; không cho UI sửa cấu hình bị backend khóa sau khi phát hành.

### A07 — Tài khoản sinh viên (`/admin?section=accounts`)

**Bố cục:** heading → card nhập danh sách → bảng tài khoản.  
**Thành phần:** vùng dán dữ liệu/import, hướng dẫn định dạng, kết quả theo dòng, bảng MSSV/tên/lớp/trạng thái.  
**Nút:** `Nhập danh sách`, `Xem lỗi`, `Tìm kiếm`, `Làm mới`; chỉ thêm `Tải mẫu CSV` nếu có dữ liệu mẫu được cung cấp.  
**Quy tắc:** báo dòng lỗi cụ thể; không hiển thị mật khẩu trong toast, bảng hay file xuất.

### A08 — Bài nộp (`/admin?section=submissions`)

**Bố cục:** heading → tổng quan → toolbar tìm kiếm/lọc → bảng bài nộp → chi tiết.  
**Thành phần:** sinh viên, khóa/bài thi, thời điểm nộp, lần nộp, tệp/ngôn ngữ, verdict, điểm.  
**Nút:** `Xem`, `Tải xuống`, `Xem lịch sử`, `Chấm lại` (nếu hỗ trợ và được phép), `Làm mới`.  
**Quy tắc:** không gộp `SYSTEM_ERROR` vào “0 điểm”; không công khai test ẩn; chấm lại không xóa lịch sử.

### A09 — Địa chỉ LAN (`/admin?section=server`)

**Bố cục:** heading → card tình trạng server → card địa chỉ truy cập/hướng dẫn → chi tiết kỹ thuật.  
**Thành phần:** địa chỉ URL/IP được server cung cấp, trạng thái cập nhật, hướng dẫn máy khách.  
**Nút:** `Làm mới`, `Sao chép địa chỉ` (nếu triển khai); copy đúng URL đã hiển thị.  
**Quy tắc:** không hardcode IP máy phát triển, không hiển thị secret hoặc đường dẫn dữ liệu nhạy cảm.

### A10 — Tài khoản Admin (`/admin?section=admins`)

**Bố cục:** heading → form tạo admin → bảng tài khoản.  
**Thành phần:** tên đăng nhập, các trường tạo tài khoản theo backend, thông báo kết quả.  
**Nút:** `Tạo tài khoản`, `Làm mới`; `Vô hiệu hóa`/`Xóa` chỉ nếu API và quyền thực sự có.  
**Quy tắc:** không hiển thị mật khẩu, không cho thao tác gây mất tài khoản quản trị cuối cùng nếu backend không cho phép.

## 7. Đặc tả từng trang SINH VIÊN

### S01 — Dashboard (`/student/dashboard`)

**Bố cục:** lời chào → thẻ tổng quan → khóa học đang học → bài tập/hạn gần → lịch và thông báo.  
**Nút:** `Vào khóa học`, `Xem bài tập`, `Xem kỳ thi`, `Xem thông báo`; CTA ưu tiên việc sắp đến hạn.

### S02 — Khóa học (`/student/courses`)

**Bố cục:** heading → tìm kiếm/lọc → lưới card khóa học → chi tiết khóa.  
**Thành phần:** tên/mã khóa, giảng viên (nếu có), mô tả, trạng thái; chi tiết có tab tổng quan, tài liệu, lịch, điểm danh, bài tập, thi, điểm tùy quyền.  
**Nút:** `Vào học`, `Xem tài liệu`, `Tải xuống`, `Xem bài tập`, `Xem điểm`.  
**Quy tắc:** cùng một khóa phải có cùng card/header giữa các nơi; sinh viên không thấy nút quản trị.

### S03 — Lịch (`/student/calendar`)

**Bố cục:** heading → điều hướng tháng/tuần → lịch → danh sách sự kiện ngày đang chọn.  
**Nút:** `Tháng trước`, `Hôm nay`, `Tháng sau`, chọn ngày, `Xem chi tiết`.  
**Quy tắc:** ngày hiện tại, ngày chọn và ngày có sự kiện phải phân biệt rõ bằng kiểu có sẵn; trên mobile ưu tiên danh sách.

### S04 — Điểm danh (`/student/attendance`)

**Bố cục:** heading → phiên hiện có → khối quét QR/nhập mã → lịch sử.  
**Nút:** `Quét QR`, `Nhập mã`, `Xác nhận điểm danh`, `Làm mới`.  
**Quy tắc:** báo rõ phiên còn/hết hạn, trạng thái đã điểm danh, lỗi quyền camera; không tự ghi nhận thành công trước phản hồi server.

### S05 — Bài tập (`/student/assignments`)

**Bố cục:** heading → bộ lọc (chưa nộp/đã nộp/quá hạn nếu có) → danh sách bài → chi tiết và vùng nộp.  
**Thành phần:** đề, hạn, loại file, số lần đã nộp, trạng thái, lịch sử.  
**Nút:** `Xem đề`, `Chọn tệp`, `Nộp bài`, `Nộp lại` (nếu được phép), `Xem lịch sử`.  
**Quy tắc:** trước khi gửi phải nhìn thấy tên file, hạn và bài đang chọn; disable nút trong lúc upload; giữ biên nhận.

### S06 — Kỳ thi (`/student/exams`)

**Bố cục:** danh sách kỳ thi → trang thông tin/kiểm tra trước thi → không gian làm bài → xác nhận nộp → kết quả.  
**Thành phần:** tên, khóa học, trạng thái, thời gian server, thời lượng, hướng dẫn, đề, upload hoặc editor, trạng thái chấm.  
**Nút:** `Xem thông tin`, `Bắt đầu làm bài`, `Chọn ngôn ngữ`, `Gửi bài chấm` hoặc `Nộp bài`, `Xem kết quả`, `Xem lịch sử`.  
**Quy tắc:** timer luôn dễ thấy; cảnh báo trước khi rời trang nếu có nội dung chưa lưu; không tiết lộ test ẩn; verdict và điểm phải có trạng thái đang xử lý.

### S07 — Lịch sử (`/student/history`)

**Bố cục:** heading → lọc theo khóa/kỳ thi/trạng thái → bảng lịch sử → chi tiết từng lần.  
**Nút:** `Xem chi tiết`, `Xem kết quả`, `Tải tệp` (nếu được phép).  
**Quy tắc:** mỗi lần nộp là một bản ghi, không ghi đè lịch sử; thời gian và mã biên nhận rõ ràng.

### S08 — Bảng điểm (`/student/grades`)

**Bố cục:** heading → chọn khóa → bảng điểm thành phần → điểm tổng kết/ghi chú công bố.  
**Nút:** `Chọn khóa học`, `Xem chi tiết` (nếu có).  
**Quy tắc:** phân biệt `Chưa có điểm` và điểm `0`; chỉ hiển thị điểm đã được phép công bố.

### S09 — Thông báo (`/student/notifications`)

**Bố cục:** heading + số chưa đọc → tab tất cả/chưa đọc → danh sách thông báo → chi tiết.  
**Nút:** `Đánh dấu đã đọc`, `Đánh dấu tất cả đã đọc` (nếu API hỗ trợ), `Xem chi tiết`.  
**Quy tắc:** thông báo chưa đọc có nhấn mạnh vừa đủ, không đổi màu theme; giữ vị trí danh sách sau khi đọc.

### S10 — Hồ sơ (`/student/profile`)

**Bố cục:** heading → card danh tính → card thông tin cá nhân → card bảo mật/đổi mật khẩu.  
**Nút:** `Đổi mật khẩu`, `Lưu thay đổi` (chỉ trường cho phép), `Hủy`.  
**Quy tắc:** thông tin không sửa được hiển thị read-only; không hiển thị mật khẩu hiện tại; validation mật khẩu mới và xác nhận.

## 8. Quy tắc chuyên biệt: form dài, bảng, thi code và cập nhật LAN

### 8.1. Form tạo/sửa

- Nhóm trường thành section có heading, mô tả ngắn; desktop 2 cột cho trường ngắn, 1 cột cho textarea, upload, editor.
- Thứ tự: thông tin chung → cấu hình → tài liệu/test → đối tượng → kiểm tra → lưu.
- Thông báo lỗi gắn đúng input, giữ giá trị nhập; không xóa dữ liệu khi backend trả 400/409/500.

### 8.2. Bảng dữ liệu

- Cột nhận dạng đầu tiên, trạng thái gần cuối, hành động cuối cùng.
- Search/filter/pagination có cùng vị trí ở tất cả bảng.
- Bảng lớn phải có `overflow-x:auto`; không ép chữ MSSV, mã bài hoặc đường dẫn vào nhiều dòng khó đọc.
- Dữ liệu mới tải không được làm mất checkbox đã chọn khi chưa xác nhận hành động.

### 8.3. Thi lập trình

- Desktop đề và editor có thể chia 2 vùng; mobile dùng tab chuyển vùng, không ép 2 cột.
- Thanh trên hiển thị tên bài, ngôn ngữ, thời gian còn lại và trạng thái kết nối.
- Nút `Gửi bài chấm` dễ tìm nhưng không che code; kết quả có verdict, điểm, thời gian, bộ nhớ nếu backend trả về.
- Với Pending/Compiling/Running hiển thị đang xử lý; Accepted/Wrong Answer/Compile Error/TLE/MLE/Runtime Error/System Error có nhãn thống nhất từ dữ liệu backend.
- Không dùng UI để suy diễn bài đã được server nhận nếu request thất bại.

### 8.4. Mạng LAN và polling

- Khi đang tải: trạng thái loading; mất mạng: banner lỗi + `Thử lại`; phục hồi: tự cập nhật mà không reset thao tác người dùng.
- Không đổi dữ liệu đã nhập khi polling. Không dùng màu xanh thành công cho hành động chưa được server xác nhận.
- Hiển thị “Cập nhật lần cuối” trên trang giám sát; không giả lập trạng thái online.

## 9. Quy tắc triển khai trong codebase

**Thứ tự sửa:** `static/css/ui-polish.css` (tokens/shared UI) → `static/css/admin-sidebar.css` (shell) → `static/css/app.css` (base) → CSS chuyên trang → template/JS tạo HTML động. Tránh thêm `!important` nếu có thể; kiểm tra thứ tự CSS trong `base.html`.

**Cấu trúc khuyến nghị (không bắt buộc di chuyển file ngay):**

```text
static/css/
  app.css                  # nền tảng đang có
  admin-sidebar.css        # sidebar dùng chung
  ui-polish.css            # token và chuẩn chung đang có
  [feature].css            # chỉ quy tắc đặc thù chức năng
templates/
  base.html                # nạp assets và toast chung
  admin.html               # admin shell và section
  student.html             # student shell và vùng nội dung
  login.html               # xác thực
static/js/
  [feature].js             # render động và sự kiện, giữ contract DOM
```

**Ưu tiên tái sử dụng class đang có:** `.btn`, `.btn-ghost`, `.panel`, `.page-title`, `.topbar`, `.main-sidebar`, `.table-wrap`, `.stack-form`, `.student-toolbar`, `.student-tabs`, `.student-status`, `.toast`. Chỉ tạo class mới khi component không có tương đương.

**Lưu ý quan trọng:** nhiều phần giao diện sinh viên và quản trị được render từ JavaScript. Chỉnh HTML template đơn thuần không đảm bảo thống nhất; cần rà soát JS sinh card, row, dialog, nút, thông báo và class trạng thái.

## 10. Checklist nghiệm thu áp dụng cho MỖI trang

- [ ] Giữ nguyên palette hiện tại, sidebar, font và icon family.
- [ ] Đúng một tiêu đề chính; heading, toolbar, card, bảng, footer cùng thứ tự.
- [ ] Nút chính ở vị trí nhất quán; nhãn hành động đúng quy ước.
- [ ] Có loading, empty, error, success, disabled cho các thao tác liên quan.
- [ ] Search/filter/pagination không mất trạng thái vô cớ.
- [ ] Form có label, validation, lỗi inline, xác nhận thao tác nguy hiểm.
- [ ] Responsive ở 1440px, 1024px, 768px, 390px; không tràn ngang toàn trang.
- [ ] Dùng bàn phím được, có focus-visible, label/aria cho icon button và dialog.
- [ ] Không thay đổi URL, `id`, `name`, `data-*`, request body, session, quyền, nghiệp vụ.
- [ ] Kiểm tra admin và student; dữ liệu rỗng, dữ liệu dài, mạng chậm/mất mạng.
- [ ] Các màn hình thi/điểm danh/nộp bài không hiển thị thành công khi server chưa xác nhận.
- [ ] So sánh screenshot trước/sau để chắc chắn **không đổi hệ màu**.

## 11. Quy trình áp dụng an toàn

1. Chụp ảnh màn hình và ghi lại chức năng của từng trang trước sửa.
2. Chuẩn hóa shared CSS và shell trước; kiểm thử login, admin dashboard, student dashboard.
3. Chuẩn hóa component cơ bản: nút, input, card, tab, bảng, modal, toast.
4. Chuẩn hóa các trang danh sách, sau đó trang chi tiết, cuối cùng trang thi và luồng nghiệp vụ nhạy cảm.
5. Với mỗi trang: đối chiếu checklist, kiểm tra cả HTML do JS sinh ra, chạy thử thao tác thực tế trên LAN.
6. Commit từng nhóm màn hình; rollback riêng UI nếu gây lỗi nghiệp vụ.

---

**Tiêu chí hoàn thành:** Người dùng chuyển giữa các trang và hai vai trò vẫn nhận ra cùng một sản phẩm LAN-LMS: cùng màu xanh/slate đang có, cùng sidebar/topbar, cùng cấu trúc heading–toolbar–content, cùng nút/form/bảng/trạng thái; chức năng và dữ liệu không đổi.
