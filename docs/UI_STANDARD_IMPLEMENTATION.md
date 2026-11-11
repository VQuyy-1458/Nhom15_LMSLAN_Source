# Triển khai UI.md

## Phần đã chuyển đổi

- `design-system.css` sở hữu token ngữ nghĩa, chữ, khoảng cách, nút, form, bảng,
  badge, tab và surface chung. File tải sau CSS theo màn hình trong giai đoạn chuyển đổi. Body có
  trạng thái `ui-standard`; không còn nạp `ui-polish.css`.
- Bỏ hero chào mừng, header dạng banner, eyebrow và các đoạn giới thiệu lặp
  trong template/JS. Không có selector ẩn toàn bộ `small`, `.muted`, `.fine-print`.
- Dashboard sinh viên ưu tiên việc cần làm và lịch; Dashboard quản trị ưu
  tiên bài chờ chấm/kỳ thi đang mở, lịch dạy và khóa học.
- Danh sách khóa học dùng header + toolbar + card thấp, một icon khóa học,
  tên mở được, metadata cần thiết và nút ở đáy card.
- Bài tập sinh viên có tìm khóa, chuyển khóa, tiến độ bài file, tìm theo
  tên/mã, lọc nhóm/trạng thái, tuần học nâng cao và xóa lọc. Dòng bài giữ hạn,
  trạng thái và số lượt còn lại; chi tiết giữ yêu cầu, tệp và lịch sử.
- Chi tiết bài tập, form câu hỏi, đề, tuần học, phiên thực hành và chấm thử
  dùng workspace trong trang. Tác vụ ngắn dùng modal, có Tab trap, Escape,
  khôi phục focus và xác nhận khi bỏ thay đổi chưa lưu.
- Import tài khoản mở trong modal, giữ nguyên node form/listener/kết quả khi
  đóng/mở. Form tạo Admin có label và quy tắc mật khẩu sát trường.
- Kho bài nộp hiển thị tìm kiếm, hình thức và trạng thái trước; các bộ lọc
  khác nằm trong disclosure, giữ nguyên tên trường và query.
- Thông báo quản trị có danh sách 30 bản ghi gửi gần nhất trước form soạn;
  form gửi thành công cập nhật danh sách. Đây chỉ là bổ sung biểu diễn dữ
  liệu đã có; không thêm endpoint hoặc đổi quy tắc người nhận.
- Icon dùng một nguồn Font Awesome cục bộ cho hai vai trò. Bộ chuẩn hóa icon
  giữ các tên cũ tương thích; không còn SVG thay riêng cho Admin.
- Có lỗi validation gần trường, `aria-invalid`/`aria-describedby`, thông tin
  file được chọn, tên truy cập cho nút có tooltip và trạng thái chọn của tab.
- Cặp màu chữ trạng thái trên nền nhạt được đo lại; token chữ bổ sung được
  ghi trong `UI.md`. Mã nguồn/editor/test case giữ font monospace.

## Giữ nguyên nghiệp vụ

URL, form names, request body, session, phân quyền, quy tắc thi, chấm bài và
thời gian server được giữ. Form workspace vẫn là `dialog open` không modal,
với `role="region"`, để tương thích `.close()`/sự kiện close mà các form đang
dùng. Nội dung danh sách chỉ tạm ẩn khi workspace mở và được khôi phục khi đóng.

UI nộp bài hiện phản ánh cả trạng thái bài đã đóng và định dạng mà backend
cho phép; backend vẫn quyết định việc nhận bài.

## Kiểm tra đã thực hiện

- 160 tổ hợp trang/kích thước: 20 trang chính và 12 tab khóa học ở
  1280×720, 1366×768, 1440×900, 1920×1080 và 1024×768.
- Kiểm tra tương tác: lọc/xóa lọc, giữ điều khiển upload, workspace chi tiết
  bài tập/câu hỏi/đề, bỏ nháp, Tab trong modal, Escape, trả focus, đóng/mở
  import, validation và viewport tương đương zoom 125%, 150%, 200%.
- Đã xác nhận lưu một đề file từ workspace qua API hiện có, sau đó lưu trữ
  bản nháp kiểm thử; không dùng dữ liệu đang vận hành.
- 74 kiểm thử `test_learning.py`: qua, một kiểm thử Docker thật được bỏ qua.
- 8 kiểm thử `test_course_learning.py`: qua.
- Kiểm tra trình duyệt luồng vào thi code, countdown, khóa khi hết hạn,
  giữ giờ kết thúc chung: qua, dùng judge fixture.
- Kiểm tra cú pháp JavaScript, biên dịch template Jinja, list controls,
  CSV test case và tương phản các cặp token/component: qua.

Lệnh kiểm tra giao diện với bộ mẫu riêng, khi thư mục đó không được server sử dụng:

```powershell
$env:CSS_UI_QA_ROOT = "$PWD/sample-data/ui-review"
node tests/browser_ui_consistency.cjs --system-data --desktop --standard
```

