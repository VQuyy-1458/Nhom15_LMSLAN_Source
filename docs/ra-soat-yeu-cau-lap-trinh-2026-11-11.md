# Rà soát code hiện tại theo yêu cầu mới

Ngày rà soát: 11/11/2026. Phạm vi: mã nguồn hiện có trong workspace, giao diện, API, lưu trữ và các kiểm thử liên quan. Không triển khai chức năng mới trong bước này. Workspace không có thư mục `.git`, nên báo cáo phản ánh trạng thái file hiện tại, không xác nhận lịch sử hoặc tính đầy đủ của từng commit merge.

## Kết luận

Hệ thống đã có một luồng thi lập trình tương đối đầy đủ và có thể tái sử dụng. Phần còn thiếu tập trung ở bài tập lập trình độc lập với kỳ thi, chạy thử cho học viên, ngân hàng câu hỏi, phân loại câu hỏi và vai trò Giáo viên riêng.

Không nên viết lại bộ chấm, trình soạn code, hàng đợi nộp bài, lịch sử hoặc bộ tổng hợp điểm. Cần mở rộng mô hình nội dung và phân quyền để những phần đó phục vụ thêm bài tập và ngân hàng câu hỏi.

## 1. Quản lý bài tập lập trình

| Yêu cầu | Hiện trạng | Code có thể dùng lại / phần còn thiếu |
| --- | --- | --- |
| Tạo, sửa bài lập trình | Có trong cấu hình kỳ thi | `app/exam_catalog.py:107`, `static/js/admin-exams.js:26`. Bài toán nằm trong `programming.problems` của từng kỳ thi. |
| Xóa bài lập trình | Có thể bỏ bài toán khỏi đề nháp rồi lưu | Giao diện có `data-problem-remove`. Chưa có thực thể bài tập độc lập hoặc API xóa bài tập lập trình độc lập; chưa có chính sách xóa/lưu trữ khi đã phát sinh bài nộp. |
| Cấu hình ngôn ngữ | Có C, C++, Java, Python | `app/exam_catalog.py`, `app/code_runner.py:18`. Danh sách ngôn ngữ được đặt ở cấp kỳ thi, chưa phải metadata riêng cho từng câu hỏi. |
| Quản lý test case | Có | Input/output, test mẫu/test ẩn, kiểm tra giới hạn, thêm/xóa test trên giao diện; nhập CSV qua `static/js/exam-test-csv.js`. |
| Giao bài cho học viên | Có thông qua kỳ thi và danh sách dự thi | `prepare_programming_participants`, `save_programming_participants`, `programming.eligible`. Chưa có quy trình giao bài lập trình độc lập theo hạn nộp của bài tập. |
| Viết code trên web | Có | `static/js/programming-student.js:46`: editor, chọn ngôn ngữ, template, tải file vào editor, nháp local theo sinh viên/bài/ngôn ngữ. |
| Chạy thử trước khi nộp | Chưa thấy luồng riêng cho học viên | Editor hiện có Submit; backend học viên có start/finish/submit/submissions. `exam_preflight.verify_reference` là chấm thử lời giải của người quản lý, không phải chức năng chạy thử cho học viên. |
| Nộp và tự chấm | Có trong kỳ thi | `app/programming.py:173`, `app/code_runner.py:142`; kiểm tra quyền, thời hạn, ngôn ngữ, dung lượng, hàng đợi và chống gửi lặp. |
| Lưu điểm và lịch sử | Có | Lưu mã nguồn, kết quả từng test, lịch sử chấm lại; archive và tổng hợp điểm. |

Phân biệt hai loại dữ liệu hiện có: `learning.json.assignments` là bài tập nộp file, hỗ trợ đính kèm đề và chấm thủ công; gửi file `.py`/`.cpp` vào đó không biến nó thành bài tập tự chấm. Luồng tự chấm hiện thuộc `exam_catalog.json` và `programming_submissions.json`.

## 2. Phân loại và phân quyền

