# Phân loại và phân quyền LMS-LAN

## Khởi động và thiết lập

Khởi động lại server sau khi cập nhật backend, rồi tải lại trang bằng Ctrl+F5. Không cần chuyển đổi dữ liệu lớp học cũ.

Admin mở **Phân loại & phân quyền** trên sidebar:

1. Tạo các chủ đề dùng chung. Có thể đổi tên hoặc ngừng sử dụng; không xóa mất tham chiếu lịch sử.
2. Tạo tài khoản Giáo viên, nhập mật khẩu từ 8 đến 200 ký tự.
3. Tích checkbox trước tên giáo viên trong từng khóa học rồi bấm **Lưu phân công**. Kiểm tra dòng **Đang phụ trách** sau khi lưu. Có thể phân công nhiều giáo viên; bỏ chọn tất cả và xác nhận để thu hồi quyền lớp. Các lựa chọn chưa lưu ở khóa học khác được giữ khi lưu một khóa học.
4. Giáo viên đăng nhập bằng tài khoản mới, mở **Khóa học** để tạo nội dung trong lớp phụ trách.
5. Gán nhiều chủ đề, một mức độ khó chính (Dễ/Trung bình/Khó) và ngôn ngữ khi soạn bài lập trình/đề thi. Ngôn ngữ phân loại phải thuộc các ngôn ngữ được phép chạy của nội dung.
6. Trong trang **Phân loại & phân quyền**, người quản lý có thể cập nhật phân loại của nội dung thuộc quyền quản lý, hoặc tạo/sửa/công bố/lưu trữ câu hỏi lập trình. Câu hỏi cần một bài toán có test case; việc công bố trong ngân hàng không tự giao câu hỏi cho học viên.

Bài tập và đề thi có bộ lọc chủ đề, độ khó, ngôn ngữ, loại nội dung, dùng cùng bộ lọc tuần và bộ lọc danh sách hiện có. Các mục chưa gán chủ đề không bị suy đoán chủ đề từ ngày đăng/hạn nộp.

Ngân hàng câu hỏi có tìm kiếm theo tên/mã/nội dung/chủ đề, xem test mẫu và test ẩn, tạo phiên bản mới và tái sử dụng vào bài tập/đề thi nháp. Xem [hướng dẫn ngân hàng câu hỏi](ngan-hang-cau-hoi.md).

## Quyền

Admin và Giáo viên dùng chung **Không gian quản lý**, cùng nhóm menu Dashboard, Khóa học, Lịch giảng dạy, Thông báo lớp học, Cấu hình kỳ thi, Bài nộp và Phân loại & phân quyền. Giáo viên đăng nhập vào Dashboard; số liệu và lịch chỉ hiển thị trong phạm vi được phân công. Trang Thông báo lớp học cho phép đăng và xem thông báo trong lớp phụ trách. Admin có thêm nhóm Quản trị hệ thống. Vai trò thật và phạm vi dữ liệu vẫn được giữ; không chuyển tài khoản Giáo viên thành Admin. Nút logo của cả hai vai trò mở trang Khóa học.

| Chức năng | Admin | Giáo viên | Học viên |
| --- | --- | --- | --- |
| Quản lý danh mục, giáo viên, phân công lớp | Toàn hệ thống | Không | Không |
| Tạo nội dung | Toàn hệ thống | Trong lớp được phân công | Không |
| Xem/sửa/xóa nháp, phân loại, công bố/giao bài | Toàn hệ thống | Phải vừa là người tạo vừa được phân công lớp | Không |
| Xem cấu hình/test ẩn | Toàn hệ thống | Chỉ nội dung thuộc quyền quản lý | Không |
| Xem/nộp bài, chạy thử | Không dùng tài khoản học viên | Không dùng tài khoản học viên | Chỉ lớp tham gia, nội dung được công bố/giao cho mình, trong hạn |
| Xem kết quả, tải bài nộp, chấm lại, xuất CSV/ZIP | Toàn hệ thống | Chỉ bài nộp của nội dung thuộc quyền quản lý | Chỉ kết quả và mã nguồn của mình |

