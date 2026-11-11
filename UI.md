# Quy chuẩn giao diện LAN-LMS

**Trạng thái:** Quy chuẩn thiết kế đã chốt để triển khai; chưa phải chứng nhận website hiện tại đã đạt chuẩn.  
**Phạm vi:** Trang đăng nhập, sinh viên và giảng viên/quản trị trên máy tính; gồm giao diện sinh động bằng JavaScript. Thiết kế điện thoại không thuộc phạm vi.  
**Mục tiêu kiểm thử:** Các tiêu chí UX desktop và những yêu cầu accessibility áp dụng bên dưới; chưa tuyên bố toàn hệ thống đạt WCAG 2.2 AA.

Tài liệu này là nguồn tham chiếu cho việc thiết kế lại giao diện sinh viên và giảng viên. Giữ nhận diện xanh navy và xanh dương hiện có, nhưng giảm chữ trang trí, giảm số lớp box và ưu tiên thao tác thực tế. Áp dụng cho HTML trong `templates/`, giao diện sinh bởi `static/js/` và CSS trong `static/css/`.

## 1. Nguyên tắc chốt

1. **Nội dung trước trang trí.** Trong 5 giây đầu, người dùng phải thấy tên màn hình, việc cần làm và trạng thái liên quan. Không dùng banner chỉ để lặp lại tên trang hoặc giải thích cách dùng hiển nhiên.
2. **Một màn hình, một hành động chính.** Ví dụ: trang bài tập là chọn/mở bài; trang ngân hàng là tìm/chọn/tạo câu; trang thi là bắt đầu/nộp bài. Hành động chính có màu xanh, hành động phụ dùng viền hoặc chữ.
3. **Thông tin ngắn nhưng đủ quyết định.** Chỉ hiện dữ liệu giúp người dùng chọn bước tiếp theo: hạn nộp, trạng thái, điểm, số lần nộp, phạm vi khóa học. Nội dung đề, test và lịch sử chi tiết nằm ở màn xem chi tiết.
4. **Không ẩn thông tin bằng selector toàn cục.** `small`, `.muted` và `.fine-print` không đồng nghĩa với “thừa”. Mỗi dòng phụ phải được đánh giá theo ngữ cảnh rồi xóa khỏi template/JS nếu không cần. Không dùng lại lớp ẩn hàng loạt `no-more-details.css`.
5. **Một nguồn dữ liệu, một biểu diễn nhất quán.** Cùng một trạng thái, ngày giờ, nhãn và hành động phải có cùng cách hiển thị ở danh sách, chi tiết, dashboard và giám sát.
6. **Không hy sinh chức năng để làm gọn.** Nếu banner đang chứa bộ chọn khóa học, bộ lọc hoặc nút hành động, chuyển chúng sang thanh công cụ gọn. Không xóa điều khiển cùng với banner.

## 2. Ngôn ngữ thị giác

### Màu

| Vai trò         | Token đề xuất         | Giá trị   | Dùng cho                          |
| --------------- | --------------------- | --------- | --------------------------------- |
| Navy            | `--ui-navy`           | `#192E50` | Sidebar, tiêu đề đậm              |
| Primary         | `--ui-primary`        | `#2864E8` | Nút chính, liên kết, focus        |
| Primary hover   | `--ui-primary-hover`  | `#1E50C8` | Hover của hành động chính         |
| Nền ứng dụng    | `--ui-canvas`         | `#F4F7FB` | Vùng ngoài nội dung               |
| Bề mặt          | `--ui-surface`        | `#FFFFFF` | Panel, form, modal                |
| Bề mặt nhẹ      | `--ui-surface-soft`   | `#F7F9FC` | Toolbar, header bảng              |
| Viền            | `--ui-border`         | `#DFE7F2` | Phân tách nhẹ                     |
| Chữ chính       | `--ui-text`           | `#20324C` | Nội dung và tiêu đề               |
| Chữ phụ         | `--ui-text-muted`     | `#62738D` | Metadata cần đọc                  |
| Thành công      | `--ui-success`        | `#21845D` | Đã nộp, có mặt, hoàn thành        |
| Cảnh báo        | `--ui-warning`        | `#A66C0A` | Sắp hạn, chờ xử lý                |
| Lỗi             | `--ui-danger`         | `#B33B38` | Quá hạn, lỗi, thao tác nguy hiểm  |
| Viền điều khiển | `--ui-control-border` | `#7C8DA4` | Viền input/nút phụ trên nền trắng |
| Chữ thành công  | `--ui-success-text`   | `#1B7450` | Chữ badge trên nền `#EAF6EF`      |
| Chữ cảnh báo    | `--ui-warning-text`   | `#996000` | Chữ badge trên nền `#FFF5DF`      |

Màu trạng thái luôn kèm chữ hoặc biểu tượng; không truyền đạt ý nghĩa bằng màu riêng lẻ. Nền trạng thái là sắc độ rất nhạt, chữ đủ tương phản. Không dùng vàng nhạt phủ cả dòng bài tập chỉ để phân loại nhóm.

### Chữ và khoảng cách

