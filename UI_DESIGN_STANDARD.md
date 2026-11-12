# Quy chuẩn giao diện dùng lại — Classroom LAN

> Phiên bản 1.1 · Nguồn tham chiếu: giao diện đang chạy của `[Old] ClassroomSubmissionServer`.
> File này tự chứa: có thể sao chép sang một web khác mà không cần mang theo mã nguồn web gốc.

## 1. Cách AI sử dụng file này

- Đọc toàn bộ file trước khi tạo, sửa hoặc đánh giá giao diện. Dùng nó làm chuẩn về **hình thức và tương tác** cho trang mới và trang được yêu cầu chỉnh sửa.
- Khi xây web mới theo file này, dùng đúng stack ở mục 3: Python standard library HTTP server + Jinja2, HTML, JavaScript thuần, Tailwind CSS 3.4.17 build local, `app.css` và Font Awesome local. Không tự đổi sang React/Vue hoặc CSS framework khác.
- Nếu đang chỉnh một web có sẵn kiến trúc khác, trước tiên giữ backend/API và dữ liệu của web đó; áp dụng giao diện bằng HTML/CSS/JS tương đương. Chỉ chuyển stack khi người dùng yêu cầu rõ.
- Giữ nguyên dữ liệu, quy tắc nghiệp vụ, quyền truy cập, API, tên sản phẩm và luồng chính của web đích, trừ khi yêu cầu của người dùng nói khác. Thay nội dung mẫu “Classroom Submission Server”, “MSSV”, “đề thi” bằng nội dung đúng của web đích.
- Nếu web đích có quy định pháp lý, thương hiệu hoặc trợ năng cụ thể, tuân theo quy định đó trước; dùng các quy tắc còn lại ở đây để giữ sự thống nhất.
- Khi hoàn tất, kiểm tra ít nhất trang đăng nhập (nếu có), một trang nội dung chính, một form, một bảng/danh sách và màn hình hẹp. Nêu rõ điểm nào chưa áp dụng được.
- **Để AI tự tìm thấy file sau khi sao chép:** đặt ở thư mục gốc và thêm một dòng trong `AGENTS.md`, `CLAUDE.md` hoặc tài liệu hướng dẫn AI của web đích: “Đọc `UI_DESIGN_STANDARD.md` trước mọi thay đổi giao diện.” Nếu không có file hướng dẫn AI, nhắc tên file này trong yêu cầu.

## 2. Phạm vi và tính cách thị giác

Thiết kế như một công cụ nội bộ dùng hằng ngày: rõ ràng, đáng tin, ít trang trí, đọc nhanh được nhiều trạng thái. Nền sáng xám xanh, bề mặt trắng, chữ xanh than, hành động chính xanh dương. Dùng độ nổi nhẹ qua viền và bóng nhỏ; không dùng gradient đậm hoặc hiệu ứng gây xao nhãng. Gradient xanh rất nhạt chỉ phù hợp nền trang đăng nhập.

Phạm vi áp dụng: bố cục, màu, chữ, khoảng cách, nút, biểu mẫu, card, bảng, trạng thái, thông báo, điều hướng, responsive và hành vi phản hồi. File này không định nghĩa database, API, bảo mật, logic chấm điểm hoặc nội dung nghiệp vụ.

## 3. Công nghệ và cấu trúc bắt buộc

### Stack giống web gốc

