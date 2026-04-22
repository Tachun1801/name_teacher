"""VN: Điều phối toàn bộ quy trình tự động hóa bằng trình duyệt.
EN: Orchestrate the full browser automation workflow.
JP: ブラウザ自動化の全体フローを制御します。
"""

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
    """VN: Điều phối toàn bộ quá trình tự động hóa với Playwright.
    EN: Orchestrate the full automation workflow with Playwright.
    JP: Playwright での自動化フロー全体を制御します。
    """
    # VN: Mở browser ở chế độ hiện cửa sổ để người dùng có thể đăng nhập và giải captcha thủ công khi hệ thống yêu cầu.
    # EN: Open the browser in visible mode so the user can log in and solve captchas manually when required.
    # JP: ブラウザを表示モードで開き、必要に応じてユーザーが手動でログインや CAPTCHA を解けるようにします。
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    # VN: Đây là phần hướng dẫn trực tiếp cho người chạy chương trình.
    # EN: This is the on-screen guidance for the person running the program.
    # JP: これはプログラム実行者向けの画面上の案内です。
    # VN: Mục tiêu là tách rõ bước thao tác thủ công và bước tự động.
    # EN: The goal is to separate manual steps from automated steps as clearly as possible.
    # JP: 手動操作と自動処理の段階を明確に分けることが目的です。
    print("\n" + "=" * 50)
    print("HỆ THỐNG BẮT ĐẦU CHẠY...")
    print("1. Hãy thao tác đăng nhập và giải Captcha trên cửa sổ trình duyệt.")
    print("2. Sau khi đăng nhập thành công, quay lại terminal và nhấn ENTER để bắt đầu quét.")
    print("=" * 50)

    # VN: Lắng nghe mọi response để bắt đúng payload class-registration khi nó đi qua.
    # EN: Listen to every response so we can catch the class-registration payload when it passes by.
    # JP: すべてのレスポンスを監視し、class-registration のペイロードを通過時に確実に捕捉します。
    page.on("response", lambda response: process_class_registration_response(response, teacher_mapping))
    page.goto(CLASS_REGISTRATION_URL)

    # VN: Đợi người dùng xác nhận xong đăng nhập trước khi tiếp tục các bước thu dữ liệu.
    # EN: Wait for the user to confirm login before continuing the data-collection steps.
    # JP: データ収集を続ける前に、ユーザーがログイン完了を確認するのを待ちます。
    input("\n>>> [CHỜ XÁC NHẬN] Nhấn ENTER sau khi bạn đã vào trang đăng ký... <<<")

    try:
        # VN: Course-members và timetable được lấy tuần tự để dễ debug từng nguồn dữ liệu.
        # EN: Course-members and timetable are fetched sequentially so each source is easier to debug.
        # JP: course-members と timetable は順番に取得し、各データ源を個別にデバッグしやすくします。
        fetch_and_save_student_course_members(page)
    except Exception as error:
        print(f"Không lấy được dữ liệu course-members: {error}")

    try:
        # VN: Lấy thêm timetable để tăng khả năng thu thập đủ cặp id-name từ nhiều nguồn.
        # EN: Fetch timetable as well to increase the chance of collecting enough id-name pairs from multiple sources.
        # JP: timetable も取得して、複数ソースから id-名前ペアをより多く収集できるようにします。
        fetch_and_save_student_timetable(page)
    except Exception as error:
        print(f"Không lấy được dữ liệu timetable: {error}")

    # VN: Hợp nhất các file mapping phụ vào teacher mapping hiện có mà không ghi đè lên dữ liệu đã biết trước đó.
    # EN: Merge auxiliary mapping files into the existing teacher mapping without overwriting known data.
    # JP: 補助的なマッピングファイルを既存の教員マッピングへ統合し、既知データは上書きしません。
    merge_person_files_into_mapping(
        teacher_mapping,
        str(STUDENT_COURSE_MEMBERS_PERSON_MAP_FILE),
        str(STUDENT_TIMETABLE_PERSON_MAP_FILE),
    )

    try:
        # VN: Sau khi đã lấy đủ dữ liệu, giữ vòng lặp reload để tiếp tục nghe response mới từ trang đăng ký trong suốt thời gian phiên làm việc còn mở.
        # EN: After the main data is collected, keep reloading so the program continues listening for new responses while the session stays open.
        # JP: 主要データを取得した後は、セッションが開いている限り再読み込みを続け、新しいレスポンスを監視し続けます。
        while True:
            page.goto(CLASS_REGISTRATION_URL)
            page.wait_for_timeout(5000)
    except Exception as error:
        print(f"\nDừng chương trình: {error}")
    finally:
        # VN: Đóng browser để giải phóng tài nguyên dù luồng kết thúc bình thường hay lỗi.
        # EN: Close the browser to release resources whether the flow ends normally or with an error.
        # JP: 正常終了でも異常終了でも、リソース解放のためにブラウザを閉じます。
        browser.close()
