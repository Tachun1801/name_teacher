from src.config import (
    CLASS_REGISTRATION_URL,
    STUDENT_COURSE_MEMBERS_PERSON_MAP_FILE,
    STUDENT_TIMETABLE_PERSON_MAP_FILE,
)
from src.services.browser.fetch_and_save_student_course_members import fetch_and_save_student_course_members
from src.services.browser.fetch_and_save_student_timetable import fetch_and_save_student_timetable
from src.services.browser.process_class_registration_response import process_class_registration_response
from src.services.teacher_mapping.merge_person_files_into_mapping import merge_person_files_into_mapping


def run_automation(playwright, teacher_mapping: dict[str, str]) -> None:
    """Điều phối toàn bộ quá trình tự động hóa với Playwright."""
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    print("\n" + "=" * 50)
    print("HỆ THỐNG BẮT ĐẦU CHẠY...")
    print("1. Hãy thao tác đăng nhập và giải Captcha trên cửa sổ trình duyệt.")
    print("2. Sau khi đăng nhập thành công, quay lại terminal và nhấn ENTER để bắt đầu quét.")
    print("=" * 50)

    page.on("response", lambda response: process_class_registration_response(response, teacher_mapping))
    page.goto(CLASS_REGISTRATION_URL)

    input("\n>>> [CHỜ XÁC NHẬN] Nhấn ENTER sau khi bạn đã vào trang đăng ký... <<<")

    try:
        fetch_and_save_student_course_members(page)
    except Exception as error:
        print(f"Không lấy được dữ liệu course-members: {error}")

    try:
        fetch_and_save_student_timetable(page)
    except Exception as error:
        print(f"Không lấy được dữ liệu timetable: {error}")

    merge_person_files_into_mapping(
        teacher_mapping,
        str(STUDENT_COURSE_MEMBERS_PERSON_MAP_FILE),
        str(STUDENT_TIMETABLE_PERSON_MAP_FILE),
    )

    try:
        while True:
            page.goto(CLASS_REGISTRATION_URL)
            page.wait_for_timeout(5000)
    except Exception as error:
        print(f"\nDừng chương trình: {error}")
    finally:
        browser.close()