- Font: `Inter`, sau đó `Segoe UI`, `Arial`, sans-serif; không tải font từ mạng khi chạy LAN.
- Cỡ chữ: tiêu đề trang 28–32px; tiêu đề khu vực 18–22px; tên mục 15–17px; nội dung 14–15px; nhãn/metadata 12–13px. Không dùng 9–10px cho thông tin cần đọc.
- Độ đậm: 700 cho tiêu đề, 600 cho nhãn và tên mục, 400–500 cho nội dung. Chỉ dùng chữ hoa và tracking rộng ở nhãn khu vực ngắn, không dùng cho đoạn văn.
- Line-height: 1.25–1.35 cho tiêu đề, 1.5–1.65 cho nội dung. Mỗi dòng văn bản nên dài dưới khoảng 80 ký tự trên desktop.
- Thang khoảng cách: 4, 8, 12, 16, 24, 32, 48px. Dùng 16px giữa các trường liên quan, 24px giữa các khối, 32px giữa các khu vực lớn. Tránh khoảng trống lớn sinh ra sau khi ẩn chữ.
- Bo góc: 8px cho input/nút, 12px cho hàng tương tác, 16px cho panel, tối đa 20px cho modal lớn. Bóng đổ nhẹ chỉ để phân tách lớp nổi; panel thông thường dùng viền.
- Icon: tuân theo mục **Quy chuẩn icon** dưới đây; icon hỗ trợ nhận biết, không thay nhãn của hành động quan trọng.

### Quy tắc token và thứ bậc

- Token có ba tầng: **nền tảng** (màu và spacing thô) → **ngữ nghĩa** (`primary`, `danger`, `surface`, `text`) → **component** (`button`, `input`, `badge`). Component tham chiếu token ngữ nghĩa, không chép mã màu rải rác.
- Mỗi token có tên, giá trị, mục đích và trạng thái. Không tạo biến `blue2`, `card-new` hoặc màu mới chỉ để sửa một màn hình. Biến thể mới cần được thêm vào bảng token và kiểm tra tương phản.
- Trạng thái tối thiểu cho thành phần tương tác: `default`, `hover`, `focus-visible`, `active/selected`, `disabled`, `loading`, `error` khi áp dụng. Màu hover và focus không được đổi kích thước hay làm layout nhảy.
- Không dùng độ trong suốt làm giảm tương phản của chữ quan trọng. Chữ trong nút bị vô hiệu hóa có thể giảm nổi bật nhưng trạng thái disabled phải còn nhận biết được.

## 3. Quy chuẩn icon

### Nguồn và hình thức

- Dùng **một ngôn ngữ icon chủ đạo** trên cả giao diện. Triển khai hiện tại dùng Font Awesome cục bộ (`static/vendor/fontawesome/`) cho cả hai vai trò; `static/js/admin-icons.js` chuẩn hóa tên icon cũ theo từ điển chung. Không trộn glyph Font Awesome và SVG trong cùng toolbar. Danh mục icon chuẩn là các tên bên dưới; mọi icon mới cần được thêm vào danh mục trước khi sử dụng.
- Không tải icon từ CDN, emoji hoặc ảnh raster cho nút điều khiển. Icon trang trí lớn chỉ được dùng ở trạng thái rỗng thực sự và có cùng phong cách với icon hệ thống.
- Cỡ glyph: 16px trong nút/bộ lọc/hàng, 18–20px trong sidebar, 20–24px trong thẻ thống kê. Dùng cùng một khung vuông và căn giữa; khoảng cách với nhãn 8px. Không phóng icon vượt 24px trong toolbar.
- Màu icon mặc định kế thừa màu chữ. Icon trên nền màu dùng màu đủ tương phản. Không tô mỗi mục menu một màu khác nhau; chỉ trạng thái active, warning, success mới đổi màu theo ngữ nghĩa.
- Icon không thay cho chữ ở thao tác quan trọng như **Nộp bài**, **Bắt đầu thi**, **Xóa**, **Lưu**. Nút icon-only chỉ dùng khi không gian thật sự hẹp và ý nghĩa đã quen thuộc (đóng, tìm, làm mới, mở menu). Có tên truy cập (`aria-label`) và kích thước hit area theo mục 8.
- Icon trang trí: `aria-hidden="true"`; nhãn chữ đứng cạnh diễn đạt đủ ý. Icon truyền đạt trạng thái phải đi kèm chữ trạng thái. Không dùng icon mũi tên ở mọi card nếu cả card đã rõ là liên kết.

### Từ điển icon

