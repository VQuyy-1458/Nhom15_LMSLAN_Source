# Tổng hợp các hạng mục đã triển khai và cập nhật LMS-LAN

Ngày tổng hợp: 11/11/2026.

## 1. Tổ chức khóa học, lịch học và điểm danh

- Đưa phần buổi học định kỳ vào khu vực **Lịch & điểm danh**.
- Tổ chức luồng tạo lịch theo hoạt động, giảm các phần tạo lịch trùng nhau.
- Chuyển form tạo buổi học thành thao tác mở bằng nút; hỗ trợ tạo nhiều buổi theo lịch đến hết kỳ.
- Đưa hoạt động đã tạo ra danh sách lịch của khóa học.
- Giữ liên kết buổi học với nội dung bài học, bài đọc, tài liệu và bài tập tương ứng.
- Bổ sung giờ kết thúc trong cấu hình buổi học, lưu dữ liệu và hiển thị trong danh sách.
- Sau khi dữ liệu buổi học cũ được cập nhật giờ kết thúc, bỏ các ô nhập bổ sung giờ kết thúc riêng cho từng buổi cũ.
- Đánh dấu các buổi học thuộc tuần hiện tại trong danh sách lịch.

## 2. Học theo tuần và tổng quan khóa học

- Bổ sung phần hiển thị tuần học trong tổng quan khóa học.
- Tập hợp nội dung bài học, bài đọc, tài liệu và bài tập theo buổi học/tuần học.
- Bổ sung nơi xem thông báo liên quan đến khóa học và tiến độ học tập.
- Bổ sung bộ lọc tuần cho trang học theo tuần của sinh viên.
- Xác định tuần theo nhãn tuần rõ ràng trong `topic` hoặc liên kết buổi học có trong dữ liệu.
- Nội dung chưa xác định được tuần nằm trong nhóm **Chưa gắn tuần**; không suy đoán tuần từ ngày đăng hoặc hạn nộp.

## 3. Giao diện tài liệu và bài tập

- Chuyển tài liệu và bài tập từ các thẻ lớn sang danh sách mỗi nội dung một dòng.
- Bấm vào dòng để mở rộng/thu gọn mô tả và các thao tác.
- Kết hợp bộ lọc tuần với nhóm **Chưa gắn tuần**.
- Giữ chức năng xem file, tải tài liệu, xem yêu cầu, nộp bài, xem kết quả và chấm điểm.
- Gộp bài tập lập trình đã giao và bài tập nộp file vào danh sách bài tập chung của khóa học ở cả phía quản lý và sinh viên.
- Tách bản nháp lập trình khỏi danh sách bài tập chính thức; bài đã giao xuất hiện trong danh sách chính thức.

## 4. Bài tập lập trình trong khóa học

Luồng đã có: **Tạo bài tập → Giao bài → Viết code → Chạy thử → Nộp bài → Chấm điểm → Lưu kết quả**.

- Tạo, chỉnh sửa và xóa bản nháp bài tập lập trình độc lập với kỳ thi.
- Cấu hình đề bài, ngôn ngữ, điểm, giới hạn thời gian/bộ nhớ và cách so khớp kết quả.
- Quản lý test mẫu và test ẩn cho từng bài toán.
- Đặt hạn nộp và giao bài cho danh sách sinh viên trong khóa học.
- Sinh viên viết code trên giao diện hoặc tải file mã nguồn.
- Chạy thử bằng test mẫu hoặc input tự nhập; chạy thử không ghi điểm hoặc tạo lần nộp chính thức.
- Nộp bài để chấm toàn bộ test, hiển thị trạng thái chờ chấm, biên dịch, chấm và kết quả.
- Lưu mã nguồn, kết quả, điểm và lịch sử nộp/chấm lại.
- Giữ kín dữ liệu test ẩn với sinh viên.
- Khóa đề và test sau khi giao để bảo toàn dữ liệu chấm.
- Kiểm tra hạn nộp, trạng thái khóa học và đối tượng được giao bài ở backend.

## 5. Phân loại nội dung và quản lý danh mục

- Quản lý danh mục chủ đề dùng chung toàn hệ thống.
- Admin tạo, đổi tên và ngừng sử dụng chủ đề; giữ tham chiếu lịch sử.
- Gán nhiều chủ đề cho một nội dung và một mức độ khó chính: **Dễ / Trung bình / Khó**.
- Phân loại theo ngôn ngữ lập trình và loại nội dung.
- Bổ sung phân loại câu hỏi theo mục đích: **Luyện tập / Thực hành / Thi**.
- Bổ sung phân loại câu hỏi theo hình thức: **Code / Nộp file**.
- Tìm kiếm và lọc nội dung theo các tiêu chí phân loại.
- Giữ dữ liệu câu hỏi cũ ở mặc định **Thi / Code**, không tự công khai thành bài luyện tập.

## 6. Tài khoản, phân quyền và giao diện giảng viên

