# Câu hỏi → Đề thi → Kỳ thi

## Phân loại và ngân hàng

Trong **Phân loại & phân quyền → Ngân hàng câu hỏi**, tạo câu hỏi với:

- **Mục đích:** Luyện tập, Thực hành hoặc Thi.
- **Hình thức:** Code hoặc Nộp file.
- Chủ đề, độ khó và ngôn ngữ phân loại theo cơ chế hiện có.

Câu code có đề bài, điểm, ngôn ngữ, test mẫu/ẩn và giới hạn chạy. Câu nộp file có đề bài, điểm và định dạng bài làm; giảng viên chấm file theo luồng chấm hiện có. Tìm kiếm và bộ lọc giúp quản lý hai hình thức trong cùng ngân hàng.

Câu cũ chưa có mục đích mặc định hiển thị **Thi**, hình thức **Code**; không tự công khai câu cũ cho sinh viên. Có thể cập nhật mục đích trong phần phân loại nội dung. Câu đã công bố giữ nguyên đề/test; dùng **Tạo phiên bản mới** để sửa nội dung.

## Luyện tập

Chọn mục đích **Luyện tập**, lưu rồi **Công bố câu hỏi**. Sinh viên trong khóa học mở **Bài tập → Tự luyện tập**, tìm bài, chọn hình thức và tự mở làm, không cần được giao riêng.

Code dùng lại trình soạn thảo, chạy thử, nộp và chấm tự động. Nộp file dùng lại luồng tải bài, lịch sử và nhận xét của giảng viên. Kết quả luyện tập không tham gia điểm bài tập hay điểm kỳ thi của khóa học. Khi lưu trữ hoặc đổi mục đích câu hỏi, quyền tiếp cận tự luyện bị thu hồi; lịch sử nộp vẫn được lưu.

Chỉ câu luyện tập đã công bố trong lớp sinh viên tham gia mới xuất hiện. Câu thực hành/thi trong ngân hàng không được đưa vào danh sách tự luyện. Khóa học đã tổng kết không nhận bài mới.

## Bài thực hành

Trong khóa học, mở **Tài liệu & bài tập**:

- Tạo bài tập lập trình: chọn nhiều câu ngay trong form từ phần ngân hàng, hoặc kết hợp với bài toán nhập tay. Lưu nháp, đặt hạn nộp và giao cho danh sách sinh viên như trước.
- Bấm **Chọn câu nộp file từ ngân hàng**, chọn nhiều câu, đặt tên/hạn nộp rồi tạo và giao cho lớp. Yêu cầu các câu được ghép vào nội dung bài thực hành; sinh viên nộp file, giảng viên chấm và phản hồi.

Việc sao chép câu không thay đổi câu gốc. Hệ thống kiểm tra quyền trên câu nguồn và lớp đích. Các giới hạn số câu, độ dài nội dung, test và ngôn ngữ chạy vẫn áp dụng.

## Đề thi độc lập

Trong **Phân loại & phân quyền → Đề thi độc lập**, chọn **Tạo đề từ ngân hàng**, đặt tên, khóa học, hình thức và chọn nhiều câu. Lưu nháp rồi công bố đề.

Đề thi lưu danh sách câu cùng bản sao nội dung/cấu hình chấm tại thời điểm tạo; không chứa lịch thi hay danh sách sinh viên. Có thể sửa bản nháp, tạo bản sao hoặc lưu trữ. Đề đã công bố không sửa trực tiếp. Một đề được dùng cho nhiều kỳ thi; sửa câu gốc, lưu trữ đề gốc không làm thay đổi kỳ thi đã tạo.

## Tạo kỳ thi và phân phối

Mở **Cấu hình kỳ thi → Tạo kỳ thi**, chọn đề đã công bố trong trường **Chọn đề thi độc lập đã lưu**, hoặc tự chọn câu như trước. Đặt khóa học, loại kỳ thi, thời gian và danh sách dự thi.

Với code, chọn:

- **Cùng bộ câu cho cả lớp**.
- **Ngẫu nhiên bộ câu riêng cho từng sinh viên**, đặt số câu mỗi người. Tập câu được chọn từ các câu trong đề; hệ thống ưu tiên bộ khác nhau khi còn tổ hợp chưa dùng. Nếu số sinh viên vượt số tổ hợp, sẽ có bộ trùng nhau.

Bấm **Phân phối đề** để lưu cố định bộ câu cho từng sinh viên. Tải lại trang hoặc khởi động lại server không đổi bộ. Nếu thay đổi tập câu, cách giao hoặc số câu trước khi mở thi, cần phân phối lại. Thay đổi danh sách dự thi của đề ngẫu nhiên cũng yêu cầu phân phối lại; bộ của sinh viên cũ được giữ nếu cấu hình đề không đổi.

Sinh viên chỉ được đọc, chạy thử, xem lịch sử và nộp những câu trong bộ của mình. Backend kiểm tra chỉ số câu ở mọi API làm bài; không chỉ lọc trên giao diện. Các câu khác và toàn bộ bảng phân phối không xuất hiện trong dữ liệu sinh viên.

Với đề nộp file từ ngân hàng, hệ thống tạo file TXT chứa bộ câu. Giảng viên chọn danh sách MSSV và bấm **Phân phối đề** tại phần vận hành đề file. Có thể mở theo lịch, mở ngay hoặc kết thúc kỳ thi. Các chức năng phân phối ngẫu nhiên nhiều file sẵn có của Admin được giữ nguyên.

## Chấm và tương thích

Điểm code lấy điểm tốt nhất từng câu **được giao**, cộng và quy đổi thang 10 theo tổng điểm tối đa của bộ đó; câu không được giao không tính 0 và không làm giảm điểm. Bảng tổng hợp hiển thị dấu trống ở các câu không được giao. Điểm giữa kỳ/cuối kỳ dùng cùng quy tắc này khi cập nhật sổ điểm.

Chấm thật cần Docker/image bộ chấm sẵn sàng. File được giảng viên chấm theo luồng hiện có. Lịch sử và snapshot bài nộp được giữ để chấm lại đúng nội dung.

Dữ liệu đề thi độc lập nằm ở `exam_blueprints.json`. Trường mới trên câu hỏi là `purpose`, `response_type`; trên kỳ thi code là `blueprint_id`, `paper_distribution`, `questions_per_student`, `student_problem_sets`. Không bắt buộc chuyển đổi dữ liệu cũ; mặc định kỳ thi cũ tiếp tục giao cùng bộ câu như trước. Sao lưu metadata hiện có tự bao gồm kho đề mới.
