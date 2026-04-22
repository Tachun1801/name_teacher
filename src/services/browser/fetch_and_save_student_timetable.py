import json

from src.config import (
    DEFAULT_TIMEOUT_MS,
    STUDENT_TIMETABLE_API_PART,
    STUDENT_TIMETABLE_PERSON_MAP_FILE,
    STUDENT_TIMETABLE_RAW_FILE,
    TIMETABLE_URL,
)
from src.services.person_extractor.save_person_id_name_file import save_person_id_name_file


def fetch_and_save_student_timetable(page, timeout_ms: int = DEFAULT_TIMEOUT_MS) -> None:
    """Vào timetable, chờ API query-student-timetable-in-range và lưu JSON."""
    print("\n--- Đang vào timetable để lấy dữ liệu student_timetable... ---")
    response = None

    for attempt in range(2):
        try:
            with page.expect_response(
                lambda res: (
                    STUDENT_TIMETABLE_API_PART in res.url
                    and res.request.method.upper() == "POST"
                ),
                timeout=timeout_ms,
            ) as response_info:
                if attempt == 0:
                    page.goto(TIMETABLE_URL, wait_until="domcontentloaded")
                else:
                    page.reload(wait_until="domcontentloaded")
            response = response_info.value
            break
        except Exception:
            if attempt == 1:
                raise

    with open(STUDENT_TIMETABLE_RAW_FILE, "w", encoding="utf-8") as output_handle:
        json.dump(response.json(), output_handle, ensure_ascii=False, indent=4)
    print(f"--- Đã lưu dữ liệu vào {STUDENT_TIMETABLE_RAW_FILE} ---")

    try:
        save_person_id_name_file(
            str(STUDENT_TIMETABLE_RAW_FILE),
            str(STUDENT_TIMETABLE_PERSON_MAP_FILE),
        )
    except Exception as error:
        print(f"Không lọc được file person map từ timetable: {error}")