| Lớp | Công nghệ | Quy tắc |
|---|---|---|
| HTTP/backend | Python 3.10+, `http.server.ThreadingHTTPServer` | Một process phục vụ route và tài nguyên tĩnh; không cần Node lúc runtime. |
| Render HTML | Jinja2 `>=3.1,<4` | `base.html` chứa `<head>`, CSS/JS chung; trang khác dùng `{% extends "base.html" %}`. Escape dữ liệu người dùng theo mặc định của Jinja2. |
| Tương tác | JavaScript thuần dùng DOM, `fetch`, `FormData` | Mỗi trang/nhóm chức năng có file JS riêng; helper chung cho request, toast và escape. Không dùng React, Vue, jQuery hoặc thư viện state nếu chưa có nhu cầu cụ thể. |
| Styling | Tailwind CSS `3.4.17` + `static/css/app.css` | Tailwind cho bố cục/utility; `app.css` cho token, component và trạng thái. Không tạo CSS inline rải rác. |
| Biểu tượng | Font Awesome 4.7 local | **Chỉ dùng một họ icon Font Awesome 4.7** trên toàn web, tải từ `static/vendor/fontawesome/`; không trộn Lucide, Material Icons, Bootstrap Icons, emoji hay icon font khác. |
| Tài nguyên | CSS, JS, font đều local | Web chạy khi không có Internet; không nhúng CDN. |

Node/npm chỉ dùng lúc phát triển để chạy `npm run build:css`. File `assets/tailwind.input.css` có ba directive `@tailwind base/components/utilities`; `tailwind.config.js` quét `templates/**/*.html` và `static/js/**/*.js`. Bản CSS đã build được phục vụ từ `static/css/tailwind.css`. Khi thêm class Tailwind mới, build lại file này trước khi kiểm tra giao diện.

### Cấu trúc tối thiểu khi tạo web mới

```text
app/                    # Python server, routes và logic
templates/
  base.html             # lang="vi", viewport, CSS/JS chung, block body
  login.html
  admin.html
  student.html          # hoặc trang người dùng tương đương
static/
  css/app.css           # tokens, component, responsive
  css/tailwind.css      # output đã build
  js/app.js             # fetch/toast/escape dùng chung
  js/<page>.js          # hành vi riêng từng trang
  vendor/fontawesome/   # CSS + font local
assets/tailwind.input.css
tailwind.config.js
package.json            # chỉ build CSS
requirements.txt        # Jinja2
```

Trong `base.html`, giữ thứ tự tải CSS: `tailwind.css` → `app.css` → Font Awesome local; tải `app.js` bằng `defer`. Các trang khai báo `<main>` duy nhất, title riêng, heading h1 riêng. Dữ liệu đưa vào HTML qua Jinja2; mã JS không ghép chuỗi HTML từ dữ liệu chưa escape.

## 4. Design tokens

Định nghĩa token tập trung trong theme/CSS variables của web đích. Không rải mã màu thô trong từng trang.

| Token | Giá trị chuẩn | Vai trò |
|---|---|---|
| `--color-canvas` | `#f4f7fb` | Nền ứng dụng |
| `--color-surface` | `#ffffff` | Card, panel, topbar |
| `--color-surface-soft` | `#f8faff` | Mục phụ, hover rất nhẹ |
| `--color-text` | `#172033` | Chữ chính |
| `--color-heading` | `#1f3150` | Tiêu đề và brand |
| `--color-muted` | `#77849a` | Mô tả, metadata |
| `--color-border` | `#e4eaf2` | Viền card |
| `--color-input-border` | `#dbe2ed` | Viền field |
| `--color-primary` | `#245edb` | Nút chính, liên kết quan trọng |
| `--color-primary-hover` | `#194bb9` | Hover nút chính |
| `--color-primary-soft` | `#eaf2ff` | Nền icon/badge xanh |
| `--color-focus` | `#6693f5` | Viền focus |
| `--color-sidebar` | `#172b4d` | Nền điều hướng quản trị |
| `--color-sidebar-text` | `#c7d3e8` | Chữ điều hướng |
| `--color-danger` | `#a32e32` | Lỗi và hành động nguy hiểm |
| `--color-warning` | `#8a5b06` | Cảnh báo |
| `--color-info` | `#1d4f94` | Thông tin |

Trạng thái thành công dùng xanh lá, cảnh báo dùng hổ phách, lỗi dùng đỏ, thông tin dùng xanh dương. Luôn có chữ hoặc icon đi kèm màu; không dùng màu làm tín hiệu duy nhất. Kiểm tra tương phản chữ thường ít nhất 4.5:1 và chữ lớn ít nhất 3:1.

