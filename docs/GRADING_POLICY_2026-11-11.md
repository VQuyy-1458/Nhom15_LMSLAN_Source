# Quy tắc điểm kỳ thi

Quy tắc áp dụng thống nhất cho thi nộp file và thi code:

- **Test:** được tạo nhiều bài, dùng luyện tập/thử hệ thống và không tính vào bảng điểm.
- **Thực hành:** được tạo nhiều bài. Điểm được quy về thang 10 rồi lấy trung bình cùng các bài tập trong thành phần **Bài tập**.
- **Giữa kỳ:** tối đa một bài cho mỗi khóa học.
- **Cuối kỳ:** tối đa một bài cho mỗi khóa học.

Thi file lấy điểm của lần nộp mới nhất. Thi code lấy kết quả tốt nhất của từng bài toán, cộng theo trọng số điểm bài toán rồi quy về thang 10. Một kết quả chưa chấm làm thành phần tương ứng tiếp tục ở trạng thái chưa đủ điểm.

Backend kiểm tra tính duy nhất của Giữa kỳ/Cuối kỳ trên toàn bộ hai hình thức thi. Khi nâng cấp, nếu danh mục cũ có nhiều Giữa kỳ, hệ thống giữ bài đang hoạt động (hoặc bài được lưu sau cùng) làm Giữa kỳ và chuyển các bài cũ hơn thành Thực hành. Việc chuyển được ghi vào audit.
