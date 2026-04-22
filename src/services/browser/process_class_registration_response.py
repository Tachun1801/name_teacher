import json
import os
import time

from src.config import CLASS_REGISTRATION_RAW_FILE, TARGET_URL_PART
from src.services.schedule_printer import extract_hust_schedule_final


def process_class_registration_response(response, teacher_mapping: dict[str, str]) -> None:
    """Lưu phản hồi class-registration và in lại thời khóa biểu nếu trúng API mục tiêu."""
    if TARGET_URL_PART not in response.url:
        return

    try:
        with open(CLASS_REGISTRATION_RAW_FILE, "w", encoding="utf-8") as output_handle:
            json.dump(response.json(), output_handle, ensure_ascii=False, indent=4)

        os.system("cls" if os.name == "nt" else "clear")
        print(f"[!] Đã bắt được dữ liệu mới lúc: {time.strftime('%H:%M:%S')}")
        extract_hust_schedule_final(str(CLASS_REGISTRATION_RAW_FILE), teacher_mapping)
        print("\n...Đang tiếp tục lắng nghe dữ liệu mới...")
    except Exception as error:
        print(f"Lỗi khi parse JSON class-registration: {error}")