**Chữ:** ưu tiên Inter; fallback `ui-sans-serif, system-ui, "Segoe UI", sans-serif`. Chữ nội dung mặc định 16px, line-height khoảng 1.5. Tiêu đề trang 27–30px, đậm; tiêu đề panel 17–20px; nhãn form và bảng 13–14px, rõ nét. Metadata có thể 12–13px, không dùng chữ nhỏ hơn 12px cho nội dung cần đọc. Dùng tối đa hai mức độ đậm chính: 600–700 cho nhãn và 750–800 cho tiêu đề/số liệu.

**Khoảng cách:** dùng thang 4 / 8 / 12 / 16 / 24 / 32px. Gap giữa field 10–12px; giữa nội dung trong card 12–16px; giữa các panel 20–24px. Không đặt mọi phần tử cách đều nhau: nhóm theo ý nghĩa.

**Bo góc và bóng:** input/nút 9px; card nhỏ 12–14px; panel 16px; card đăng nhập 22px. Bóng card nhẹ, ví dụ `0 4px 14px #12294a08`; viền mảnh vẫn là ranh giới chính.

### CSS khởi đầu có thể sao chép

Đặt đoạn này ở đầu `static/css/app.css` khi tạo web mới. Đây là **token nền**; phần component ở dưới vẫn cần CSS riêng. Nếu web đích đã có token, ánh xạ tên cũ sang các giá trị này một lần.

```css
:root {
  --color-canvas: #f4f7fb;
  --color-surface: #ffffff;
  --color-surface-soft: #f8faff;
  --color-text: #172033;
  --color-heading: #1f3150;
  --color-muted: #77849a;
  --color-border: #e4eaf2;
  --color-input-border: #dbe2ed;
  --color-primary: #245edb;
  --color-primary-hover: #194bb9;
  --color-primary-soft: #eaf2ff;
  --color-focus: #6693f5;
  --color-sidebar: #172b4d;
  --color-sidebar-text: #c7d3e8;
  --color-danger: #a32e32;
  --color-warning: #8a5b06;
  --color-info: #1d4f94;
  --radius-control: 9px;
  --radius-card: 16px;
  --shadow-card: 0 4px 14px #12294a08;
  font-family: Inter, ui-sans-serif, system-ui, "Segoe UI", sans-serif;
  color: var(--color-text);
  background: var(--color-canvas);
}
*, *::before, *::after { box-sizing: border-box; }
body { margin: 0; min-height: 100vh; }
```

Nếu dùng Inter, đóng gói file font trong `static/` và khai báo `@font-face`; nếu không, dùng system UI. Không tải font từ CDN. Thang chữ tham khảo: eyebrow 10–11px/800 chữ hoa có letter-spacing; label 13px/700; body 16px/400; heading panel 18px/700; heading trang 30px/800. Nội dung bảng có thể 13–14px nhưng phải đọc được ở mức zoom 200%.

## 5. Bố cục trang

### Đăng nhập

- Một card trắng duy nhất, căn giữa, rộng tối đa khoảng 450px; nền `--color-canvas` với điểm sáng xanh rất nhạt ở góc trên trái.
- Thứ tự: biểu tượng/brand → tiêu đề → mô tả ngắn → nhãn và field → nút chính full width → ghi chú. Không thêm panel minh họa chiếm nửa màn hình.
- Field có nhãn luôn hiện. Lỗi xuất hiện gần form bằng màu lỗi và câu hướng dẫn rõ ràng. Giữ nút ở trạng thái loading khi gửi.

### Trang quản trị