- Duy trì ba vai trò: **Admin / Giảng viên / Sinh viên**.
- Admin và Giảng viên dùng chung giao diện quản lý; phạm vi quyền vẫn khác nhau.
- Tạo/cập nhật tài khoản giảng viên, khóa tài khoản và phân công khóa học.
- Chuyển giao diện phân công giảng viên sang checkbox, hiển thị danh sách đã lưu và giữ lựa chọn chưa lưu ở khóa học khác.
- Giảng viên quản lý nội dung do mình tạo trong lớp được phân công.
- Sinh viên chỉ tiếp cận nội dung được công bố/giao trong lớp mình tham gia.
- Kiểm tra quyền ở backend cho các thao tác tạo, xem, sửa, xóa, phân loại, công bố, giao bài, nộp bài, xem kết quả, tải mã nguồn và chấm lại.
- Giới hạn các chức năng quản trị tài khoản, cấu hình server và quản trị hệ thống cho Admin.
- Bổ sung **Dashboard**, **Lịch giảng dạy** và **Thông báo lớp học** cho giảng viên.
- Dashboard và lịch của giảng viên lấy dữ liệu theo phạm vi được phân công.
- Hỗ trợ giảng viên đăng thông báo cho lớp phụ trách.

## 7. Ngân hàng câu hỏi độc lập

Luồng đã có: **Tạo câu hỏi → Thêm cấu hình/test → Phân loại → Lưu ngân hàng → Tìm kiếm và tái sử dụng**.

- Quản lý câu hỏi riêng, không bắt buộc tạo kỳ thi trước.
- Câu hỏi code lưu đề bài, điểm, ngôn ngữ, test mẫu/ẩn và giới hạn chấm.
- Câu hỏi nộp file lưu đề bài, điểm và định dạng bài làm được chấp nhận.
- Tạo và chỉnh sửa bản nháp, công bố, lưu trữ và tạo phiên bản câu hỏi mới.
- Xem lại đề bài, phân loại và test case trong ngân hàng dành cho người quản lý.
- Tìm theo tên, mã, nội dung hoặc chủ đề; kết hợp lọc độ khó, ngôn ngữ, mục đích và hình thức.
- Tái sử dụng câu hỏi vào bài tập hoặc đề thi; sao chép nội dung độc lập với câu gốc.
- Kiểm tra quyền với câu hỏi nguồn và khóa học/nội dung đích.
- Bổ sung bộ dữ liệu mẫu gồm **8 câu hỏi lập trình, 45 test case**, thuộc khóa **Lập trình mạng nâng cao**, do `TEACHER1` quản lý.

## 8. Bài tự luyện tập cho sinh viên

- Cho phép chuyển mục đích câu hỏi sang **Luyện tập**, lưu phân loại rồi công bố.
- Bổ sung khu vực **Bài tập → Tự luyện tập**.
- Sinh viên trong lớp tự chọn bài đã công bố mà không cần giảng viên giao riêng từng người.
- Hỗ trợ cả bài code và bài nộp file.
- Bài code dùng lại trình soạn thảo, chạy thử, nộp và chấm tự động.
- Bài file dùng lại luồng nộp, lịch sử và nhận xét/chấm điểm của giảng viên.
- Kết quả luyện tập không được cộng vào điểm bài tập hay điểm kỳ thi của khóa học.
- Câu thực hành/thi chưa được giao không xuất hiện trong danh sách tự luyện.
- Lưu trữ hoặc đổi mục đích câu hỏi sẽ thu hồi quyền tiếp cận tự luyện; lịch sử nộp vẫn được lưu.

## 9. Tạo bài thực hành từ ngân hàng

- Trong form tạo bài tập lập trình, chọn nhiều câu trực tiếp từ ngân hàng.
- Có thể kết hợp câu đã lưu với bài toán nhập mới.
- Giữ đề bài, test case và cấu hình chấm khi sao chép.
- Hiển thị các câu đã có trong danh sách ngân hàng và tránh thêm lại khi lưu.
- Bổ sung thao tác chọn nhiều câu nộp file từ ngân hàng để tạo bài thực hành cho lớp.
- Ghép yêu cầu, giữ thông tin câu nguồn và định dạng bài nộp.
- Dùng lại các chức năng giao bài, nộp file/code, chấm và lịch sử hiện có.

## 10. Tách câu hỏi, đề thi và kỳ thi

Đã tổ chức theo luồng **Câu hỏi → Đề thi → Kỳ thi**:

| Đối tượng | Nội dung quản lý |
| --- | --- |
| Câu hỏi | Một đề bài, phân loại, điểm và cấu hình bài làm/test |
| Đề thi độc lập | Tập hợp nhiều câu, lưu bản sao nội dung và cấu hình; không chứa lịch thi/danh sách sinh viên |
| Kỳ thi | Sử dụng đề đã lưu hoặc câu được chọn trực tiếp, gắn với lớp, thời gian và đối tượng dự thi |