| Ý nghĩa duy nhất              | Icon hiện có                                                              | Nơi dùng             | Không dùng thay thế                                   |
| ----------------------------- | ------------------------------------------------------------------------- | -------------------- | ----------------------------------------------------- |
| Dashboard                     | `fa-th-large`                                                             | Điều hướng tổng quan | `fa-dashboard` ở một vai trò khác trong cùng hệ thống |
| Khóa học                      | `fa-book`                                                                 | Điều hướng, thẻ khóa | Folder chỉ để trang trí                               |
| Bài tập                       | `fa-pencil-square-o`                                                      | Bài tập, tạo bài     | `fa-file-text-o` nếu cùng ý nghĩa bài tập             |
| Kỳ thi / đề thi               | `fa-file-text-o`                                                          | Kỳ thi, bộ đề        | Icon shield cho kỳ thi thông thường                   |
| Ngân hàng câu hỏi             | `fa-database`                                                             | Kho câu hỏi          | Folder mở                                             |
| Lịch                          | `fa-calendar`                                                             | Lịch học, ngày thi   | Clock cho lịch tổng thể                               |
| Thời gian / hạn               | `fa-clock-o`                                                              | Hạn nộp, đếm giờ     | Calendar nếu là thời lượng                            |
| Điểm danh                     | `fa-qrcode`                                                               | Điểm danh QR         | QR cho mọi hoạt động khác                             |
| Sinh viên / thành viên        | `fa-users`                                                                | Danh sách người      | Một người cho cả lớp                                  |
| Thông báo                     | `fa-bell-o`                                                               | Hộp thông báo        | Bullhorn cho thông báo cá nhân                        |
| Tìm kiếm / lọc                | `fa-search` / `fa-filter`                                                 | Input và filter      | Dùng cùng icon cho hai chức năng                      |
| Thêm / sửa / xóa              | `fa-plus` / `fa-pencil` / `fa-trash-o`                                    | CRUD                 | `fa-times` cho xóa dữ liệu                            |
| Tải lên / tải xuống           | `fa-upload` / `fa-download`                                               | Chuyển file          | Mũi tên chung không rõ chiều                          |
| Thành công / lỗi / cảnh báo   | `fa-check-circle-o` / `fa-exclamation-circle` / `fa-exclamation-triangle` | Phản hồi trạng thái  | Màu đơn lẻ không có chữ                               |
| Quay lại / mở chi tiết / đóng | `fa-arrow-left` / `fa-chevron-right` / `fa-times`                         | Điều hướng, modal    | Chevron dùng cho xóa hoặc submit                      |

Nếu Font Awesome không có icon phù hợp, bổ sung một SVG nội bộ có `viewBox` 24×24, hình dáng và độ đậm đồng nhất; không thêm thư viện icon thứ hai. Tạo một ánh xạ ngữ nghĩa dùng chung cho student/admin rồi thay icon cũ theo từng màn hình. Kiểm tra hiển thị khi font/icon lỗi: nhãn chữ vẫn đủ hiểu.

## 4. Khung trang

- Sidebar giữ một chiều rộng ổn định khoảng 240–248px. Nhóm menu theo công việc, chỉ một mục active; có thể cuộn độc lập khi chiều cao màn hình thấp.
- Thanh trên cùng chỉ chứa định vị hiện tại và thao tác tài khoản/Thông báo. Không lặp logo, tên người dùng và tiêu đề trang nhiều lần trong cùng một viewport.
- Vùng nội dung có chiều rộng tối đa khoảng 1440–1540px, padding ngang 24–32px; không để nội dung chạm mép ở cửa sổ desktop hẹp.
- Đầu trang gồm **tên trang + hành động chính nếu có**. Mô tả chỉ hiện khi thật sự giải thích một quy tắc khó hoặc rủi ro; ưu tiên thông tin ngắn trong đúng form/chi tiết.
- Trong trang theo khóa học: breadcrumb hoặc nút quay lại, tên khóa học, bộ chuyển khóa học gọn, rồi nội dung. Không cần một banner lớn để công bố đang ở “bước 1/bước 2”.
- Mỗi khu vực chỉ có một lớp panel chính. Tránh panel chứa panel, nền tô nhiều lớp và box viền bao quanh một box viền khác. Toolbar có thể nằm trong panel danh sách, nhưng không thành một card giới thiệu riêng.

## 5. Thành phần chuẩn

| Thành phần      | Quy tắc                                                                                                                                                                                       |
| --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Nút chính       | Tối đa một nút primary trong một khu vực tác vụ; cao tối thiểu 40px.                                                                                                                          |
| Nút phụ         | Viền trung tính; icon có thể đi cùng nhãn. Nút chỉ có icon phải có `aria-label` và tooltip nếu khó hiểu.                                                                                      |
| Form            | Nhãn ở trên trường; trường cùng nhóm đặt theo lưới 2 cột khi đủ chỗ, 1 cột khi form hẹp. Lỗi nằm cạnh trường hoặc đầu form, có thông điệp sửa được.                                           |
| Bộ lọc          | Tìm kiếm và 1–2 bộ lọc thường dùng hiển thị ngay; bộ lọc nâng cao gấp lại. Hiện số kết quả và nút xóa lọc khi có lọc. Không có filter “chết” hoặc chọn không làm đổi kết quả.                 |
| Bảng/danh sách  | Tên mục là điểm nhấn và mở được chi tiết; mỗi hàng chỉ giữ 2–4 dữ liệu để quyết định. Hàng có `hover`, `focus`, trạng thái đang chọn và hành động rõ. Bảng rộng cuộn trong vùng của chính nó. |
| Card thống kê   | Một nhãn, một con số, tối đa một đơn vị/ngữ cảnh. Không thêm câu diễn giải dưới mỗi số. Dùng khi số liệu dẫn đến quyết định hoặc hành động.                                                   |
| Badge           | Dùng cho loại và trạng thái. Giới hạn 1–2 badge trên một mục; các mã dài cắt hợp lý, có thể xem đầy đủ ở chi tiết.                                                                            |
| Modal           | Chỉ dùng cho tác vụ ngắn. Form dài, nhiều test case, tạo đề hoặc chấm bài cần một workspace/trang riêng. Có nút đóng, trạng thái lưu và cảnh báo nháp chưa lưu.                               |
| Trạng thái rỗng | Tên trạng thái + một hành động phù hợp nếu người dùng có quyền tạo. Không dùng đoạn văn dài hoặc minh họa lớn.                                                                                |
| Thông báo       | Thành công ngắn gọn; lỗi nói nguyên nhân và cách xử lý. Toast không thay thế thông tin lỗi trong form.                                                                                        |