- Desktop: sidebar cố định khoảng 250px, nền xanh than; topbar trắng cao khoảng 68px; vùng nội dung có chiều rộng tối đa khoảng 1380px và padding ngang 24px.
- Sidebar chia nhóm bằng nhãn nhỏ, mục đang chọn có nền xanh dương và chữ trắng. Icon đứng trước nhãn; không dùng icon đơn độc cho mục điều hướng.
- Đầu trang có đường hướng/nhãn ngữ cảnh, một tiêu đề chính, mô tả ngắn và trạng thái hệ thống nếu hữu ích.
- Dashboard đặt số liệu quan trọng trong stat card, sau đó mới tới nhóm thao tác và bảng. Không lặp cùng số liệu ở nhiều vùng mà không có lý do.
- Sidebar rộng 250px khi màn lớn, 220px ở khoảng dưới 1100px; vùng nội dung có `margin-left` tương ứng. Sidebar brand cao 68px; mỗi mục menu có padding khoảng `10px 11px`, gap icon/nhãn 12px và nhãn nhóm chữ hoa 10px. Mục đang chọn dùng nền `#2f6fed`.
- Lưới thống kê desktop 4 cột, gap 16px; card nền trắng, viền `#e5eaf2`, bo 14px, padding 18px. Icon số liệu nằm trong ô 44×44px nền trạng thái nhạt. Panel chung padding 22px, margin dưới 20px.
- Bảng quản trị có thanh tìm kiếm/lọc phía trên và vùng `overflow-x: auto` riêng. Cột hành động đặt ở cuối; cập nhật dữ liệu có thời điểm cập nhật hoặc trạng thái loading.

### Trang người dùng đơn giản

- Dùng topbar trắng và vùng nội dung hẹp hơn, tối đa khoảng 900px. Một panel chính cho tác vụ hiện tại, các thông tin phụ xếp sau.
- Trạng thái chưa có dữ liệu có icon, tiêu đề ngắn, giải thích và bước tiếp theo khi có thể.
- Header có brand trái và hành động tài khoản phải. Khối chào mừng đặt tên người dùng, mã/metadata và badge trạng thái ở cùng nhóm. Một tác vụ chính nằm trong panel trắng; trước khi có dữ liệu hiện empty state, sau khi có dữ liệu hiện trạng thái/tác vụ theo thứ tự người dùng cần thực hiện.

### Mẫu khung HTML/Jinja

```html
{# templates/base.html #}
<!doctype html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block title %}Tên ứng dụng{% endblock %}</title>
  <link rel="stylesheet" href="/static/css/tailwind.css">
  <link rel="stylesheet" href="/static/css/app.css">
  <link rel="stylesheet" href="/static/vendor/fontawesome/css/all.min.css">
  <script defer src="/static/js/app.js"></script>
</head>
<body class="app-body">
  {% block body %}{% endblock %}
  <div id="toast" class="toast hidden" role="status" aria-live="polite"></div>
</body>
</html>
```

Trang đăng nhập dùng `<main class="login-shell ui-page">` chứa `<section class="login-card ui-card">`. Trang admin dùng `admin-shell` với `aside.main-sidebar`, `header.topbar`, `main.page-wrap`. Trang người dùng dùng `header.topbar` và `main.page-wrap.narrow.ui-page`. Đây là tên class khuyến nghị để giữ tương thích cách tổ chức CSS của web gốc.

## 6. Thành phần dùng chung

| Thành phần | Cách thể hiện |
|---|---|
| Nút chính | Nền `--color-primary`, chữ trắng, bán kính 9px; hover đậm hơn. Mỗi vùng tác vụ chỉ nên có một hành động chính. |
| Nút phụ | Nền trắng, viền `--color-input-border`, chữ xanh than. |
| Nút nhẹ | Nền trong suốt, dùng cho thao tác ít quan trọng như đăng xuất hoặc hủy. |
| Form field | Nền trắng, viền 1px, bán kính 9px, padding khoảng 11–12px; focus có viền xanh và vòng sáng nhạt. |
| Panel/card | Nền trắng, viền `--color-border`, bán kính 14–16px, padding 18–24px, bóng nhẹ. |
| Badge/trạng thái | Dạng pill nhỏ; màu nền nhạt, chữ đậm; luôn có nhãn diễn đạt trạng thái. |
| Bảng | Có tiêu đề cột, phân hàng rõ, thao tác ở cột cuối; bảng rộng nằm trong vùng cuộn ngang riêng trên màn hình hẹp. |
| Thông báo | Info xanh, warning vàng, error đỏ; một câu nêu vấn đề và một câu nêu việc cần làm nếu có. |
| Icon | Chỉ dùng Font Awesome 4.7 local. Icon đứng trước nhãn và có cùng cỡ trên các mục cùng cấp. Icon trang trí cần ẩn khỏi trình đọc màn hình. |

