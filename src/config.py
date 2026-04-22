from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
DERIVED_DATA_DIR = DATA_DIR / "derived"
CACHE_DATA_DIR = DATA_DIR / "cache"

CLASS_REGISTRATION_URL = "https://qldt.hust.edu.vn/students/learn/class-registration"
PERSONAL_TRANSCRIPT_URL = "https://qldt.hust.edu.vn/students/learn/personal-transcript"
TIMETABLE_URL = "https://qldt.hust.edu.vn/students/learn/timetable"

TARGET_URL_PART = "student-requests?ignorePhase=true"
STUDENT_COURSE_MEMBERS_API_PART = "api/v1/course-member/student-course-members"
STUDENT_TIMETABLE_API_PART = "api/v2/timetables/query-student-timetable-in-range"

DEFAULT_TIMEOUT_MS = 45000

CLASS_REGISTRATION_RAW_FILE = RAW_DATA_DIR / "class_registration_response.json"
STUDENT_COURSE_MEMBERS_RAW_FILE = RAW_DATA_DIR / "student_course_members_response.json"
STUDENT_TIMETABLE_RAW_FILE = RAW_DATA_DIR / "student_timetable_response.json"

STUDENT_COURSE_MEMBERS_PERSON_MAP_FILE = DERIVED_DATA_DIR / "student_course_members_person_map.json"
STUDENT_TIMETABLE_PERSON_MAP_FILE = DERIVED_DATA_DIR / "student_timetable_person_map.json"

TEACHER_DIRECTORY_CACHE_FILE = CACHE_DATA_DIR / "teacher_directory_cache.json"


def ensure_output_directories() -> None:
    for folder in (RAW_DATA_DIR, DERIVED_DATA_DIR, CACHE_DATA_DIR):
        folder.mkdir(parents=True, exist_ok=True)