### Thông số và hành vi bắt buộc

| Thành phần     | Kích thước / bố cục                                                     | Trạng thái và tương tác                                                          |
| -------------- | ----------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| Button         | Cao 40–44px, padding ngang 14–16px; icon 16px, gap 8px                  | Enter/Space kích hoạt; loading khóa gửi lặp và có nhãn trạng thái; focus thấy rõ |
| Input/select   | Cao tối thiểu 40px, nhãn cách trường 6–8px; trường dài chiếm đủ cột     | Lỗi hiển thị sát trường, giữ dữ liệu đã nhập; không dựa vào màu đỏ đơn độc       |
| Toolbar lọc    | Một hàng khi đủ chỗ, tự xuống dòng ở cửa sổ desktop hẹp                 | Bộ lọc đang áp dụng hiện rõ; xóa lọc trả về kết quả mặc định                     |
| Hàng danh sách | Padding dọc 12–16px, ranh giới nhẹ                                      | Vùng click có đích rõ; không lồng nút trong nút hoặc link trong link             |
| Modal          | Rộng tối đa 640px cho tác vụ ngắn, padding 24px; chiều cao tối đa 90dvh | Escape/đóng, focus được quản lý; thao tác nguy hiểm có xác nhận cụ thể           |
| Badge          | Cao khoảng 24–28px, padding ngang 8–10px                                | Tên trạng thái đọc được; không dùng badge như nút nếu không click được           |
| Tabs           | Nhãn ngắn, active bằng màu và đường gạch/khối                           | Dùng được bằng bàn phím, trạng thái chọn được công bố cho công cụ hỗ trợ         |

Không ép tất cả màn hình vào bảng hoặc card. Chọn cấu trúc theo nhiệm vụ: danh sách ngắn có thể dùng card, dữ liệu cần so sánh theo cột dùng bảng. Với bảng, header vẫn liên kết rõ với dữ liệu; không ẩn cột quan trọng chỉ để vừa cửa sổ hẹp.

### Mẫu triển khai dùng chung cho màn hình nhiều dữ liệu

Các class sau là hợp đồng giao diện chung, dùng trong template và HTML sinh bởi JavaScript. Chỉ thêm biến thể khi cấu trúc nghiệp vụ thật sự khác; không tạo class mới chỉ để đổi màu hoặc vài pixel.

| Mẫu            | Class chung                         | Quy tắc bố cục                                                                                                                                                                 |
| -------------- | ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Đầu màn tác vụ | `ui-page-bar`                       | Một tiêu đề, trạng thái/phạm vi nếu cần, hành động chính ở bên phải. Không lặp lại tiêu đề trong panel ngay dưới.                                                              |
| Form dài       | `ui-form-workspace`                 | Rộng tối đa 1120px trên desktop; các nhóm form nằm liên tiếp trên cùng một bề mặt, không lồng nhiều card.                                                                      |
| Nhóm trường    | `ui-form-section` + `ui-form-grid`  | Tiêu đề nhóm ngắn; trường theo hai cột, khoảng cách 16–24px; trường dài dùng `ui-span-2`. Chia nhóm theo quyết định của người dùng: thông tin, nội dung, chính sách, xác nhận. |
| Quy tắc phụ    | `ui-rule-details`                   | Quy tắc dài nằm trong `<details>` cạnh nhóm trường liên quan; tóm tắt luôn nói rõ nội dung. Hạn, lỗi và ràng buộc nhập liệu quan trọng vẫn hiển thị ngay.                      |
| Danh sách chọn | `ui-choice-group`                   | Viền nhẹ, nền trắng, nhãn rõ; trạng thái chưa có dữ liệu dùng `ui-empty-state` với một lối đi tiếp theo. Không để `fieldset` giữ viền mặc định trình duyệt.                    |
| Hành động form | `ui-action-bar`                     | Nằm cuối form, tách bằng đường viền; một nút chính, các nút phụ bên cạnh. Không để nút lưu trôi giữa các nhóm trường.                                                          |
| Chọn khóa học  | `ui-course-grid` + `ui-course-card` | Card gồm mã, tên, học kỳ/trạng thái, 1–2 số liệu có ích và hành động mở. Khi nhiều khóa học có ô tìm; không đặt một panel giới thiệu bọc thêm quanh lưới.                      |

