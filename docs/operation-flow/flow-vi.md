# Cách thức hoạt động và luồng chạy chi tiết (Tiếng Việt)

## 1) Mục tiêu luồng chạy
Hệ thống liên tục lắng nghe response class-registration, cập nhật snapshot JSON cục bộ, trích xuất mapping person, và in thời khóa biểu có tên giảng viên ra terminal.

## 2) Giai đoạn khởi động

1. Người dùng chạy `python app.py` (hoặc `python src/main.py`).
2. `app.py` chuyển quyền cho `src.main.main()`.
3. `main()` gọi `ensure_output_directories()` để tạo thư mục dữ liệu.
4. `main()` gọi `get_teacher_mapping(cache_file)`:
   - đọc cache từ `data/cache/teacher_directory_cache.json` nếu có.
   - nếu cache ít dữ liệu thì gọi API để bổ sung danh sách giảng viên.
   - merge dữ liệu `MANUAL_TEACHER_DATA` làm lớp ghi đè cuối cùng.
5. `main()` mở Playwright và gọi `run_automation(playwright, teacher_mapping)`.

## 3) Vòng đời automation trình duyệt

Trong `run_automation()`:

1. Mở Chromium với `headless=False`.
2. Tạo context và page.
3. Đăng ký listener response:
   - mọi response đi qua `process_class_registration_response(response, teacher_mapping)`.
4. Mở trang đăng ký học phần.
5. Chờ người dùng đăng nhập/captcha xong rồi nhấn ENTER.

## 4) Xử lý response class-registration

`process_class_registration_response()` làm các bước:

1. Bỏ qua response không chứa `TARGET_URL_PART`.
2. Parse JSON và lưu vào `data/raw/class_registration_response.json`.
3. Xóa màn hình terminal.
4. Gọi `extract_hust_schedule_final()` để parse và in lịch:
   - duyệt block lớp/học phần/lịch học.
   - map teacherId sang tên bằng `teacher_mapping`.
   - sắp xếp theo thứ/buổi/tiết.
   - in thời khóa biểu và tổng tín chỉ.

Hàm này được gọi lặp lại khi có response mục tiêu mới.

## 5) Bắt dữ liệu một lần sau khi người dùng xác nhận

Trong `run_automation()`, sau ENTER:

1. Gọi `fetch_and_save_student_course_members(page)`:
   - vào trang bảng điểm cá nhân.
   - chờ response GET khớp `STUDENT_COURSE_MEMBERS_API_PART`.
   - lưu raw vào `data/raw/student_course_members_response.json`.
   - gọi `save_person_id_name_file()` để sinh
     `data/derived/student_course_members_person_map.json`.

2. Gọi `fetch_and_save_student_timetable(page)`:
   - vào trang thời khóa biểu.
   - chờ response POST khớp `STUDENT_TIMETABLE_API_PART`.
   - lưu raw vào `data/raw/student_timetable_response.json`.
   - gọi `save_person_id_name_file()` để sinh
     `data/derived/student_timetable_person_map.json`.

3. Gộp 2 map person mới vào mapping đang dùng bằng
   `merge_person_files_into_mapping(...)`.

## 6) Cơ chế trích xuất person map

Luồng `save_person_id_name_file(input_file, output_file)`:

1. Đọc JSON nguồn.
2. Duyệt đệ quy toàn bộ object/list (`walk_and_collect_person_pairs`).
3. Với mỗi dict, trích dữ liệu theo pattern (`collect_person_pairs_from_dict`):
   - `<prefix>Id + <prefix>Name`
   - `<prefix>Ids + <prefix>Names`
   - `id + fullName`
   - phần tử `gradeLogs` chứa JSON string có `staffId + staffName`
4. Chuẩn hóa ID/tên, loại giá trị không hợp lệ.
5. Bỏ qua ID `-1`.
6. Xử lý xung đột tên cùng ID theo nguyên tắc ổn định.
7. Sort và ghi file ID->name cuối cùng.

## 7) Vòng lặp refresh liên tục

Sau khi setup xong, `run_automation()` chạy vòng lặp vô hạn:

1. Mỗi 5 giây mở lại trang đăng ký học phần.
2. Listener response luôn hoạt động và in lại lịch khi có dữ liệu mới.
3. Trình duyệt chỉ đóng khi vòng lặp dừng vì lỗi hoặc bị kết thúc.

## 8) Mô hình nhất quán dữ liệu

- `data/raw/*`: snapshot response gốc (ghi đè bản mới nhất).
- `data/derived/*`: dữ liệu trích xuất xác định từ raw tương ứng.
- `teacher_mapping` trong RAM gồm 3 lớp:
  1) cache/API,
  2) dữ liệu nhập tay,
  3) map person sinh trong runtime.

## 9) Khả năng chịu lỗi

- Các bước chờ response mục tiêu có retry 2 lần.
- Lỗi parse/IO thường được bắt và log để luồng chính tiếp tục.
- Trường thiếu dữ liệu có fallback để hạn chế vỡ khi in lịch.