| Yêu cầu | Hiện trạng | Phần cần bổ sung |
| --- | --- | --- |
| Phân loại theo chủ đề | Bài tập/tài liệu học tập có `topic` | Bài toán lập trình trong `exam_catalog.save` chưa lưu trường chủ đề. Không nên coi `topic` của tài liệu là đã đáp ứng phân loại câu hỏi lập trình. |
| Phân loại theo độ khó | Chưa thấy | Chưa có trường độ khó được validate/lưu và bộ lọc tương ứng cho bài toán. |
| Phân loại theo ngôn ngữ | Có cấu hình ngôn ngữ thi | Còn thiếu metadata và bộ lọc ở cấp bài tập/câu hỏi độc lập. |
| Admin/Giáo viên/Học viên | Hiện chỉ có `admin` và `student` | `app/main.py:531`, `app/security.py:79`. Tên đăng nhập `teacher` trong test vẫn sử dụng role `admin`; nhãn “giảng viên” trên UI không tạo thêm role. |
| Quyền tạo/sửa/xem/nộp ở backend | Có cho hai role hiện tại | Route quản lý yêu cầu `admin`; route sinh viên yêu cầu `student`; kiểm tra danh sách dự thi, thành viên khóa học, thời hạn và quyền xem mã nguồn. |
| Quyền Giáo viên theo tài nguyên | Chưa có mô hình riêng | Cần quyền sở hữu/phụ trách lớp, bài tập, câu hỏi, đề thi; kiểm tra tại backend cho cả đọc, ghi và tái sử dụng. Chưa có metadata chủ sở hữu giáo viên cho các thực thể mới này. |
| Quyền xóa | Chưa thể hoàn thành theo yêu cầu mới | Chưa có CRUD độc lập cho câu hỏi/bài tập lập trình để áp dụng quyền xóa và chính sách xử lý tham chiếu/lịch sử. |

Các vị trí phải xét khi bổ sung role: đăng nhập và session trong `main.py`/`security.py`; `_auth(req, "admin")` tại các route; điều kiện `session["role"] == "admin"` trong các module nghiệp vụ; quyền xem source, archive, báo cáo và test ẩn. Không chỉ thêm lựa chọn Giáo viên ở giao diện hoặc đổi tất cả kiểm tra admin thành “admin hoặc teacher”.

## 3. Ngân hàng câu hỏi

Chưa tìm thấy module, kho dữ liệu, API và màn hình ngân hàng câu hỏi lập trình độc lập trong code hiện tại.

Những phần đã có nhưng mới ở cấp đề thi:

- Tạo/sửa/xóa bài toán và test case trong bản nháp của một đề.
- Mô tả bài, điểm tối đa, time limit, memory limit, checker `exact`/`tokens`.
- Test mẫu và test ẩn, nhập test bằng CSV.

Những phần còn thiếu:

- ID câu hỏi ổn định, CRUD riêng, chủ đề, độ khó, ngôn ngữ, chủ sở hữu và phạm vi chia sẻ.
- Tìm kiếm/lọc ngân hàng và chọn câu hỏi để tái sử dụng trong nhiều bài tập/đề thi.
- Quy tắc phiên bản: sửa câu hỏi gốc có tác động gì tới đề nháp, đề đã phát và bài đã nộp.
- Quy tắc xóa/lưu trữ câu hỏi đang được tham chiếu.

Nên tách logic validate bài toán/test case từ `exam_catalog.save` để ngân hàng và cấu hình đề dùng chung. Hiện hàm này chỉ lưu các trường đã chọn vào `cleaned`, nên gửi thêm `topic`, `difficulty` hoặc ID câu hỏi từ UI sẽ chưa được lưu nếu backend không được mở rộng.

## 4. Tạo đề thi và phân phối đề

| Yêu cầu | Hiện trạng | Khoảng thiếu |
| --- | --- | --- |
| Tạo đề thủ công | Có | Hiện nhập từng bài trực tiếp vào kỳ thi; chưa chọn từ ngân hàng. |
| Tạo đề ngẫu nhiên từ ngân hàng | Chưa có | Cần bộ tiêu chí chọn câu theo chủ đề/độ khó/ngôn ngữ, số lượng, điểm và xử lý khi nguồn câu hỏi không đủ. |
| Thiết lập thời gian, điểm | Có | Thời gian bắt đầu, thời lượng, thời gian kết thúc, điểm từng bài; cấu hình điều chỉnh giờ thi trong `app/exam_timing.py`. |
| Giao đề cho học viên | Có | Danh sách dự thi, kiểm tra thành viên lớp, tự mở theo lịch hoặc mở thủ công, chặn truy cập trước giờ. |
| Học viên làm bài, nộp code | Có | Editor và start/submit/finish, xem kết quả/lịch sử riêng. |
| Chấm và tổng hợp kết quả | Có | Bộ chấm, kết quả từng bài; `app/course_grades.py:11` tổng hợp điểm thi lập trình theo điểm tốt nhất mỗi bài và quy về thang 10. |

`app/exams.py:58` có phân phối **file đề có sẵn** theo các chế độ random/selected/parity/custom. Việc này không phải sinh đề lập trình ngẫu nhiên từ ngân hàng câu hỏi. Hiện sinh viên trong một kỳ thi lập trình dùng cấu hình `programming.problems` của kỳ thi đó; chưa thấy cơ chế bốc câu độc lập theo từng sinh viên.

## 5. Các khối cần giữ và mở rộng

