# Cấu trúc dự án (Tiếng Việt)

## 1) Mục tiêu tổng quát
Dự án tự động hóa việc bắt dữ liệu từ các trang sinh viên HUST bằng Playwright, sau đó xử lý JSON để in thời khóa biểu dễ đọc kèm tên giảng viên.

## 2) Thư mục/chạy chính

- `app.py`
  - File chạy vào hệ thống. Chỉ gọi `src.main.main()`.
- `src/`
  - Toàn bộ mã nguồn chính.
- `data/`
  - Dữ liệu JSON bắt được và dữ liệu đã xử lý.
- `.venv/`
  - Môi trường Python.
- `docs/`
  - Tài liệu mô tả dự án.

## 3) Chi tiết mã nguồn

### `src/main.py`
- `main()`
  - Điều phối luồng chạy chính.
  - Tạo thư mục output nếu thiếu.
  - Nạp mapping giảng viên.
  - Khởi chạy Playwright và bắt đầu automation.

### `src/config.py`
- Chứa hằng số cấu hình:
  - URL các trang và dấu hiệu API.
  - timeout mặc định.
  - đường dẫn file output.
- `ensure_output_directories()`
  - Tạo `data/raw`, `data/derived`, `data/cache`.

### `src/services/browser/`
- `run_automation.py`
  - Luồng tự động hóa chính trên trình duyệt.
- `process_class_registration_response.py`
  - Lọc response class-registration và gọi in thời khóa biểu.
- `fetch_and_save_student_course_members.py`
  - Bắt/lưu response course-members.
  - Sinh thêm file mapping person-id-name từ response này.
- `fetch_and_save_student_timetable.py`
  - Bắt/lưu response timetable.
  - Sinh thêm file mapping person-id-name từ response này.

### `src/services/teacher_mapping/`
- `manual_teacher_data.py`
  - Dữ liệu giảng viên nhập tay (ID -> tên).
- `get_teacher_mapping.py`
  - Nạp cache, gọi API bổ sung khi cần, rồi merge dữ liệu nhập tay.
- `merge_person_files_into_mapping.py`
  - Gộp các map person đã sinh vào mapping đang dùng mà không ghi đè key có sẵn.

### `src/services/person_extractor/`
- `constants.py`
  - Tập key gợi ý để nhận diện trường thông tin con người.
- `is_person_key.py`
  - Kiểm tra tên key có phải key liên quan người hay không.
- `to_string_id.py`
  - Chuẩn hóa ID về chuỗi an toàn.
- `split_names.py`
  - Tách chuỗi nhiều tên thành danh sách.
- `add_person_pair.py`
  - Validate và thêm cặp `(id, name)` vào set.
- `collect_person_pairs_from_dict.py`
  - Trích cặp person từ một object dict theo nhiều pattern.
- `walk_and_collect_person_pairs.py`
  - Duyệt đệ quy JSON lồng nhau để gom dữ liệu person.
- `save_person_id_name_file.py`
  - Tạo file JSON mapping ID->tên từ dữ liệu nguồn.

### `src/services/schedule_printer.py`
- `extract_hust_schedule_final()`
  - Đọc dữ liệu class-registration.
  - Tổng hợp lịch học/tín chỉ.
  - In thời khóa biểu theo định dạng rõ ràng.

## 4) Cấu trúc dữ liệu

### `data/raw/`
Dữ liệu response gốc:
- `class_registration_response.json`
- `student_course_members_response.json`
- `student_timetable_response.json`

### `data/derived/`
Dữ liệu phát sinh sau xử lý:
- `student_course_members_person_map.json`
- `student_timetable_person_map.json`

### `data/cache/`
Dữ liệu cache:
- `teacher_directory_cache.json`

## 5) Tóm tắt quan hệ các thành phần

1. `app.py` gọi `src/main.py`.
2. `config` tạo thư mục output.
3. Nạp mapping giảng viên.
4. Browser automation bắt response API cần thiết.
5. Ghi dữ liệu thô vào `data/raw`.
6. Sinh map person vào `data/derived`.
7. Gộp map vào teacher mapping.
8. Khi có response class-registration thì parse và in thời khóa biểu.