Form dài phải giữ cấu trúc này ở các trang kỳ thi, tạo/sửa bài tập, kho câu hỏi và quản lý khóa học. Bản desktop 1280px phải hiển thị hai cột trường mà không tạo khoảng trống một cột sau trường cuối; ở cửa sổ 1024px, nhóm trường có thể xếp một cột. Khi đã chọn khóa học ở thanh phạm vi, không lặp thêm một bộ chọn cùng mục đích trong form nếu có thể dùng thanh đó; nếu việc đổi khóa trong form có ý nghĩa nghiệp vụ khác, phải ghi rõ bằng nhãn.

## 6. Quy tắc nội dung: bỏ `more-detail`

Xóa khỏi UI các dòng chỉ nhắc lại tiêu đề hoặc mô tả thao tác hiển nhiên, ví dụ “Bấm tên bài để xem”, “Chọn khóa học để xem danh sách”, “Mở để xem yêu cầu”, “Thông tin sẽ hiển thị tại đây”. Không dùng eyebrow “BƯỚC 1”, “KẾ HOẠCH HỌC TẬP” nếu tiêu đề ngay dưới đã nói rõ cùng một việc. Không thêm câu giới thiệu vào mọi panel cho đủ bố cục.

**Giữ thông tin có giá trị vận hành:** hạn nộp và múi giờ, tình trạng nhận bài, số lần được nộp, điểm/nhận xét, quyền truy cập, định dạng/giới hạn file, quy tắc tính điểm, tình trạng giám sát, lỗi bộ chấm. Các thông tin này có thể trình bày bằng nhãn ngắn hoặc đặt gần thao tác tương ứng; không được ẩn chỉ vì đang dùng `<small>` hay `.muted`.

**Quy tắc banner:** chỉ dùng banner khi có thông báo quan trọng cần chú ý ngay (kỳ thi đang mở, sự cố, thay đổi chính sách, yêu cầu đổi mật khẩu). Banner giới thiệu, chào mừng, nhắc lại tên trang, icon trang trí lớn và gradient không mang thông tin phải bỏ. Banner cảnh báo có thể đóng khi phù hợp; thông báo khẩn không được mất khi tải lại nếu chưa xử lý.

## 7. Mẫu bố cục theo luồng

### Sinh viên

- **Dashboard:** việc cần làm gần nhất, lịch sắp tới, truy cập nhanh khóa học/kỳ thi. Không có hero chào mừng lớn.
- **Khóa học:** danh sách khóa học → trong khóa có tab học liệu, lịch, bài tập, điểm danh, kết quả. Mã/khóa/tiến độ hiển thị gọn trên card.
- **Bài tập:** chọn khóa học từ danh sách; khi vào khóa, hiện thanh tên khóa + chuyển khóa. Bên dưới là tiến độ vừa đủ, tìm kiếm/lọc nhóm/trạng thái, rồi danh sách bài. Chi tiết bài mới hiện yêu cầu, file và lịch sử nộp.
- **Kỳ thi:** trạng thái và giờ mở/đóng nổi bật; vào thi có điều hướng bài, đề, editor/upload và lịch sử. Không dùng chú thích dày đặc cạnh các điều khiển đã có nhãn.

### Giảng viên / quản trị

- **Dashboard:** việc cần xử lý, lịch dạy, khóa đang hoạt động, truy cập tác vụ chính.
- **Khóa học:** một điều hướng cấp khóa rõ ràng; lịch, học liệu, bài tập, điểm danh và bảng điểm dùng cùng bộ lọc, bảng và trạng thái.
- **Kho bài tập & Đề:** khóa học → ngân hàng câu hỏi → bộ đề → kỳ thi. Tìm theo tên/mã/nhóm, chọn nhiều câu, xem trước test và cấu hình. Không tạo hai giao diện ngân hàng song song.
- **Giám sát / chấm bài:** trạng thái người học, bộ lọc theo kỳ thi, dữ liệu có thể hành động; chi tiết và lịch sử riêng. Không dùng badge hoặc màu chỉ để trang trí.

### Áp dụng cho từng trang sinh viên

Các trang dưới đây dùng cùng sidebar, topbar, tiêu đề, nút, badge, bảng, form và icon ở các mục 2–5. “Bỏ” chỉ nói về nội dung trình bày; các thông tin vận hành quan trọng vẫn hiện ở vị trí được nêu.