Các quy tắc được kiểm tra ở backend; ẩn nút trên UI chỉ giúp người dùng thao tác đúng. Giáo viên không được dùng API quản trị tài khoản, cấu hình server, phân phối file đề toàn hệ thống hoặc tạo tài khoản học viên qua danh sách dự thi.

Thu hồi phân công lớp có hiệu lực ở yêu cầu tiếp theo, kể cả khi tab cũ còn mở. Khóa tài khoản hoặc đổi mật khẩu Giáo viên thu hồi các session của giáo viên đó. Nội dung cũ thiếu `created_by` tiếp tục do Admin quản lý, không tự chuyển quyền cho giáo viên được phân công lớp.

Bài tập đã giao và đề thi đã mở vẫn giữ nguyên cơ chế khóa đề/test và snapshot khi nộp. Xóa bản nháp hoặc lưu trữ câu hỏi không xóa điểm, mã nguồn hoặc lịch sử chấm đã có. Nội dung nộp file/học liệu cũ giữ hành vi công bố hiện tại để tương thích dữ liệu cũ.

## Lưu trữ và mô-đun

- `teachers.json`: tài khoản Giáo viên riêng, mật khẩu hash theo cơ chế hiện có.
- `topics.json`: danh mục chủ đề dùng chung, cờ `active` để ngừng sử dụng.
- `questions.json`: câu hỏi lập trình có chủ sở hữu, khóa học, cấu hình bài/test, trạng thái công bố/lưu trữ và phân loại.
- `learning.json.courses[].teacher_ids`: các giáo viên phụ trách; mặc định rỗng khi chưa phân công.
- `created_by` của nội dung được lấy từ session, không lấy từ dữ liệu client gửi lên.
- `topic_ids`, `difficulty`, `classification_languages`, `content_type`: metadata phân loại của bài lập trình, câu hỏi và đề thi. Loại nội dung được xác định theo tài nguyên backend.
- `app/permissions.py`: kiểm tra vai trò + khóa học + chủ sở hữu, danh sách API Giáo viên được phép dùng theo nguyên tắc mặc định từ chối.
- `app/classification.py`: danh mục, quản lý Giáo viên, phân công, kiểm tra metadata và câu hỏi.

Các file dữ liệu mới được tạo khi có thao tác lưu đầu tiên, không cần tài khoản hoặc mật khẩu mặc định.

## API quản lý

| API | Quyền |
| --- | --- |
| `GET /api/admin/classification` | Admin: toàn bộ; Giáo viên: danh mục chung, lớp và nội dung thuộc quyền quản lý |
| `POST /api/admin/topics/save`, `/topics/archive` | Admin |
| `POST /api/admin/teachers/save` | Admin |
| `POST /api/admin/courses/teachers` | Admin |
| `POST /api/admin/classification/assign` | Admin hoặc Giáo viên có quyền trên nội dung |
| `POST /api/admin/questions/save`, `/questions/publish`, `/questions/archive` | Admin hoặc Giáo viên có quyền trên câu hỏi/lớp |

API bài tập, đề thi, preflight, thời gian thi, roster, chấm lại, tải mã nguồn và archive hiện có đã được nối với cùng lớp kiểm tra quyền. Archive lọc quyền trước khi phân trang, tổng hợp danh sách hoạt động hoặc xuất file.

## Kiểm thử

- Các test `test_teacher_*` và `test_taxonomy_*` trong `tests/test_learning.py` kiểm tra đăng nhập Giáo viên, phạm vi lớp, chủ sở hữu, thu hồi quyền, danh mục ngừng sử dụng, draft/publication, file/source/preview, archive/export và chấm lại.
- `node tests/test_classification.cjs`: bộ lọc theo nhiều tiêu chí, danh mục cũ, ngôn ngữ cấu hình và escape nội dung.
- `npm run test:classification`: Chrome headless, dữ liệu tạm, xác nhận luồng Admin tạo danh mục/Giáo viên và phân công; Giáo viên đăng nhập, tạo/phân loại/giao bài, soạn câu hỏi; các API Admin bị từ chối; desktop/mobile.
- `npm test`: bộ kiểm thử hồi quy hiện có cùng các test mới. Các test cần Docker thật vẫn phụ thuộc môi trường Docker của máy.
