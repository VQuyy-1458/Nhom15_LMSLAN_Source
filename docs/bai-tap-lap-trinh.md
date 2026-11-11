# Bài tập lập trình

## Sử dụng

1. Giảng viên mở **Khóa học → Bài tập → Tạo bài tập lập trình**.
2. Nhập tên, chủ đề/tuần, hạn nộp theo giờ Việt Nam và chọn ngôn ngữ. Thêm bài toán, điểm, giới hạn thời gian/bộ nhớ và test case. Có thể dùng chức năng nhập test CSV hiện có.
3. Lưu bản nháp. Có thể sửa hoặc xóa bản nháp. Bấm **Giao bài**, chọn học viên đang hoạt động trong khóa học rồi xác nhận. Học viên chỉ thấy bài sau bước này.
4. Học viên mở **Bài tập → Bài tập lập trình → Mở bài tập**, chọn bài toán và viết code hoặc tải mã nguồn vào editor.
5. **Chạy thử** bằng test mẫu công khai hoặc input tự nhập. Kết quả chạy thử chỉ hiển thị cho người chạy, không ghi điểm, không tạo lần nộp và không chạy test ẩn.
6. **Submit bài** lưu mã nguồn, snapshot đề/test và đưa vào hàng đợi chấm toàn bộ test. Có thể nộp nhiều lần đến hạn.
7. Học viên xem lịch sử và kết quả từng bài. Giảng viên xem **Kết quả & lịch sử chấm**, tải mã nguồn hoặc chấm lại bằng snapshot đã lưu.

Bài đã giao khóa cấu hình đề/test để bảo toàn kết quả. Không có thao tác “kết thúc thi” cho bài tập; hạn nộp được kiểm tra ở backend. Khóa học đã tổng kết không nhận bài/chạy thử mới.

## Điểm và lưu trữ

- Mỗi bài toán tính điểm theo bộ chấm hiện có: điểm tối đa × số test đạt / tổng số test.
- Điểm một bài tập lấy điểm tốt nhất đã chấm của từng bài toán, cộng lại rồi quy về thang 10.
- Điểm này tham gia trung bình thành phần **Bài tập** của khóa học cùng các bài tập nộp file. Bài chưa nộp sau hạn nhận 0; bài đang chờ chấm chưa được tự biến thành 0.
- Metadata bài tập độc lập ở `data/programming_assignments.json`, được tạo khi lưu bài đầu tiên. Không chuyển bài tập cũ hoặc đề thi cũ sang cấu trúc mới.
- Dùng chung `programming_attempts.json`, `programming_submissions.json` và kho mã nguồn/snapshot hiện có. Các record mới có `activity_type: assignment`; `exam_id` là ID ngữ cảnh dùng chung của engine, có tiền tố `pa_` với bài tập.
- Bài tập lập trình không nằm trong danh sách kỳ thi, không tự mở bằng worker lịch thi và không tham gia điểm Giữa kỳ/Cuối kỳ.

## API

| API POST | Quyền | Chức năng |
| --- | --- | --- |
| `/api/admin/programming-assignments/save` | Admin hiện tại | Lưu/tạo bản nháp; validate bài toán bằng validator dùng chung với đề thi |
| `/api/admin/programming-assignments/assign` | Admin hiện tại | Giao bài cho `student_ids` thuộc khóa học |
| `/api/admin/programming-assignments/delete` | Admin hiện tại | Xóa bản nháp |
| `/api/student/programming/run` | Học viên được giao bài, đã mở bài, chưa hết hạn | Chạy `source`, `language`, `exam_id`, `problem_index`; `run_mode=samples` hoặc `custom` kèm `stdin` |

Start, submit, xem bài nộp/mã nguồn và rejudge sử dụng API programming có sẵn. Workspace quản trị thêm trường `programming_assignments`; workspace học viên trả ngữ cảnh bài tập đã giao trong `programming.exams` với `activity_type=assignment` để dùng lại editor và polling.

Chạy thử có tối đa 2 lượt đồng thời, dùng chung giới hạn tần suất theo học viên với luồng nộp bài. Mã nguồn và input tự nhập tối đa 100.000 byte. Không chạy code trực tiếp trên host; dùng Docker runner hiện có.

## Kiểm tra

- Kiểm thử backend trong `tests/test_learning.py`: ba test `test_programming_homework_*` xác nhận tạo/sửa/xóa bản nháp, giao bài, quyền, hạn nộp, test mẫu/input tự nhập, không ghi điểm khi chạy thử, nộp chống lặp, snapshot, lịch sử và tổng hợp điểm.
- `npm run test:programming-homework` kiểm tra luồng giao diện từ tạo/giao bài đến chạy thử/nộp/xem điểm ở Chrome headless, desktop và mobile, trên dữ liệu tạm. Fixture dùng bộ chấm giả lập, không xác nhận Docker thật.
- Để dùng thật cần Docker Desktop và image chấm sẵn sàng theo `docs/programming-judge.md`. Nếu Docker không sẵn sàng, API báo lỗi thay vì chạy mã trên host.