| Trang             | Thứ tự khối trên màn hình                                                                   | Nội dung và hành động chính                                                             | Bỏ / chuyển vào chi tiết                                                                          |
| ----------------- | ------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| Đăng nhập         | Logo gọn → tiêu đề → form → lỗi tại form                                                    | MSSV/tài khoản, mật khẩu, Đăng nhập, thông báo sai/khóa tài khoản                       | Câu giới thiệu lặp tên hệ thống; ghi chú dài dưới form                                            |
| Dashboard         | Việc cần làm → lịch gần nhất → khóa học đang học → lối vào kỳ thi đang mở                   | Hạn gần nhất, trạng thái bài, liên kết mở bài/khóa/kỳ thi                               | Hero chào mừng, icon trang trí lớn, thống kê không dẫn đến quyết định                             |
| Khóa học của tôi  | Tìm/lọc → lưới khóa học                                                                     | Tên, mã, trạng thái, tiến độ cần thiết, Mở khóa học                                     | Banner “không gian học tập”; mô tả giống nhau ở mọi card                                          |
| Chi tiết khóa học | Breadcrumb → tên + đổi khóa → tab → nội dung tab                                            | Tab học liệu, lịch, bài tập, điểm danh, kết quả; trạng thái khóa                        | Lặp tên khóa trong nhiều box; câu hướng dẫn “chọn tab”                                            |
| Lịch học          | Chọn tuần/tháng → lịch → danh sách hoạt động chọn được                                      | Ngày, giờ, tên buổi, địa điểm, trạng thái; mở chi tiết                                  | Intro và legend dài; giữ tháng/ngày trong ô lịch                                                  |
| Điểm danh         | Buổi hiện tại → nút điểm danh nếu được phép → lịch sử                                       | Mã/QR hoặc điểm danh LAN theo luồng đang có, trạng thái có mặt/đến muộn/vắng            | Diễn giải dài về công nghệ LAN/QR trên mỗi dòng; giữ hướng dẫn cấp quyền camera tại điểm thao tác |
| Bài tập           | Chọn khóa → thanh tên khóa + đổi khóa → tiến độ gọn → lọc → danh sách                       | Tên/mã/nhóm, hạn, trạng thái, số lần nộp còn lại; Mở bài                                | Banner “Bước 1”, “Kế hoạch học tập”, “Mở để xem yêu cầu” và dòng phụ lặp ý                        |
| Chi tiết bài tập  | Tên + trạng thái/hạn → yêu cầu và file → nộp bài → lịch sử                                  | Giới hạn file, hạn, quy tắc nộp, phản hồi, tải file; Nộp bài                            | Thông tin tóm tắt lặp lại trong nhiều panel; không ẩn yêu cầu hay lỗi nộp                         |
| Kỳ thi / bài code | Danh sách kỳ thi → trạng thái/đồng hồ → danh sách câu hoặc đề file → vùng làm bài → lịch sử | Bắt đầu, mở đề, submit/nộp file, xem kết quả; giữ thông tin thời gian và điều kiện khóa | Banner chào thi, chú giải chung lặp ở từng câu; không ẩn test mẫu hoặc lỗi biên dịch              |
| Lịch sử nộp bài   | Bộ lọc → bảng các lần nộp → chi tiết                                                        | Bài, lần nộp, thời gian, kết quả, Tải về/Xem chi tiết                                   | Đoạn giới thiệu về lưu trữ ở đầu mỗi bảng                                                         |
| Kết quả học tập   | Bộ lọc khóa → bảng điểm → chi tiết nhận xét/quy tắc                                         | Điểm, trạng thái chưa chấm, trọng số khi cần giải thích tổng kết                        | Banner thành tích; không ẩn quy tắc tính điểm quan trọng                                          |
| Thông báo         | Bộ lọc đọc/chưa đọc → danh sách → nội dung                                                  | Tiêu đề, người gửi, thời gian, trạng thái đọc; mở/đánh dấu đọc                          | Intro và nhãn “mới” lặp nhiều lần trong cùng một hàng                                             |
| Tài khoản         | Thông tin cá nhân → form đổi mật khẩu                                                       | MSSV, tên, đổi mật khẩu, xác nhận thành công/lỗi                                        | Card giới thiệu tài khoản; giữ yêu cầu độ dài mật khẩu sát trường                                 |

### Áp dụng cho từng trang giảng viên/quản trị

