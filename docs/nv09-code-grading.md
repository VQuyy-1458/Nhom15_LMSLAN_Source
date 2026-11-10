# Chấm program, class và method

Trong Cấu hình kỳ thi → Thi lập trình → Bài toán, chọn dạng bài và ngôn ngữ mã kiểm thử. Program cũ tiếp tục hỗ trợ nhiều ngôn ngữ. Class/method và template tùy chỉnh dùng một ngôn ngữ cố định cho mỗi bài.

- Program: nộp chương trình hoàn chỉnh, input được truyền vào stdin.
- Class: nộp lớp; test code tạo đối tượng và gọi phương thức. C không hỗ trợ class.
- Method: nộp hàm hoặc phương thức; test code gọi hàm và in kết quả.
- Template trống dùng khuôn mặc định. Template tùy chỉnh phải chứa `{{ STUDENT_ANSWER }}` và `{{ TEST.testcode }}`. Đây là phép thay thế văn bản một lượt, không chạy template engine trên máy chủ. Java tùy chỉnh cần tạo lớp Main.

Java class mặc định giữ public class trong file đúng tên và tạo Main riêng. Bài nộp có thể chứa các lớp phụ không public trong cùng một file, ví dụ `abstract class Person` và `public class Student extends Person`; bộ chấm biên dịch cả hai file nguồn. Không dùng package hoặc lớp tên Main. Java method được chèn vào Main và test chạy trong phương thức của đối tượng Main; không nộp cả lớp cho dạng method. C/C++ dùng hàm main do hệ thống tạo; Python ghép định nghĩa với mã gọi thử.

## Ví dụ Java method

Bài làm: `int add(int a,int b){ return a+b; }`

Test code: `System.out.println(add(2,3));`

Standard input: trống. Expected output: `5`.

## Ví dụ Java class

Bài làm: `public class Product { public int price(){return 7;} }`

Test code: `System.out.println(new Product().price());`

Expected output: `7`.

## Ví dụ và phản hồi

Test mẫu quyết định ví dụ công khai trên đề. Phản hồi sau chấm được chọn độc lập: theo test mẫu, hiện, ẩn, chỉ hiện khi đúng hoặc chỉ hiện khi sai. Backend lọc dữ liệu trước khi trả cho sinh viên, kể cả lịch sử chấm lại. Log biên dịch chứa mã kiểm thử chỉ dành cho giảng viên; sinh viên nhận thông báo lỗi hợp đồng lớp/phương thức.

Nút Xem trước đề hiển thị các ví dụ được chọn. CSV giữ các cột input,output,sample và bổ sung test_code,feedback_visibility. Dùng nháy kép cho mã có dấu phẩy hoặc nhiều dòng.

Mỗi bài nộp tiếp tục lưu nguồn và snapshot bài toán/test/template. Các test của dạng mới chạy độc lập trong container giới hạn tài nguyên. Điểm vẫn tính theo tỷ lệ test đạt; chưa bổ sung trọng số từng test, penalty hoặc combinator của CodeRunner.

## Kiểm tra

`python -m unittest tests.test_code_templates tests.test_code_runner tests.test_learning`

Đặt `CSS_JUDGE_TESTS=1`, Docker đang chạy và image `classroom-judge:1` đã có để chạy kiểm thử thực tế Java class/method, C++ class, Python function, WA và CE.
