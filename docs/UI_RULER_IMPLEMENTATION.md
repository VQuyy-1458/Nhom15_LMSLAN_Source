# Đồng bộ giao diện theo LAN_LMS_UI_DESIGN_RULER.md

## Phạm vi

- Dùng các token màu, radius và shadow có sẵn trong `ui-polish.css`.
- Thống nhất khoảng cách, heading, toolbar, nút, trường nhập, tab, card,
  bảng cuộn ngang, trạng thái rỗng, phân trang và dialog cho hai vai trò.
- Áp dụng các selector chung cho cả template và HTML do JavaScript dựng.
- Chuyển CSS khóa học vào `page_styles`, trước lớp CSS dùng chung.
- Thống nhất drawer ở màn hình dưới 768px, sidebar desktop rộng 244px.
- Giới hạn kích thước lưới nội dung để lịch, bảng điểm và danh sách trong
  khóa học không đẩy tràn toàn trang.
- Dùng nhãn “Tổng quan” cho dashboard. Cập nhật phiên bản URL tài nguyên.
- Giữ nguyên route, hợp đồng form/DOM, API, phân quyền và xử lý nghiệp vụ.

## Kiểm tra

`node tests/browser_ui_consistency.cjs` dùng server fixture và dữ liệu tạm,
không sử dụng tài khoản hoặc dữ liệu hệ thống đang chạy.

- Qua 128 tổ hợp trang/kích thước: 20 trang chính và 12 tab chi tiết khóa học
  ở 1440, 1024, 768, 390px; không tràn viewport, có một h1 đang hiển thị.
- Qua kiểm tra menu ở 32 tổ hợp trang/kích thước, gồm màn hình thấp và ngang.
- Qua kiểm tra vào kỳ thi code: desktop/mobile, countdown, khóa khi hết giờ,
  ẩn câu hỏi trước khi vào thi và giữ thời hạn chung. Judge dùng fixture.
- Kiểm tra đăng nhập thực tế qua HTTP LAN, hộp thoại đặt lại mật khẩu và
  gửi thông báo đã qua. Bước QR cuối của cùng script chưa qua: script đợi
  `#qr-read-status` nhưng giao diện hiện hiển thị lịch sử “Có mặt”.
- `npm test`: chạy 187 test, 15 bỏ qua, 2 lỗi: tiến trình LAN launcher không
  dừng trong 10 giây/khóa file Windows; module `test_question_workflows`
  tham chiếu `LearningTests.teacher_context` không tồn tại. Không sửa backend
  hoặc các lỗi kiểm thử ngoài phạm vi giao diện.

Ảnh và báo cáo bố cục: `previews/ui-consistency/after/`.
Ảnh kiểm tra nhanh sau cập nhật nhãn: `previews/ui-consistency/quick/`.
Ảnh kiểm tra menu/kỳ thi: `previews/student-qa/`.

Chưa nghiệm thu thực tế trên thiết bị LAN riêng, mất mạng, camera hoặc
chấm bằng Docker; kết quả kiểm tra bố cục không thay thế các kiểm tra đó.
