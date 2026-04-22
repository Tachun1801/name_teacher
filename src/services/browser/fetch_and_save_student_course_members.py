import json

from src.config import (
    DEFAULT_TIMEOUT_MS,
    PERSONAL_TRANSCRIPT_URL,
    STUDENT_COURSE_MEMBERS_API_PART,
    STUDENT_COURSE_MEMBERS_PERSON_MAP_FILE,
    STUDENT_COURSE_MEMBERS_RAW_FILE,
)
from src.services.person_extractor.save_person_id_name_file import save_person_id_name_file


def fetch_and_save_student_course_members(page, timeout_ms: int = DEFAULT_TIMEOUT_MS) -> None:
    """Vào personal-transcript, chờ API student-course-members và lưu JSON."""
    print("\n--- Đang vào personal-transcript để lấy dữ liệu student_course_members... ---")
    response = None

    for attempt in range(2):
        try:
            with page.expect_response(
                lambda res: (
                    STUDENT_COURSE_MEMBERS_API_PART in res.url
                    and res.request.method.upper() == "GET"
                ),
                timeout=timeout_ms,
            ) as response_info:
                if attempt == 0:
                    page.goto(PERSONAL_TRANSCRIPT_URL, wait_until="domcontentloaded")
                else:
                    page.reload(wait_until="domcontentloaded")
            response = response_info.value
            break
        except Exception:
            if attempt == 1:
                raise

    with open(STUDENT_COURSE_MEMBERS_RAW_FILE, "w", encoding="utf-8") as output_handle:
        json.dump(response.json(), output_handle, ensure_ascii=False, indent=4)
    print(f"--- Đã lưu dữ liệu vào {STUDENT_COURSE_MEMBERS_RAW_FILE} ---")

    try:
        save_person_id_name_file(
            str(STUDENT_COURSE_MEMBERS_RAW_FILE),
            str(STUDENT_COURSE_MEMBERS_PERSON_MAP_FILE),
        )
    except Exception as error:
        print(f"Không lọc được file person map từ course-members: {error}")
