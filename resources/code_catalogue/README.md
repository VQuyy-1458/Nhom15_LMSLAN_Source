# Bộ 60 bài code LAN-LMS

20 C++ (CSES), 20 Java (Exercism, gồm 17 class OOP và 3 program hoàn chỉnh), 20 Python (Exercism chuyển thể stdin/stdout JSON).
Mặc định 20 bài cho luyện tập, 40 bài riêng tư. Đây là một kho chung: giảng viên đổi liên kết khóa học, bật/tắt luyện tập và dùng lại bất kỳ bài nào trong đề thực hành/thi.

Mỗi bài có URL gốc, hash bản nguồn, test mẫu và test ẩn. CSES được viết lại ngắn bằng tiếng Việt; ví dụ gốc có ghi nguồn. Exercism dùng MIT, giấy phép kèm thư mục này. Các lời giải tham chiếu tự viết phục vụ xác minh, không phục vụ qua API sinh viên.

Các bản chuyển thể nêu rõ giao thức và phạm vi trong từng đề. Java Reverse String giới hạn ASCII; Bank Account kiểm thử tuần tự, không tuyên bố chấm concurrency. JSON checker so sánh cấu trúc, phân biệt boolean và number, không chấp nhận JSON không hợp lệ.

Tái tạo: `python scripts/fetch_catalogue_sources.py`, `python scripts/build_code_catalogue.py`. Kiểm chứng lời giải trong Docker: `python scripts/validate_code_catalogue.py`. Nạp dữ liệu: `python scripts/seed_shared_catalogue.py --apply` (nên dừng server trước khi nạp).
