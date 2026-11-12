# Nội dung tuần, bài tập code và quyền xem câu hỏi

Thực hiện trên nền `nv09` + `2H`; không ghép lại những nhánh đã rollback.

## Đối chiếu video

- 01:16–02:49: tuần/bài học có bài đọc, file chia sẻ, bài tập; thông báo có nơi xem rõ ràng.
- 05:20–06:55: giữ Tài liệu/Bài tập tổng hợp, mỗi mục một dòng; bấm để mở chi tiết và tìm theo tuần.
- 07:06–08:18: có bài tự luyện code; câu thực hành/thi riêng cho giảng viên, chỉ hiện khi giao.
- 17:03–18:10: câu hỏi chia theo mục đích Luyện tập/Thực hành/Thi và hình thức File/Code.

## Cách dùng

1. Giảng viên mở khóa học → **Nội dung theo tuần** → Thêm tuần. Nhập bài học/bài đọc và chọn nhiều tài liệu, bài tập, bài code hoặc thông báo. Một tài liệu có thể được dùng lại ở nhiều tuần. Nội dung chưa xếp tuần vẫn nằm trong danh sách tổng hợp.
2. **Tài liệu/Bài tập** là danh sách gọn có tìm kiếm, lọc tuần tự động và phân trang. Chi tiết nằm trong hộp thoại; file vẫn xem trực tiếp/tải xuống được.
3. Khóa học → **Bài tập → Kho câu hỏi**: thêm Code hoặc File và chọn mục đích. Code dùng lại editor, CSV test case, Customise/class/method/program của nv09.
4. **Luyện tập**: bấm Công bố để sinh viên trong lớp truy cập. Không có giờ thi chung và không tính điểm khóa học. Chạy test mẫu không tạo bài nộp; Submit mới lưu mã nguồn, bản chụp đề/test và kết quả.
5. **Thực hành**: tạo phiên, chọn câu Thực hành trong kho và danh sách MSSV (để trống = cả lớp). Lưu tạo bản nháp; bấm Mở thực hành mới phát cho sinh viên. Thời lượng tính từ lúc giảng viên mở cho cả lớp. Đóng tay hoặc hết thời gian đều chặn nộp tiếp. Thực hành File nhận file theo hạn chung; Code dùng cùng hàng đợi chấm/nguồn lưu/lịch sử với kỳ thi.
6. **Thi**: câu riêng tư trong kho. Ở Cấu hình kỳ thi → chi tiết đề code, bấm **Thêm câu từ kho của khóa học**. Nội dung được sao chép vào đề; đề chỉ được sinh viên đọc theo luồng mở thi hiện có.
7. Khóa học → **Thông báo** để đăng/xem thông báo riêng của khóa, có thể gắn vào tuần.

Vai trò quản lý hiện tại là tài khoản Admin/giảng viên của ứng dụng; thay đổi này phân quyền giữa tài khoản quản lý và sinh viên, không tạo thêm hệ thống tài khoản giảng viên riêng.

## Dữ liệu và chấm điểm

- Tất cả metadata dùng SQLite qua API storage hiện có: `learning.json` (thêm `course_weeks`), `course_questions.json`, `course_practicals.json` là tên document bên trong database.
- Bài nộp code dùng nguyên `programming-submissions/<id>/source` và `problem.json`, cùng `programming_submissions.json` và lịch sử chấm. File dùng kho bài nộp hiện tại.
- Đề thực hành được chụp lại khi tạo phiên, nên sửa câu trong kho không sửa đề đã giao. Test ẩn/template riêng không gửi cho sinh viên.
- Code thực hành lấy điểm tốt nhất từng bài toán, quy về 10 rồi tham gia thành phần Bài tập. Bài luyện tập (cả File lẫn Code) bị loại khỏi điểm tổng kết. Bài File thực hành chấm tay qua kho Bài nộp.
- Dùng chung giới hạn 6 lần nộp/người/phút cho File và Code. Chạy mẫu có giới hạn riêng và tối đa hai lượt chạy đồng thời.
- Các khóa đã tổng kết giữ chế độ chỉ đọc.

## Kiểm tra

`python -m unittest tests.test_course_learning` kiểm tra quyền, snapshots, deadline, điểm và liên kết tuần. `node tests/browser_student_qa.cjs --course-learning` kiểm tra cả hai giao diện và chấm Docker thật. Các fixture dùng database/thư mục tạm, không thay dữ liệu lớp.

`python scripts/seed_four_items_demo.py --apply` thêm một khóa demo riêng cho SV001; không xóa dữ liệu đang có. Chạy lại giữ nguyên khóa đã tạo.