Trạng thái hover, focus, disabled, loading, thành công và lỗi phải có phản hồi nhìn thấy được. Không chỉ dựa vào toast cho lỗi form: lỗi phải ở gần field hoặc form. Thao tác nguy hiểm cần kiểu nút riêng và xác nhận phù hợp.

### Quy tắc icon duy nhất

- Dùng **Font Awesome 4.7 local** cho toàn bộ icon chức năng và trạng thái. Không cài hoặc nhúng thêm bộ icon khác. Không dùng emoji thay icon. Nếu một biểu tượng không có sẵn, chọn glyph gần nghĩa nhất trong cùng bộ hoặc diễn đạt bằng chữ; không phá quy tắc một bộ icon.
- Giữ cùng cỡ theo cấp: 14px trong nút/menu/bảng, 18–20px ở tiêu đề panel và card thống kê, 24px ở brand/empty state. Các icon nằm cùng hàng phải có chiều rộng/căn hàng thống nhất; khoảng cách tới nhãn khoảng 8–12px.
- Icon đi cùng chữ là trang trí: đặt `aria-hidden="true"` trên `<i>`. Nút chỉ có icon phải có `aria-label` diễn đạt hành động, ví dụ `<button aria-label="Mở menu"><i class="fa fa-bars" aria-hidden="true"></i></button>`.
- Dùng cùng glyph cho cùng hành động ở mọi trang: `fa-sign-in` đăng nhập, `fa-sign-out` đăng xuất, `fa-users` người dùng, `fa-desktop` giám sát, `fa-file-text-o` tài liệu/đề, `fa-cloud-upload` nộp file, `fa-refresh` làm mới, `fa-exclamation-triangle` cảnh báo. Không đổi icon của cùng hành động giữa các trang.
- Không thêm icon chỉ để trang trí dày đặc. Mỗi mục menu, nút có tác vụ và trạng thái chính có thể có một icon; đoạn văn thường không cần icon.

### CSS component cơ bản

```css
.btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 8px;
  border: 1px solid transparent; border-radius: var(--radius-control);
  padding: 10px 14px; font-size: 13px; font-weight: 750;
  text-decoration: none; cursor: pointer; transition: background-color .15s, border-color .15s;
}
.btn-primary { background: var(--color-primary); color: #fff; }
.btn-primary:hover:not(:disabled) { background: var(--color-primary-hover); }
.btn-secondary { background: #fff; border-color: #dce4f0; color: #34445f; }
.btn-ghost { background: transparent; color: #52617a; }
.btn:disabled { opacity: .45; cursor: not-allowed; }
.ui-action { min-height: 40px; }
.ui-form input:not([type="checkbox"]):not([type="radio"]),
.ui-form select, .ui-form textarea {
  width: 100%; padding: 11px 12px; border: 1px solid var(--color-input-border);
  border-radius: var(--radius-control); background: #fff; color: var(--color-text);
}
.ui-form input:focus-visible, .ui-form select:focus-visible,
.ui-form textarea:focus-visible, .btn:focus-visible, .sidebar-nav a:focus-visible {
  outline: 2px solid var(--color-focus); outline-offset: 2px;
}
.panel {
  background: var(--color-surface); border: 1px solid var(--color-border);
  border-radius: var(--radius-card); padding: 22px;
  margin-bottom: 20px; box-shadow: var(--shadow-card);
}
.table-scroll { overflow-x: auto; border: 1px solid #e7ebf2; border-radius: 10px; }
.status-pill { display: inline-flex; align-items: center; gap: 5px;
  padding: 5px 8px; border-radius: 999px; font-size: 12px; font-weight: 700; }
```

