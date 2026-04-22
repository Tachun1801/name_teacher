# Teachers of HUST v3

Công cụ tự động bắt dữ liệu từ hệ thống học tập HUST bằng Playwright, xử lý JSON và in thời khóa biểu có gắn tên giảng viên.

## Mục tiêu

- Tự động mở trang và lắng nghe các API response cần thiết.
- Lưu dữ liệu raw để tiện debug/đối soát.
- Trích xuất mapping `person_id -> person_name` từ nhiều nguồn.
- Hợp nhất mapping giảng viên từ cache, API và dữ liệu nhập tay.
- In thời khóa biểu rõ ràng trong terminal.

## Tính năng chính

- Browser automation bằng Playwright (chế độ sync).
- Cơ chế chờ đúng API response theo URL pattern.
- Sinh dữ liệu theo lớp:
  - `data/raw`: dữ liệu response gốc.
  - `data/derived`: dữ liệu mapping đã xử lý.
  - `data/cache`: dữ liệu cache phục vụ lần chạy sau.
- Cấu trúc code đã tách nhỏ theo hướng 1 function/1 file để dễ bảo trì.

## Cấu trúc dự án

```text
.
├── app.py
├── src
│   ├── main.py
│   ├── config.py
│   └── services
│       ├── browser
│       ├── person_extractor
│       ├── teacher_mapping
│       └── schedule_printer.py
├── data
│   ├── raw
│   ├── derived
│   └── cache
└── docs
    ├── project-structure
    └── operation-flow
```

## Yêu cầu môi trường

- Python 3.10+
- Linux/macOS/Windows
- Trình duyệt Chromium (Playwright sẽ dùng browser tương ứng)

## Cài đặt

### 1) Tạo và kích hoạt môi trường ảo

```bash
python -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 2) Cài dependency

```bash
pip install playwright requests
python -m playwright install chromium
```

## Cách chạy

### Cách 1 (khuyến nghị)

```bash
python app.py
```

### Cách 2

```bash
python src/main.py
```

## Luồng chạy thực tế

1. Chương trình khởi tạo thư mục output trong `data/`.
2. Nạp teacher mapping từ cache + API + dữ liệu nhập tay.
3. Mở browser để bạn đăng nhập và xử lý captcha.
4. Sau khi bạn nhấn ENTER trong terminal:
   - Bắt và lưu response course-members.
   - Bắt và lưu response timetable.
   - Sinh person map từ từng response.
   - Merge vào teacher mapping đang dùng.
5. Hệ thống tiếp tục lắng nghe response class-registration và in lại thời khóa biểu khi có dữ liệu mới.

## Dữ liệu đầu ra

### Raw

- `data/raw/class_registration_response.json`
- `data/raw/student_course_members_response.json`
- `data/raw/student_timetable_response.json`

### Derived

- `data/derived/student_course_members_person_map.json`
- `data/derived/student_timetable_person_map.json`

### Cache

- `data/cache/teacher_directory_cache.json`

## Tùy chỉnh nhanh

- Cập nhật danh sách giảng viên nhập tay tại:
  - `src/services/teacher_mapping/manual_teacher_data.py`
- Cập nhật timeout, URL và đường dẫn output tại:
  - `src/config.py`

## Tài liệu chi tiết

- Cấu trúc dự án đa ngôn ngữ: thư mục `docs/project-structure`
- Luồng hoạt động đa ngôn ngữ: thư mục `docs/operation-flow`

## Lưu ý khi push GitHub

Nên cân nhắc thêm `.gitignore` để tránh commit dữ liệu runtime không cần thiết, ví dụ:

```gitignore
.venv/
__pycache__/
*.pyc

data/raw/*.json
data/derived/*.json
```

Nếu bạn muốn giữ dữ liệu mẫu để demo, chỉ nên giữ một bộ nhỏ đã ẩn thông tin nhạy cảm.

## Disclaimer

Dự án này dùng cho mục đích học tập/cá nhân. Hãy tuân thủ điều khoản sử dụng của hệ thống nguồn dữ liệu và không chia sẻ dữ liệu cá nhân nhạy cảm.
