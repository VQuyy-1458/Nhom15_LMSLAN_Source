# Quy trình đề thi lập trình

Có thể tạo kỳ thi từ **đề thi độc lập đã công bố**, hoặc chọn câu trực tiếp như dưới đây. Cấu hình **Ngẫu nhiên bộ câu riêng cho từng sinh viên** để giao tập con cố định từ đề. Xem [hướng dẫn đầy đủ](cau-hoi-de-thi-ky-thi.md).

## Giáo viên / Admin

1. Mở **Cấu hình kỳ thi → Tạo kỳ thi → Thi lập trình**, chọn khóa học, tên và loại kỳ thi.
2. Chọn nhiều câu hỏi từ ngân hàng. Tìm theo tên/chủ đề hoặc lọc độ khó. Bấm **Tạo và mở thiết lập**; đề và test được sao chép độc lập.
3. Kiểm tra đề, điểm mỗi câu, ngôn ngữ, test mẫu/ẩn. Có thể thêm bài toán thủ công hoặc thêm câu hỏi từ ngân hàng. Các câu đã có được tích và khóa để tránh thêm trùng.
4. Đặt thời lượng và tùy chọn giờ bắt đầu theo giờ Việt Nam (UTC+7). Lưu thiết lập. Thời gian tính chung cho phòng thi; vào muộn không được cấp lại toàn bộ thời lượng.
5. Trong **Đối tượng được vào thi**, chọn sinh viên trong lớp, bấm **Lưu danh sách dự thi**.
6. Bấm **Phân phối đề**. Kỳ thi mới tạo qua giao diện ở chế độ phân phối thủ công, chưa hiển thị cho sinh viên trước bước này. Phân phối không yêu cầu Docker; câu hỏi vẫn được giữ kín.
7. Có giờ bắt đầu: kỳ thi tự mở khi đến giờ nếu cấu hình hợp lệ. Không có lịch: dùng **Lưu và mở ngay**, kiểm tra rồi xác nhận mở thi. Docker và image bộ chấm cần sẵn sàng để nhận và chấm code.
8. Theo dõi **Kết quả theo sinh viên** và lịch sử nộp trong **Vận hành & chấm thi lập trình**. Có thể chấm lại khi cần; hệ thống giữ lịch sử chấm.

Kỳ thi cũ giữ cơ chế mở theo lịch hiện có. Chế độ phân phối thủ công được ghi trên kỳ thi mới tạo qua giao diện (`distribution_mode=manual`), tránh làm mất lịch đang sử dụng.

## Sinh viên

Vào **Kỳ thi**, chọn đề đã được phân phối. Trước giờ bắt đầu chỉ thấy thông tin phòng thi. Khi được mở, bấm **Vào làm bài**, chọn câu hỏi và ngôn ngữ, viết code hoặc tải file mã nguồn, chạy thử rồi nộp bài. Có thể nộp nhiều lần trong thời gian còn lại. Bấm kết thúc bài làm để khóa nộp sớm; hết thời gian hệ thống ngừng nhận bài.

Chạy thử không lưu điểm; nộp bài sẽ chấm toàn bộ test mẫu và test ẩn. Sinh viên chỉ thấy dữ liệu test mẫu, kết quả test ẩn được giữ kín.

## Điểm và kiểm tra quyền

Điểm một lần nộp bằng điểm tối đa của câu nhân tỷ lệ test đạt. Tổng điểm là tổng điểm tốt nhất từng câu, quy đổi thang 10 theo tổng điểm tối đa của đề. Bảng tổng hợp thể hiện bài đang chấm và lỗi bộ chấm; điểm còn tạm tính nếu chưa chấm xong. Quy tắc đưa điểm vào sổ điểm theo loại kỳ thi (Test/Giữa kỳ/Cuối kỳ) giữ cơ chế hiện có.

Backend kiểm tra quyền quản lý đề, khóa học và danh sách sinh viên. Học viên ngoài danh sách không vào thi/nộp bài; giáo viên không được phân phối hoặc xem kết quả đề của giáo viên khác. Đề đã mở khóa cấu hình câu hỏi để giữ nguyên dữ liệu chấm.

API phân phối: `POST /api/admin/programming/control`, `action=publish`, `exam_id`. API tổng hợp kết quả dùng `GET /api/admin/programming/submissions?exam=...`, trả thêm `problems` và `results` bên cạnh lịch sử `submissions`.
