# Ngân hàng câu hỏi lập trình

Ngân hàng hiện hỗ trợ cả **Code / Nộp file**, mục đích **Luyện tập / Thực hành / Thi**, đề thi độc lập và bộ câu code theo từng sinh viên. Hướng dẫn đầy đủ: [Câu hỏi → Đề thi → Kỳ thi](cau-hoi-de-thi-ky-thi.md).

Mở **Phân loại & phân quyền → Ngân hàng câu hỏi** bằng tài khoản Admin hoặc Giáo viên.

## Chọn câu hỏi ngay khi tạo kỳ thi

Mở **Cấu hình kỳ thi → Tạo kỳ thi**, chọn **Thi lập trình** và khóa học. Trong phần **Chọn câu hỏi từ ngân hàng**, tìm theo tên/chủ đề, lọc độ khó và tích nhiều câu hỏi. Bấm **Tạo và mở thiết lập** để lưu tất cả câu hỏi đã chọn cùng kỳ thi trong một lần. Không cần tạo đề trước rồi thêm từng câu từ trang ngân hàng.

Ngôn ngữ thi ban đầu lấy phần chung của các câu hỏi được chọn. Hệ thống từ chối nếu không có ngôn ngữ chung hoặc vượt 30 câu. Trang thiết lập cho phép kiểm tra/sửa đề, điểm, test case, ngôn ngữ và danh sách dự thi trước khi mở thi. Câu hỏi gốc không bị thay đổi.

Sau khi lưu đề và danh sách dự thi, bấm **Phân phối đề** để sinh viên thấy phòng thi. Xem [quy trình đề thi lập trình](de-thi-lap-trinh.md) để cấu hình thời gian, mở thi và theo dõi kết quả.

API `POST /api/admin/exam-configurations/save` nhận thêm `question_ids` là mảng JSON các mã câu hỏi. Backend kiểm tra quyền từng câu, trạng thái lưu trữ và ngôn ngữ; sao chép dữ liệu hiện tại của ngân hàng, không tin đề/test do client tự khai thay cho các mã đã chọn. Thao tác lưu toàn bộ kỳ thi là một giao dịch.

## Quản lý và tái sử dụng từ ngân hàng

1. Bấm **Tạo câu hỏi lập trình**, chọn khóa học, chủ đề, độ khó và ngôn ngữ.
2. Thêm đúng một bài toán: tên, đề bài, điểm, giới hạn thời gian, bộ nhớ và cách so khớp kết quả.
3. Thêm test case với input/output; đánh dấu test mẫu để phân biệt với test ẩn. Cần ít nhất một test case.
4. Lưu câu hỏi. Bản nháp được sửa; câu hỏi đã công bố cần tạo phiên bản mới để sửa đề/test. Lưu trữ sẽ bỏ câu hỏi khỏi ngân hàng đang sử dụng.
5. Tìm theo tên, mã, nội dung hoặc tên chủ đề; kết hợp bộ lọc chủ đề, độ khó và ngôn ngữ.
6. Bấm **Tái sử dụng / Tạo phiên bản**: tạo bài tập lập trình, đề thi lập trình hoặc phiên bản câu hỏi mới. Có thể chọn bản nháp bài tập/đề thi có sẵn để thêm câu hỏi; chọn đúng loại và khóa học tương ứng.

Bài tập mới cần hạn nộp trong tương lai; đề thi mới có thời lượng từ 1 đến 1440 phút. Khi thêm vào bản nháp, các ngôn ngữ được phép chạy lấy phần chung; hệ thống từ chối nếu không tương thích. Chủ đề ngừng sử dụng được giữ ở câu hỏi gốc nhưng không gán cho bản mới.

Nội dung được sao chép độc lập, gồm đề bài, điểm, test mẫu/ẩn và giới hạn chạy. Sửa hoặc lưu trữ câu hỏi gốc không thay đổi nội dung đã sao chép. Bài tập và đề thi mới ở trạng thái nháp; mở **Khóa học** hoặc **Cấu hình kỳ thi** để kiểm tra, chỉnh sửa và giao/mở thi.

Backend kiểm tra quyền trên câu hỏi nguồn và khóa học đích. Giáo viên chỉ tái sử dụng câu hỏi mình quản lý vào lớp được phân công; nội dung đích có sẵn cũng phải thuộc quyền quản lý. Không được thêm câu hỏi vào bài đã giao hoặc đề thi đã mở. Học viên không truy cập ngân hàng hoặc test ẩn.

API bổ sung: `POST /api/admin/questions/reuse`, với `id`, `target_type` (`question`, `assignment`, `exam`), `course_id`; tùy chọn `target_id` để thêm vào bản nháp có sẵn. Tạo bài tập cần `due_at`; tạo đề thi có thể truyền `duration_minutes`. API dùng cùng bộ kiểm tra cấu hình và cơ chế lưu giao dịch hiện có.