| Trang               | Thứ tự khối trên màn hình                                                 | Nội dung và hành động chính                                                                   | Bỏ / chuyển vào chi tiết                                                              |
| ------------------- | ------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| Dashboard           | Việc cần xử lý → lịch dạy → khóa học → tác vụ nhanh                       | Bài chờ chấm, kỳ thi đang chạy, buổi sắp tới; mở việc cần xử lý                               | Banner giới thiệu và chỉ số không có hành động tiếp theo                              |
| Danh sách khóa học  | Tên trang + Tạo khóa → tìm/lọc → lưới khóa                                | Tên, mã, kỳ, sĩ số, trạng thái; Tạo/Mở khóa                                                   | Mô tả lặp ở mỗi card; cover hình quá cao                                              |
| Chi tiết khóa học   | Breadcrumb → tên + hành động khóa → tab → nội dung                        | Thành viên, lịch, học liệu, bài tập, điểm danh, bảng điểm; mỗi tab có toolbar và tác vụ riêng | Nhiều header khóa học lồng nhau; lời nhắc thao tác hiển nhiên                         |
| Kho bài tập & Đề    | Chọn khóa → tab câu hỏi/bộ đề → tìm/lọc → danh sách → editor/preview      | Tạo/import, chọn nhiều câu, kiểm tra test, tạo bộ đề, dùng lại cho thực hành/thi              | Banner quảng bá kho; hai danh sách câu hỏi song song; không ẩn ràng buộc import/test  |
| Cấu hình kỳ thi     | Danh sách kỳ thi → chi tiết kỳ thi theo nhóm form → kiểm tra trước mở     | Khóa học, loại thi, đề, thời gian, thí sinh, chính sách nộp/chấm; Lưu/Mở thi                  | Intro “quy trình kỳ thi” lặp; không ẩn cảnh báo cấu hình thiếu hoặc thời gian hết hạn |
| Giám sát            | Chọn khóa/kỳ thi → số liệu trực tiếp → bảng thí sinh → chi tiết           | Online, đang làm, đã nộp, cần chú ý; lọc và xử lý trường hợp cụ thể                           | Banner tổng quan không có dữ liệu; giữ giờ đồng bộ và nguồn dữ liệu quan trọng        |
| Bài nộp / chấm      | Tìm/lọc → bảng lần nộp → chi tiết file/code → điểm/nhận xét               | Người nộp, bài, lần, thời gian, trạng thái chấm; tải bản gốc, chấm/lưu                        | Dòng giải thích lưu trữ lặp; không ẩn lỗi thiếu file hay lịch sử chấm                 |
| Thông báo           | Danh sách đã gửi → tạo thông báo → chọn người nhận                        | Nội dung, phạm vi, người nhận, thời gian; Gửi, xem trạng thái gửi                             | Đoạn giới thiệu chung; giữ xác nhận phạm vi trước gửi                                 |
| Tài khoản sinh viên | Tìm/lọc → bảng tài khoản → thao tác trên người được chọn → nhập hàng loạt | MSSV, tên, khóa, trạng thái; tạo, khóa/mở, đặt lại mật khẩu, import                           | Hướng dẫn import dài trên trang chính; chuyển vào modal import và giữ file mẫu        |
| Tài khoản Admin     | Danh sách → tạo tài khoản → trạng thái                                    | Tên, trạng thái, quyền; Tạo/Khóa theo nghiệp vụ hiện có                                       | Card trang trí hoặc mô tả quyền lặp trên từng hàng                                    |
| Địa chỉ LAN         | Địa chỉ truy cập → trạng thái server → thao tác sao chép                  | URL hiện tại, địa chỉ trong mạng, tình trạng kết nối; Sao chép                                | Intro kỹ thuật dài; giữ cảnh báo kết nối thật sự cần thiết                            |

Ở trang có nhiều tab, mỗi tab tuân theo cùng mẫu: **tiêu đề khu vực + một hành động chính → bộ lọc nếu cần → nội dung → phân trang/trạng thái**. Thứ tự này không đổi tùy tiện giữa các tab. Khi một trường hợp đặc thù đòi bố cục khác, ghi lý do vào `UI.md` trước khi triển khai.

## 8. Kích thước cửa sổ máy tính, tương tác và khả năng tiếp cận

- Thiết kế cho màn hình máy tính từ 1280×720 trở lên; kiểm tra ở 1280×720, 1366×768, 1440×900 và 1920×1080. Cửa sổ hẹp 1024px phải giữ được tác vụ chính; bảng rộng cuộn trong vùng riêng. Không thiết kế breakpoint điện thoại.
- Thứ tự tab và focus phải theo thứ tự đọc. Mọi thao tác dùng được bằng bàn phím; trạng thái focus nhìn rõ với viền xanh và offset.
- Không dùng placeholder thay label. Các trường bắt buộc, lỗi và giới hạn cần được đọc bằng trình hỗ trợ; cập nhật bất đồng bộ dùng `role="status"` hoặc `aria-live` ở đúng nơi.
- Modal giữ focus bên trong khi mở và trả focus về nút mở khi đóng. Nút, link và hàng click được phải có ngữ nghĩa đúng.
- Motion chỉ dùng cho phản hồi ngắn 120–200ms; tôn trọng `prefers-reduced-motion`.
- Các trạng thái phải được thiết kế và kiểm tra: loading, rỗng, lỗi, chưa lưu, đang lưu, thành công, bị khóa, quá hạn, không có quyền và dữ liệu dài.

### Mục tiêu accessibility đo được trên desktop

- Tương phản chữ thường tối thiểu **4.5:1**, chữ lớn tối thiểu **3:1**; viền/biểu tượng cần để nhận biết thành phần và trạng thái tối thiểu **3:1** với màu kề bên. Tính theo cặp màu thực tế gồm cả nền hover/selected, không chỉ bảng token.
- Mục tiêu cho nút icon-only và điều khiển nhỏ: vùng nhấn tối thiểu **32×32 CSS px**, ưu tiên 40×40px. Ngưỡng WCAG 2.2 AA là **24×24 CSS px hoặc có khoảng cách ngoại lệ phù hợp**. Không thu nhỏ vùng nhấn chỉ vì icon có kích thước 16px.
- Kiểm tra zoom trình duyệt 125%, 150% và 200% trên màn hình desktop; không che nút, mất chữ hay làm nội dung quan trọng không thể truy cập. Kiểm tra reflow 320 CSS px nếu sau này cần tuyên bố tuân thủ WCAG AA đầy đủ; đây là tiêu chí zoom/accessibility, không phải yêu cầu thiết kế điện thoại.
- Focus bàn phím không bị header/sidebar/modal che; Tab đi theo thứ tự hợp lý; Escape xử lý modal; trạng thái mở/đóng và chọn/không chọn có ngữ nghĩa đúng. Không dùng `outline: none` nếu thiếu chỉ báo focus thay thế.
- Có label/name/role/value cho form và control tùy chỉnh. Thông báo lỗi xác định trường lỗi, nói cách sửa, và được công bố cho công cụ hỗ trợ. Chuyển động tắt hoặc giảm khi người dùng bật `prefers-reduced-motion`.

