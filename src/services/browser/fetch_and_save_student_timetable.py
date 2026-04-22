"""VN: Vào trang timetable, chờ API và lưu dữ liệu thô.
EN: Open timetable, wait for the API, and save the raw data.
JP: timetable 画面を開き、API を待って生データを保存します。
"""

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
    """VN: Vào timetable, chờ API query-student-timetable-in-range và lưu JSON.
    EN: Open timetable, wait for the query-student-timetable-in-range API, and save the JSON.
    JP: timetable を開き、query-student-timetable-in-range API を待って JSON を保存します。
    """
    print("\n--- Đang vào timetable để lấy dữ liệu student_timetable... ---")
    response = None

    for attempt in range(2):
        try:
            # VN: Chỉ bắt response của API timetable, tránh nhầm với các request phụ của trang.
            # EN: Capture only the timetable API response so we do not confuse it with auxiliary page requests.
            # JP: timetable API のレスポンスだけを捕捉し、ページの補助リクエストと混同しないようにします。
            with page.expect_response(
                lambda res: (
                    STUDENT_TIMETABLE_API_PART in res.url
                    and res.request.method.upper() == "POST"
                ),
                timeout=timeout_ms,
            ) as response_info:
                # VN: Lần đầu đi tới trang, lần thứ hai reload để kích hoạt lại request.
                # EN: The first attempt navigates to the page; the second reloads to trigger the request again.
                # JP: 1回目はページへ移動し、2回目は再読み込みでリクエストを再発生させます。
                if attempt == 0:
                    page.goto(TIMETABLE_URL, wait_until="domcontentloaded")
                else:
                    page.reload(wait_until="domcontentloaded")
            response = response_info.value
            break
        except Exception:
            # VN: Nếu fail ở lần đầu thì thử lại một lần trước khi bỏ cuộc.
            # EN: If the first attempt fails, retry once before giving up.
            # JP: 1回目が失敗したら、諦める前にもう一度だけ試します。
            if attempt == 1:
                raise

    # VN: Ghi lại raw timetable response để có dữ liệu đầu vào ổn định cho các bước sau.
    # EN: Store the raw timetable response so downstream steps have a stable input source.
    # JP: 後続処理が安定した入力を使えるように、raw timetable レスポンスを保存します。
    with open(STUDENT_TIMETABLE_RAW_FILE, "w", encoding="utf-8") as output_handle:
        json.dump(response.json(), output_handle, ensure_ascii=False, indent=4)
    print(f"--- Đã lưu dữ liệu vào {STUDENT_TIMETABLE_RAW_FILE} ---")

    try:
        # VN: Từ raw timetable, sinh tiếp file mapping người để merge vào teacher map.
        # EN: From the raw timetable, generate another person mapping file to merge into the teacher map.
        # JP: raw timetable から人物マッピングを生成し、教員マップへ統合できるようにします。
        save_person_id_name_file(
            str(STUDENT_TIMETABLE_RAW_FILE),
            str(STUDENT_TIMETABLE_PERSON_MAP_FILE),
        )
    except Exception as error:
        # VN: Bước này chỉ là bổ trợ nên lỗi ở đây không nên làm dừng luồng chính.
        # EN: This step is only supplementary, so an error here should not stop the main flow.
        # JP: この手順は補助的なものなので、ここで失敗してもメインの流れは止めません。
        print(f"Không lọc được file person map từ timetable: {error}")