| Khối | Vị trí | Hướng tái sử dụng |
| --- | --- | --- |
| Bộ biên dịch/chấm trong Docker | `app/code_runner.py` | Dùng chung cho bài tập, thi và chạy thử; giữ giới hạn tài nguyên, không mạng, container hạn chế quyền. |
| Nộp bài và hàng đợi | `app/programming.py`, `app/submission_rate.py` | Giữ chống gửi lặp, giới hạn hàng đợi/tần suất; mở rộng ngữ cảnh ngoài `exam_id` sau khi chốt mô hình bài tập. |
| Bảo toàn dữ liệu chấm | `programming.submit`, `_work`, `rejudge` | Giữ snapshot mã nguồn, `problem.json`, image chấm và lịch sử, không chấm lại bằng câu hỏi gốc đã bị sửa. |
| Editor, nháp, lịch sử trực tiếp | `static/js/programming-student.js`, `static/js/programming.js` | Tách phần phụ thuộc kỳ thi để phục vụ bài tập độc lập; không viết editor mới. |
| Soạn bài và nhập test | `static/js/admin-exams.js`, `static/js/exam-test-csv.js` | Tái sử dụng editor câu hỏi và parser CSV cho ngân hàng. |
| Lịch thi và kiểm tra trước khi mở | `app/exam_schedule.py`, `app/exam_timing.py`, `app/exam_preflight.py` | Giữ luồng thời gian và kiểm tra cấu hình; không dùng API chấm thử của admin làm API chạy thử cho học viên. |
| Tổng hợp điểm/xuất kết quả | `app/course_grades.py`, `app/submission_archive.py` | Giữ quy tắc hiện có, bổ sung quy tắc điểm bài tập lập trình sau khi được xác định. |
| Session, kiểm tra quyền, transaction, audit | `app/security.py`, `app/storage.py`, `app/main.py` | Mở rộng thay vì tạo luồng xác thực/lưu dữ liệu thứ hai. |

## 6. Thứ tự đề xuất cho bước thiết kế tiếp theo

1. Chốt ma trận quyền ba vai trò, phạm vi Giáo viên phụ trách và quy tắc dùng chung câu hỏi. Chốt cách phân biệt bài tập lập trình với kỳ thi và bài tập nộp file hiện có.
2. Thiết kế câu hỏi độc lập cùng metadata và phiên bản/snapshot; tách validator dùng chung từ cấu hình kỳ thi.
3. Bổ sung CRUD/tìm kiếm/lọc ngân hàng và quyền backend; mở rộng editor hiện có.
4. Bổ sung bài tập lập trình độc lập và giao bài, dùng lại editor/nộp/chấm/lịch sử hiện có.
5. Bổ sung API chạy thử riêng, kiểm tra quyền và giới hạn tài nguyên/tần suất; phân biệt kết quả chạy thử với lần nộp tính điểm.
6. Cho chọn thủ công hoặc sinh ngẫu nhiên từ ngân hàng vào đề; lưu lựa chọn/snapshot để lượt thi không đổi khi ngân hàng thay đổi.

Đây là thứ tự đề xuất để tránh phải sửa mô hình dữ liệu nhiều lần, chưa phải các thay đổi đã được triển khai.

## 7. Kiểm chứng đã thực hiện

Đã chạy 12 kiểm thử tích hợp, tất cả thành công, sử dụng storage tạm trong `tests/test_learning.py`:

- `test_programming_lifecycle_privacy_deadline_and_rejudge_snapshot`
- `test_programming_roster_persists_and_restricts_every_student_entry`
- `test_programming_roster_account_creation_is_atomic_and_per_exam`
- `test_programming_roster_validates_course_lock_and_current_membership`
- `test_exam_catalog_types_persistence_and_access`
- `test_student_cannot_create_content_or_grade`
- `test_assessment_types_and_one_final_across_file_and_code`
- `test_scheduled_code_blocks_early_entry_then_uses_planned_common_clock`
- `test_preflight_reference_optional_and_never_counts_as_student_work`
- `test_preflight_judge_runs_outside_learning_lock_and_limits_concurrency`
- `test_student_can_finish_programming_exam_early`
- `test_programming_original_bom_and_rate_header`

Đã chạy thành công `node tests/test_exam_csv.cjs` và `node tests/test_resource_weeks.cjs`, kiểm tra parser CSV và bộ phân tuần/danh sách sau merge.

Giới hạn: chưa chạy toàn bộ suite, chưa kiểm thử trình duyệt trong đợt rà soát này và chưa chạy biên dịch/chấm thật bằng Docker. Các bài kiểm thử vòng đời sử dụng mock bộ chấm; kết quả pass không chứng minh Docker/image hiện tại đã sẵn sàng. Traceback `OSError: roster write failure` trong log kiểm thử là lỗi được chủ động giả lập để kiểm tra rollback, không phải test thất bại.

Không sửa code chức năng hoặc dữ liệu lớp học trong bước rà soát; chỉ thêm báo cáo này.
