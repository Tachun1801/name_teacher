"""VN: Khai báo đường dẫn, URL, và hằng số cấu hình dùng chung.
EN: Shared paths, URLs, and configuration constants.
JP: 共通のパス、URL、設定定数を定義します。
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
DERIVED_DATA_DIR = DATA_DIR / "derived"
CACHE_DATA_DIR = DATA_DIR / "cache"

# URLs gốc của hệ thống HUST mà chương trình sẽ đi qua theo thứ tự sử dụng.
CLASS_REGISTRATION_URL = "https://qldt.hust.edu.vn/students/learn/class-registration"
PERSONAL_TRANSCRIPT_URL = "https://qldt.hust.edu.vn/students/learn/personal-transcript"
TIMETABLE_URL = "https://qldt.hust.edu.vn/students/learn/timetable"

# Các chuỗi nhận diện API cần chờ khi nghe phản hồi từ trình duyệt.
TARGET_URL_PART = "student-requests?ignorePhase=true"
STUDENT_COURSE_MEMBERS_API_PART = "api/v1/course-member/student-course-members"
STUDENT_TIMETABLE_API_PART = "api/v2/timetables/query-student-timetable-in-range"

# Timeout mặc định để tránh treo vô hạn khi chờ response từ API.
DEFAULT_TIMEOUT_MS = 45000

# File raw lưu nguyên phản hồi API để có thể debug hoặc tái xử lý sau này.
CLASS_REGISTRATION_RAW_FILE = RAW_DATA_DIR / "class_registration_response.json"
STUDENT_COURSE_MEMBERS_RAW_FILE = RAW_DATA_DIR / "student_course_members_response.json"
STUDENT_TIMETABLE_RAW_FILE = RAW_DATA_DIR / "student_timetable_response.json"

# File derived dùng cho mapping id-name đã lọc từ raw data.
STUDENT_COURSE_MEMBERS_PERSON_MAP_FILE = DERIVED_DATA_DIR / "student_course_members_person_map.json"
STUDENT_TIMETABLE_PERSON_MAP_FILE = DERIVED_DATA_DIR / "student_timetable_person_map.json"

# Cache dùng để tránh phải gọi API giảng viên mỗi lần khởi động chương trình.
TEACHER_DIRECTORY_CACHE_FILE = CACHE_DATA_DIR / "teacher_directory_cache.json"


def ensure_output_directories() -> None:
    # VN: Tạo lần lượt từng thư mục cần thiết.
    # EN: Create each required directory in turn.
    # JP: 必要な各ディレクトリを順番に作成します。
    # VN: mkdir(..., exist_ok=True) giúp hàm này an toàn khi chạy lặp lại nhiều lần.
    # EN: mkdir(..., exist_ok=True) keeps this function safe to call repeatedly.
    # JP: mkdir(..., exist_ok=True) により、この関数は何度呼んでも安全です。
    for folder in (RAW_DATA_DIR, DERIVED_DATA_DIR, CACHE_DATA_DIR):
        folder.mkdir(parents=True, exist_ok=True)
