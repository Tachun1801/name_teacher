"""VN: Vào personal-transcript, chờ API và lưu dữ liệu thô.
EN: Open personal-transcript, wait for the API, and save the raw data.
JP: personal-transcript を開き、API を待って生データを保存します。
"""

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
    """VN: Vào personal-transcript, chờ API student-course-members và lưu JSON.
    EN: Open personal-transcript, wait for the student-course-members API, and save the JSON.
    JP: personal-transcript を開き、student-course-members API を待って JSON を保存します。
    """
    print("\n--- Đang vào personal-transcript để lấy dữ liệu student_course_members... ---")
    response = None

    for attempt in range(2):
        try:
            # VN: `expect_response` giúp chặn đúng response cần lấy thay vì phải polling thủ công.
            # EN: `expect_response` captures the exact response we need instead of polling manually.
            # JP: `expect_response` を使うと、手動ポーリングせずに必要なレスポンスを正確に捕捉できます。
            with page.expect_response(
                lambda res: (
                    STUDENT_COURSE_MEMBERS_API_PART in res.url
                    and res.request.method.upper() == "GET"
                ),
                timeout=timeout_ms,
            ) as response_info:
                # VN: Lần đầu thì đi thẳng tới trang đích, lần sau reload để kích hoạt lại request.
                # EN: The first attempt goes directly to the target page; the second attempt reloads to trigger the request again.
                # JP: 1回目は対象ページへ直接移動し、2回目は再読み込みしてリクエストを再発生させます。
                if attempt == 0:
                    page.goto(PERSONAL_TRANSCRIPT_URL, wait_until="domcontentloaded")
                else:
                    page.reload(wait_until="domcontentloaded")
            response = response_info.value
            break
        except Exception:
            # VN: Chỉ ném lỗi sau khi thử cả 2 lần; cách này cho phép retry nhẹ khi mạng chậm.
            # EN: Raise only after both attempts fail; this gives a light retry in case the network is slow.
            # JP: 2回試してから失敗を投げることで、通信が遅い場合の軽いリトライになります。
            if attempt == 1:
                raise

    # VN: Lưu raw response để nếu downstream lỗi thì vẫn còn nguồn gốc ban đầu để kiểm tra.
    # EN: Save the raw response so the original source remains available if downstream processing fails.
    # JP: downstream の処理が失敗しても、元データを確認できるように生レスポンスを保存します。
    with open(STUDENT_COURSE_MEMBERS_RAW_FILE, "w", encoding="utf-8") as output_handle:
        json.dump(response.json(), output_handle, ensure_ascii=False, indent=4)
    print(f"--- Đã lưu dữ liệu vào {STUDENT_COURSE_MEMBERS_RAW_FILE} ---")

    try:
        # VN: Sinh thêm file mapping id-name từ raw data để phục vụ bước merge về sau.
        # EN: Generate an extra id-name mapping file from the raw data for later merge steps.
        # JP: 後続の merge 処理のために、raw データから id-名前マッピングを生成します。
        save_person_id_name_file(
            str(STUDENT_COURSE_MEMBERS_RAW_FILE),
            str(STUDENT_COURSE_MEMBERS_PERSON_MAP_FILE),
        )
    except Exception as error:
        # VN: Không chặn luồng chính nếu bước trích xuất phụ này lỗi.
        # EN: Do not block the main flow if this auxiliary extraction step fails.
        # JP: この補助的な抽出処理が失敗しても、メインの流れは止めません。
        print(f"Không lọc được file person map từ course-members: {error}")