- Tạo, sửa bản nháp, công bố, tạo bản sao và lưu trữ đề thi độc lập.
- Hỗ trợ đề code và đề nộp file.
- Sử dụng một đề cho nhiều kỳ thi với lịch và danh sách sinh viên khác nhau.
- Chọn đề đã lưu ngay trong form tạo kỳ thi.
- Giữ cách chọn nhiều câu trực tiếp từ ngân hàng khi tạo kỳ thi.
- Thay đổi câu gốc hoặc lưu trữ đề gốc không làm thay đổi nội dung kỳ thi đã tạo.

## 11. Tổ chức kỳ thi và phân phối đề

- Cấu hình thời lượng, giờ bắt đầu và thời gian kết thúc theo giờ Việt Nam.
- Quản lý danh sách sinh viên được dự thi.
- Bổ sung bước **Phân phối đề** trước khi mở kỳ thi mới qua giao diện.
- Trước khi vào làm bài, sinh viên chỉ thấy thông tin phòng thi; câu hỏi được giữ kín.
- Mở thi theo lịch hoặc mở ngay sau bước kiểm tra cấu hình.
- Thời gian tính chung cho phòng thi; vào muộn không được cấp lại toàn bộ thời lượng.
- Hết giờ khóa nhận bài; hỗ trợ sinh viên kết thúc bài làm sớm.
- Phân biệt thông báo đề trống, câu thiếu test và test vượt ngân sách chấm.
- Kiểm tra số câu sau khi lưu để phát hiện server chưa nhận đủ lựa chọn.
- Hiển thị tích chọn các câu đã có trong kỳ thi; tránh sao chép trùng khi lưu lại.

Với đề nộp file từ ngân hàng:

- Tạo file đề TXT từ các câu trong đề thi độc lập.
- Giảng viên có thể phân phối cho danh sách sinh viên thuộc lớp, mở và kết thúc kỳ thi qua luồng kiểm tra quyền riêng.
- Giữ các chế độ phân phối nhiều file sẵn có của hệ thống, gồm ngẫu nhiên và các chế độ lựa chọn khác.

## 12. Bộ câu code theo từng sinh viên

- Chọn giao cùng bộ câu cho cả lớp hoặc bộ câu ngẫu nhiên theo từng sinh viên.
- Cấu hình số câu mỗi sinh viên nhận từ tập câu của đề.
- Ưu tiên bộ khác nhau khi còn tổ hợp chưa dùng; có thể trùng khi số sinh viên vượt số tổ hợp.
- Lưu cố định bộ câu lúc phân phối; tải lại trang hoặc khởi động lại server không đổi đề.
- Sinh viên chỉ đọc, chạy thử, xem lịch sử và nộp câu thuộc bộ được giao.
- Backend kiểm tra chỉ số câu tại các API làm bài, không chỉ lọc trên giao diện.
- Không đưa bảng phân phối hoặc các câu ngoài bộ vào dữ liệu sinh viên.
- Khi sửa cấu hình bộ câu trước giờ mở, yêu cầu phân phối lại.

## 13. Chấm điểm, kết quả và lịch sử

- Chấm tự động code bằng bộ chấm Docker theo test mẫu và test ẩn.
- Tính điểm theo tỷ lệ test đạt của từng câu.
- Tổng hợp điểm tốt nhất từng câu, tổng điểm và quy đổi thang 10.
- Với đề riêng từng sinh viên, chỉ tính các câu được giao; câu không được giao không bị tính 0.
- Áp dụng cùng cách tính vào điểm giữa kỳ/cuối kỳ trong sổ điểm.
- Bổ sung bảng kết quả theo sinh viên: điểm từng câu, tổng điểm, số lần nộp, trạng thái chấm và lỗi bộ chấm.
- Lưu snapshot câu/test của lần nộp và lịch sử chấm lại.
- Sinh viên xem lịch sử và kết quả của mình; người quản lý xem dữ liệu trong phạm vi được phép.

## 14. Kiểm thử và hướng dẫn

- Đã chạy bộ hồi quy **180 test**, không có lỗi; **5 test cần Docker được bỏ qua** trong môi trường kiểm thử.
- Đã kiểm thử trình duyệt các luồng quản lý ngân hàng, câu hỏi file/code, bài thực hành, đề thi độc lập, phân phối và tự luyện tập.
- Đã kiểm tra thời gian phòng thi, khóa nộp khi hết giờ, bảo mật câu hỏi/test ẩn và quyền theo lớp/chủ sở hữu.
- Chấm code thực tế cần Docker và image bộ chấm sẵn sàng.

Tài liệu thao tác:

- [Phân loại và phân quyền](phan-loai-phan-quyen.md).
- [Ngân hàng câu hỏi](ngan-hang-cau-hoi.md).
- [Quy trình đề thi lập trình](de-thi-lap-trinh.md).
- [Câu hỏi → Đề thi → Kỳ thi](cau-hoi-de-thi-ky-thi.md).

Sau khi cập nhật backend/giao diện, khởi động lại server rồi tải lại trang bằng **Ctrl+F5**.
