# Cấu trúc dự án (Tiếng Việt)

Mục tiêu của tài liệu này là trình bày cấu trúc theo dạng cây, chi tiết đến từng file để dễ tra cứu nhanh.

## Cây thư mục và file

```text
teachers-of-hust-v3/
├── README.md                                    # Tổng quan dự án, cài đặt, cách chạy
├── run.py                                       # Entry point chạy chương trình
├── docs/
│   ├── operation-flow/
│   │   ├── flow-en.md                           # Luồng hoạt động (English)
│   │   ├── flow-ja.md                           # Luồng hoạt động (Japanese)
│   │   └── flow-vi.md                           # Luồng hoạt động (Vietnamese)
│   └── project-structure/
│       ├── structure-en.md                      # Mô tả cấu trúc dự án (English)
│       ├── structure-ja.md                      # Mô tả cấu trúc dự án (Japanese)
│       └── structure-vi.md                      # Mô tả cấu trúc dự án (Vietnamese)
└── src/
    ├── __init__.py                              # Đánh dấu package src
    ├── config.py                                # Hằng số cấu hình + tạo thư mục output data
    ├── main.py                                  # Điều phối luồng chính
    └── services/
        ├── __init__.py                          # Đánh dấu package services
        ├── schedule_printer.py                  # Parse/in thời khóa biểu từ dữ liệu class-registration
        ├── browser/
        │   ├── __init__.py                      # Đánh dấu package browser
        │   ├── fetch_and_save_student_course_members.py
        │   │                                       # Bắt và lưu response course-members
        │   ├── fetch_and_save_student_timetable.py
        │   │                                       # Bắt và lưu response timetable
        │   ├── process_class_registration_response.py
        │   │                                       # Xử lý response class-registration rồi gọi in lịch
        │   └── run_automation.py                # Luồng Playwright automation chính
        ├── person_extractor/
        │   ├── __init__.py                      # Đánh dấu package person_extractor
        │   ├── add_person_pair.py               # Validate và thêm cặp (id, name)
        │   ├── collect_person_pairs_from_dict.py
        │   │                                       # Trích cặp person từ dict theo nhiều pattern
        │   ├── constants.py                     # Tập key gợi ý nhận diện dữ liệu person
        │   ├── is_person_key.py                 # Kiểm tra key có liên quan người hay không
        │   ├── save_person_id_name_file.py      # Lưu file JSON mapping person_id -> person_name
        │   ├── split_names.py                   # Tách chuỗi nhiều tên thành danh sách tên
        │   ├── to_string_id.py                  # Chuẩn hóa ID về chuỗi
        │   └── walk_and_collect_person_pairs.py # Duyệt đệ quy JSON để gom person pairs
        └── teacher_mapping/
            ├── __init__.py                      # Đánh dấu package teacher_mapping
            ├── get_teacher_mapping.py           # Nạp/merge mapping giảng viên từ nhiều nguồn
            ├── manual_teacher_data.py           # Dữ liệu giảng viên nhập tay
            └── merge_person_files_into_mapping.py
                                                    # Gộp person map phát sinh vào teacher mapping
```

## Dữ liệu runtime (được tạo khi chạy)

Các thư mục/file dưới đây thường không có sẵn từ đầu, sẽ được sinh trong lúc chạy:

```text
data/
├── raw/
│   ├── class_registration_response.json
│   ├── student_course_members_response.json
│   └── student_timetable_response.json
├── derived/
│   ├── student_course_members_person_map.json
│   └── student_timetable_person_map.json
└── cache/
    └── teacher_directory_cache.json
```

Ngoài ra, Python có thể tự sinh thư mục `__pycache__/` và các file `.pyc` trong quá trình chạy.

## Luồng liên kết nhanh

1. `run.py` gọi vào `src.main.main()`.
2. `src/config.py` đảm bảo các thư mục output tồn tại.
3. `src/services/teacher_mapping/get_teacher_mapping.py` chuẩn bị mapping giảng viên.
4. `src/services/browser/run_automation.py` chạy Playwright để bắt response API.
5. Các file trong `src/services/browser/` lưu raw JSON và kích hoạt xử lý tiếp.
6. Các file trong `src/services/person_extractor/` trích xuất `person_id -> person_name`.
7. `src/services/schedule_printer.py` tổng hợp và in thời khóa biểu cuối cùng.
