import json
import os

import requests

from src.services.teacher_mapping.manual_teacher_data import MANUAL_TEACHER_DATA


def get_teacher_mapping(cache_file: str) -> dict[str, str]:
    """Lấy danh sách giảng viên và hợp nhất với dữ liệu nhập tay."""
    teacher_map: dict[str, str] = {}

    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as cache_handle:
                teacher_map = json.load(cache_handle)
        except Exception as error:
            print(f"Lỗi đọc file cache: {error}")

    if len(teacher_map) < 700:
        url = "https://student.hust.edu.vn/api/v1/projects/project-topics/query"
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }
        root_ids = [
            6170508018057217,
            6234759713783809,
            5606644603944960,
            5107078788022273,
            4618805103820801,
            4560738412658689,
            6534081428848641,
            4836798626791424,
            4767095241834497,
            5058924227067905,
            5043694650523648,
            4759934910595073,
        ]

        print("--- Đang tải bổ sung dữ liệu giảng viên từ API... ---")
        for root_id in root_ids:
            payload = {
                "rootId": root_id,
                "unitIds": [],
                "supervisorIds": None,
                "limited": False,
                "majorId": -1,
                "projectFrom": 1,
            }
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    for item in data.get("data", []):
                        teacher_id = str(item.get("teacherId"))
                        teacher_name = item.get("teacherName")
                        if teacher_id and teacher_name:
                            teacher_map[teacher_id] = teacher_name
            except Exception:
                continue

        try:
            with open(cache_file, "w", encoding="utf-8") as cache_handle:
                json.dump(teacher_map, cache_handle, ensure_ascii=False, indent=4)
        except Exception as error:
            print(f"Không thể lưu file cache: {error}")

    teacher_map.update(MANUAL_TEACHER_DATA)

    print(
        f"--- Tổng cộng: {len(teacher_map)} giảng viên "
        f"(đã bao gồm {len(MANUAL_TEACHER_DATA)} người nhập tay). ---"
    )
    return teacher_map