Đây là mẫu triển khai mới, không phải yêu cầu thay nguyên `app.css` của project Old. Khi áp dụng vào web có sẵn, kiểm tra cascade để tránh style cũ ghi đè. Không dùng `!important` làm giải pháp mặc định.

### Trạng thái cụ thể

| Loại | Nền / chữ / viền | Cách dùng |
|---|---|---|
| Thành công | `#e7f8ed` / `#197348` / xanh lá nhạt | Hoàn thành, đang hoạt động |
| Cảnh báo | `#fff3d8` / `#956208` / vàng nhạt | Gần hạn, cần chú ý |
| Lỗi | `#ffebeb` / `#b33232` / đỏ nhạt | Thất bại, quá hạn, bất thường |
| Thông tin | `#eaf2ff` / `#245edb` / xanh nhạt | Đã đăng nhập, thông tin trung tính |

Thông báo dạng `alert` nên ở ngay vùng liên quan, có icon phù hợp và câu rõ nghĩa. Toast nổi góc dưới phải, nền `#1f3150`, chữ trắng, bo 10px; chỉ dùng cho phản hồi ngắn sau thao tác. Loading dùng text như “Đang tải dữ liệu…” hoặc skeleton có kích thước cố định để tránh nhảy bố cục. Empty state không chỉ có icon: có tiêu đề và lời giải thích.

## 7. Responsive và trợ năng

- Thiết kế từ màn hình hẹp trước, mở rộng dần. Mốc tham khảo của web gốc: 560, 760, 900 và 1100px; chỉ thêm mốc mới khi bố cục thực sự cần.
- Dưới khoảng 760px, sidebar chuyển thành menu mở/đóng có nền phủ. Nội dung bỏ margin sidebar; card và form xếp một cột. Dưới 560px, lưới thống kê còn tối đa hai cột; nhóm nút quan trọng có thể full width.
- Không để toàn trang cuộn ngang. Với bảng nhiều cột, chỉ vùng bảng cuộn ngang hoặc đổi sang card theo hàng.
- Các nút/bộ điều khiển cần vùng chạm ít nhất 44×44px khi dùng trên di động. Có focus rõ, thứ tự Tab hợp lý, nhãn truy cập cho nút chỉ có icon.
- Dùng thẻ heading theo thứ bậc, label gắn với input, thông báo lỗi có thể được trình đọc màn hình nhận biết. Không khóa zoom.
- Chuyển động chỉ để báo phản hồi; thời lượng ngắn khoảng 150–200ms. Tôn trọng `prefers-reduced-motion`.

### Ma trận kích thước phải kiểm tra

| Viewport | Kết quả cần thấy |
|---|---|
| 1440px desktop | Sidebar cố định; topbar và panel thẳng hàng; dashboard tối đa 4 stat card/cột. |
| 1024px laptop/tablet ngang | Sidebar khoảng 220px; nội dung không bị ép chữ; lưới giảm cột khi cần. |
| 760px tablet dọc | Sidebar đóng mặc định thành menu; nút mở menu có nhãn truy cập; nội dung chiếm toàn chiều rộng. |
| 390–560px điện thoại | Login card có lề tối thiểu 16–24px; panel padding khoảng 13–17px; nút chính dễ bấm; lưới thống kê tối đa 2 cột. |
| 320px và zoom 200% | Không cắt nội dung hoặc che focus; bảng cuộn trong khung riêng; form vẫn hoàn thành được. |

Menu di động cần đóng khi người dùng chọn mục, bấm nền phủ hoặc bấm Escape; khi mở cập nhật `aria-expanded` cho nút. Nếu dùng dialog, đưa focus vào dialog và trả focus về nút mở khi đóng. Không làm menu chỉ hoạt động bằng hover.

### Trạng thái tương tác bắt buộc

