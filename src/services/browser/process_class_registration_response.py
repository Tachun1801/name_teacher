"""VN: Xử lý phản hồi class-registration và lưu JSON thô.
EN: Handle class-registration responses and persist raw JSON.
JP: class-registration のレスポンスを処理して生JSONを保存します。
"""

import json
import os
import time

from src.config import CLASS_REGISTRATION_RAW_FILE, TARGET_URL_PART
from src.services.schedule_printer import extract_hust_schedule_final


def process_class_registration_response(response, teacher_mapping: dict[str, str]) -> None:
    """VN: Lưu phản hồi class-registration và in lại thời khóa biểu nếu trúng API mục tiêu.
    EN: Save class-registration responses and reprint the timetable when the target API is hit.
    JP: class-registration のレスポンスを保存し、対象 API に一致したら時間割を再表示します。
    """
    # VN: Chỉ xử lý response thuộc đúng API mà ta đang quan tâm, tránh ghi nhầm dữ liệu từ các request khác của trang.
    # EN: Only process the response for the API we care about, so we do not store data from unrelated page requests.
    # JP: 対象の API に一致するレスポンスだけを処理し、別リクエストのデータを誤って保存しないようにします。
    if TARGET_URL_PART not in response.url:
        return

    try:
        # VN: Ghi nguyên payload trả về để có thể inspect lại khi cần debug.
        # EN: Persist the raw payload so it can be inspected again during debugging.
        # JP: デバッグ時に再確認できるよう、生のペイロードをそのまま保存します。
        with open(CLASS_REGISTRATION_RAW_FILE, "w", encoding="utf-8") as output_handle:
            json.dump(response.json(), output_handle, ensure_ascii=False, indent=4)

        # VN: Xóa màn hình để phần timetable mới nhất luôn nằm ở vị trí dễ nhìn nhất.
        # EN: Clear the screen so the newest timetable stays in the most visible place.
        # JP: 画面をクリアして、最新の時間割を見やすい位置に保ちます。
        os.system("cls" if os.name == "nt" else "clear")
        print(f"[!] Đã bắt được dữ liệu mới lúc: {time.strftime('%H:%M:%S')}")

        # VN: In lại thời khóa biểu ngay sau khi nhận dữ liệu mới để người dùng thấy kết quả cập nhật theo thời gian thực.
        # EN: Reprint the timetable immediately after receiving new data so the user sees live updates.
        # JP: 新しいデータを受け取った直後に時間割を再表示し、リアルタイム更新を確認できるようにします。
        extract_hust_schedule_final(str(CLASS_REGISTRATION_RAW_FILE), teacher_mapping)
        print("\n...Đang tiếp tục lắng nghe dữ liệu mới...")
    except Exception as error:
        # VN: Nếu response lỗi hoặc JSON không hợp lệ thì chỉ báo lỗi, không dừng toàn bộ luồng.
        # EN: If the response is invalid or the JSON is malformed, log the error and keep the stream alive.
        # JP: レスポンス異常や JSON 不正の場合でも、エラーを表示するだけで全体の処理は止めません。
        print(f"Lỗi khi parse JSON class-registration: {error}")