Các con số là **tiêu chí nghiệm thu desktop**, không phải tuyên bố ứng dụng hiện tại đã đạt WCAG AA đầy đủ. Kiểm tra bằng công cụ tự động kết hợp bàn phím, screen reader và quan sát thủ công; công cụ tự động không đủ để kết luận toàn diện.

## 9. Quản trị quy chuẩn và nghiệm thu

### Nguồn chuẩn trong code

- `UI.md` quyết định tên token, vai trò icon và quy tắc nội dung. Token mới phải được cập nhật ở đây cùng với code.
- CSS nền tảng sở hữu token và component phổ biến; CSS theo trang sở hữu layout đặc thù. Template/JS sinh markup dùng cùng class component, không tự chế biến thể chỉ khác vài pixel.
- Mỗi component có bản mẫu ở ít nhất các trạng thái: default, hover, focus, disabled, loading, error, empty khi phù hợp. Thay đổi component phải rà cả sinh viên lẫn admin.
- Không duy trì hai đường dẫn UI cho cùng một chức năng. Dữ liệu và logic nghiệp vụ ở backend hiện có được giữ khi thay giao diện.

### Checklist cho từng màn hình trước khi hoàn tất

- [ ] Người dùng thấy tiêu đề, phạm vi và tác vụ chính ngay khi mở; không có banner giới thiệu hoặc `more-detail` lặp ý.
- [ ] Hạn, trạng thái, điểm, lỗi và giới hạn có ý nghĩa vẫn đọc được; không bị selector toàn cục ẩn.
- [ ] Dùng đúng token, cỡ chữ, khoảng cách, icon và tên hành động; không có màu/độ bo mới tùy tiện.
- [ ] Dữ liệu rỗng, loading, lỗi, quá dài và thao tác đang lưu đều có giao diện.
- [ ] Hoạt động ở 1280×720, 1366×768, 1440×900 và 1920×1080; cửa sổ 1024px và zoom 200% không che tác vụ chính.
- [ ] Bàn phím và screen reader đi được luồng chính; contrast và target size được kiểm tra.
- [ ] Chức năng chính, điều hướng, lưu dữ liệu và quyền truy cập qua API vẫn đúng.

### Tài liệu tham chiếu

- [WCAG 2.2 — W3C](https://www.w3.org/TR/WCAG22/)
- [Hướng dẫn tương phản chữ — W3C](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum)
- [Kích thước mục tiêu tương tác — W3C](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum)
- [Mẫu modal dialog và quản lý focus — W3C](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/)

## 10. Cách triển khai trong repo

1. Đưa token và component dùng chung vào `static/css/design-system.css`. Trong giai đoạn chuyển đổi, tải sau CSS màn hình để thống nhất các thành phần cũ; khi CSS màn hình đã dùng token trực tiếp, tách token nền tảng lên trước. CSS theo màn hình chỉ chứa bố cục/chức năng đặc thù; hạn chế selector quá dài và `!important`.
2. Chọn **một màn hình mẫu**: Bài tập sinh viên. Xóa các đoạn `more-detail` và banner từ `static/js/student-workspace.js`, sắp lại header, toolbar, danh sách, chi tiết; xác nhận ở các kích thước desktop đã chốt.
3. Áp dụng thành phần đã chốt cho Dashboard/Khóa học/Kỳ thi sinh viên, rồi Khóa học/Kho bài tập & Đề/Kỳ thi/Giám sát quản trị.
4. Gỡ `static/css/no-more-details.css` khỏi `templates/base.html`; xóa đoạn giới thiệu thừa tại template/JS thay vì ẩn bằng CSS. Giữ thời hạn, trạng thái, điểm, lỗi và giới hạn ở đúng ngữ cảnh.
5. Không đưa các tệp thử nghiệm ngân hàng câu hỏi cũ vào UI mới nếu chức năng tương đương đã có trong `app/exercise_bank.py`, `app/question_papers.py` và `static/js/question-bank.js` của nhánh `dev`.

Một màn hình được coi là hoàn tất khi người dùng làm được tác vụ chính không cần đoán; không còn banner hoặc dòng chữ phụ lặp ý; dữ liệu quan trọng vẫn hiện; trạng thái lỗi/rỗng rõ ràng; dùng được trên máy tính và bằng bàn phím; các nút/API cũ tiếp tục hoạt động.

### Ghi nhận triển khai hợp đồng form (12/11/2026)

`design-system.css` tải sau CSS màn hình trong giai đoạn chuyển đổi. Các builder gắn `data-ui-form` và dùng `ui-forms.js` để tạo `ui-form-section`, `ui-form-grid`, `ui-span-2`, `ui-choice-group` và `ui-action-bar` từ chính các control đang có; không thay tên trường, giá trị, listener hoặc phạm vi fieldset disabled. Workspace giữ phần tử `dialog open` không modal với `role="region"` và giữ nguyên container bắt sự kiện gửi form. Màu chữ success/warning bổ sung đạt tương phản khoảng 5.17:1/4.81:1 trên nền badge tương ứng; không thay màu nền tảng đã chốt.