Ảnh và báo cáo: `previews/system-data/desktop/`.

Đây là kết quả kiểm thử desktop và các luồng nêu trên, không phải chứng nhận
WCAG AA toàn hệ thống. Chưa kiểm tra screen reader thủ công hoặc chấm code
bằng Docker thật trong đợt thay đổi này. Giao diện điện thoại không thuộc
phạm vi thiết kế mới; các breakpoint cũ còn được giữ cho cửa sổ/zoom hẹp.

Sau khi cập nhật, khởi động lại server để nạp phần lịch sử thông báo quản trị,
rồi Ctrl+F5 trên trình duyệt để tải bộ tài nguyên phiên bản mới.


## Cập nhật theo UI.md mới — 12/11/2026

- Đổi nguồn CSS chung thành `static/css/design-system.css`, tải cuối nhóm
  stylesheet trong head; gỡ tham chiếu cũ `ui-system.css` và giảm độ dài selector.
- Header/card dùng class hợp đồng `ui-page-bar`, `ui-course-grid`, `ui-course-card`
  song song hook cũ để giữ điều hướng, tìm kiếm và xử lý sự kiện.
- Builder khai báo `data-ui-form`; `ui-forms.js` tạo các section/grid từ control
  hiện có. Các profile gồm câu hỏi, bộ đề, tuần, thực hành, khóa học, bài tập,
  học liệu, lịch, kỳ thi, danh sách thi, thời gian thi và cấu hình thi file.
- Workspace tối đa 1120px; nhóm trường hai cột ở 1280px, một cột ở 1024px;
  textarea/file/lựa chọn lớn trải hai cột. Trường ngắn lẻ được trải đủ hàng.
- `ui-choice-group` bỏ viền mặc định của fieldset; empty state ở lựa chọn học
  liệu/câu/đề có liên kết bổ sung nội dung. Quy tắc dài dùng `ui-rule-details`;
  hạn, lỗi và ràng buộc nhập liệu vẫn hiện tại nhóm tương ứng.
- Thanh `ui-action-bar` nằm cuối nhóm form, có viền phân tách, một primary
  đặt sau hành động phụ. Label/id độc lập của cấu hình file được giữ nguyên.
- Phạm vi lọc khóa và khóa sở hữu kỳ thi là hai thao tác khác nhau; trường
  đổi sở hữu được ghi nhãn rõ, không loại bỏ chức năng chuyển kỳ thi sang khóa khác.
- Workspace giữ container gốc để submit vẫn đến listener ủy quyền hiện có.
  Khi save tải lại nội dung, trạng thái tạm ẩn và focus được khôi phục cả khi
  phần tử bị render lại mà không phát sự kiện close.
- Có utility `[hidden]` để grid/flex không vô tình hiện editor đang ẩn; không
  có quy tắc ẩn hàng loạt `.muted`, `small` hoặc `.fine-print`.
- Bảng token trong UI.md đã bổ sung viền control và màu chữ badge đang dùng;
  ghi rõ Font Awesome là nguồn icon chung hiện tại.

Kiểm tra mới trong `tests/ui_contract_interactions.cjs` đo width/grid/action
bar trên form thật, kiểm tra payload và listener trước/sau nhóm trường,
fieldset disabled, ẩn editor, lưu khóa học và các luồng workspace cũ.
Ảnh form: `previews/ui-contracts/`.

Chạy kiểm tra bản mới:

```powershell
$env:CSS_TEST_PYTHON = "python"
$env:CSS_UI_QA_ROOT = "$PWD/sample-data/ui-contract-review"
node tests/browser_ui_consistency.cjs --system-data --desktop --contracts --standard
```

Bộ dữ liệu kiểm tra này tách khỏi `sample-data/full-system` và dữ liệu mặc định.
Các giới hạn screen reader thủ công/chấm Docker thật nêu trên vẫn áp dụng;
không suy ra chứng nhận WCAG AA từ các kiểm tra bố cục.


### Kết quả kiểm tra sau cập nhật

- 160 trường hợp màn hình desktop với dữ liệu mẫu riêng: đạt, không ghi nhận lỗi bố cục trong bộ kiểm tra.
- Kiểm tra workspace, hộp thoại, bàn phím và zoom 125/150/200%: đạt.
- Hợp đồng form: đạt; gồm giới hạn 1120px, lưới hai/một cột, không bỏ trống nửa hàng,
  fieldset, thanh hành động, bảo toàn FormData/listener/disabled và tạo khóa học thực tế.
- 74 bài kiểm tra learning: đạt, bỏ qua 1 trường hợp phụ thuộc môi trường; 8 bài course-learning: đạt.
- Cú pháp 42 tệp JavaScript liên quan, phân tích template Jinja và độ tương phản token: đạt.
- Đây là kết quả kiểm tra tự động và rà soát ảnh giao diện; phần nghiệm thu screen reader thủ công
  và môi trường chấm Docker thực tế vẫn cần thực hiện riêng.