- Form: nhãn luôn hiện; `required` và định dạng hiển thị rõ; khi lỗi giữ giá trị đã nhập (trừ mật khẩu theo chính sách), đặt thông báo dưới field hoặc gần nút và hỗ trợ `aria-describedby`.
- Submit: khóa nút trong lúc request, hiện tiến trình, mở lại khi thất bại; không gửi trùng. Thông báo thành công phải nói hành động đã hoàn tất.
- Bảng/danh sách: có trạng thái đang tải, rỗng và lỗi tải; ô tìm kiếm có nhãn truy cập; nút làm mới cho biết dữ liệu đã cập nhật.
- Trạng thái thời gian thực: hiện chữ “Đang kết nối”, “Đã kết nối” hoặc “Mất kết nối”; polling không làm mất focus hay cuộn lại trang.
- Màu và chuyển động: `prefers-reduced-motion: reduce` tắt chuyển động trang trí; thông tin không phụ thuộc màu hoặc animation.

## 8. Quy trình áp dụng cho web khác

1. Kiểm tra các trang và component hiện có; liệt kê những mẫu đang dùng trước khi sửa.
2. Khai báo tokens ở một nơi. Ánh xạ màu/chữ/bố cục cũ sang tokens; giữ lại tên thương hiệu và nội dung của web đích.
3. Tạo hoặc chuẩn hóa component nền tảng: Button, Input, Card/Panel, Badge, Alert, Table, Navigation.
4. Áp dụng theo thứ tự: khung trang → typography/màu → component → trạng thái tương tác → responsive.
5. Kiểm tra trang thật ở desktop và màn hình hẹp, dùng bàn phím để đi qua form/menu, chạy build/test sẵn có.

**Tiêu chí hoàn thành:** các trang cùng dùng một bảng màu và thang khoảng cách; nút/field/card cùng hình dạng; điều hướng và trạng thái dễ nhận ra; không có lỗi tràn ngang; form có nhãn và lỗi rõ; chức năng của web đích vẫn hoạt động.

### Lệnh kiểm tra với stack web gốc

```powershell
# Chỉ cần khi sửa template/class Tailwind hoặc file nguồn Tailwind
npm run build:css

# Kiểm tra cú pháp Python và test nghiệp vụ có sẵn
.\.venv\Scripts\python.exe -m compileall app run_server.py tests
.\.venv\Scripts\python.exe -m unittest discover -s tests

# Chạy và mở các trang thật để kiểm tra giao diện
.\.venv\Scripts\python.exe run_server.py
```

Nếu chưa có `node_modules`, chạy `npm ci` khi có lockfile hoặc `npm install` khi không có lockfile, rồi mới build CSS. Khi không sửa Tailwind, không cần cài Node để chạy server. Không dùng bản build thành công để thay cho kiểm tra giao diện trong trình duyệt: xem trang đăng nhập, một trang admin, một trang người dùng ở ít nhất desktop và điện thoại.

### Bàn giao cho AI ở web đích

Khi hoàn thành việc áp dụng file này, báo ngắn gọn: các trang đã chỉnh, component/tokens đã tạo, lệnh build/test đã chạy, hai kích thước màn hình đã kiểm tra và những điểm phải giữ khác chuẩn do yêu cầu của web đích. Không chép nguyên logo, tên sản phẩm, dữ liệu người dùng hoặc nội dung kỳ thi từ Classroom Submission Server.

## 9. Điểm tham chiếu từ web gốc

- `templates/base.html`: khung trang và tải CSS/JavaScript chung.
- `templates/login.html`, `templates/admin.html`, `templates/student.html`: ba kiểu trang đại diện.
- `static/css/app.css`: các giá trị giao diện hiện dùng.
- `tailwind.config.js`: màu brand và cấu hình Tailwind.

Các đường dẫn ở mục này chỉ giúp đối chiếu trong project Old. Khi mang file sang web khác, các mục 1–8 vẫn đủ để thực hiện quy chuẩn.
