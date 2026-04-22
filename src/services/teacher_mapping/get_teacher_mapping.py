"""VN: Tải, cache, và bổ sung danh sách giảng viên.
EN: Load, cache, and enrich the teacher list.
JP: 教員一覧を読み込み、キャッシュし、補完します。
"""

import json
import os

import requests

from src.services.teacher_mapping.manual_teacher_data import MANUAL_TEACHER_DATA


def get_teacher_mapping(cache_file: str) -> dict[str, str]:
    """VN: Lấy danh sách giảng viên và hợp nhất với dữ liệu nhập tay.
    EN: Load the teacher list and merge it with manually curated data.
    JP: 教員一覧を取得し、手入力データと統合します。
    """
    teacher_map: dict[str, str] = {}

    # VN: Ưu tiên dùng cache local trước để giảm số request mạng khi chương trình chạy nhiều lần liên tiếp.
    # EN: Prefer the local cache first to reduce network requests when the program runs repeatedly.
    # JP: 何度も実行する際のネットワークリクエストを減らすため、まずローカルキャッシュを優先します。
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as cache_handle:
                teacher_map = json.load(cache_handle)
        except Exception as error:
            print(f"Lỗi đọc file cache: {error}")

    # VN: Nếu cache còn quá ít dữ liệu thì coi như cache chưa đủ tin cậy và tải bổ sung từ API.
    # EN: If the cache still contains too little data, treat it as unreliable and fetch more from the API.
    # JP: キャッシュの件数が少なすぎる場合は信頼性が低いとみなし、API から補完取得します。
    if len(teacher_map) < 700:
        # VN: Endpoint này cung cấp dữ liệu giảng viên theo từng nhóm root_id.
        # EN: This endpoint provides teacher data grouped by root_id.
        # JP: このエンドポイントは root_id ごとに教員データを返します。
        url = "https://student.hust.edu.vn/api/v1/projects/project-topics/query"
        # VN: Header mô phỏng trình duyệt thật để giảm rủi ro bị chặn hoặc trả response bất thường.
        # EN: The headers mimic a real browser to reduce the risk of blocking or unusual responses.
        # JP: ヘッダーは実ブラウザを模倣し、ブロックや不自然なレスポンスのリスクを下げます。
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }
        # VN: Các root id được hard-code vì nguồn API hiện tại cần quét theo từng nhánh dữ liệu.
        # EN: The root ids are hard-coded because the current API source must be scanned branch by branch.
        # JP: 現在の API はデータ分岐ごとに走査する必要があるため、root_id を固定値で持っています。
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
            # VN: Payload giữ các trường tối thiểu để API trả về danh sách cần thiết.
            # EN: The payload keeps only the minimum fields required for the API to return the needed list.
            # JP: 必要な一覧を返させるため、payload は最小限の項目だけを送ります。
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
                    # VN: Ghi đè theo teacher_id vì cùng một id có thể xuất hiện nhiều lần, còn giá trị cuối cùng vẫn là tên cần hiển thị.
                    # EN: Overwrite by teacher_id because the same id may appear multiple times, and the final value is still the display name we want.
                    # JP: 同じ id が複数回出る可能性があるため teacher_id で上書きし、最終的な表示名を採用します。
                    for item in data.get("data", []):
                        teacher_id = str(item.get("teacherId"))
                        teacher_name = item.get("teacherName")
                        if teacher_id and teacher_name:
                            teacher_map[teacher_id] = teacher_name
            except Exception:
                # VN: Một root_id lỗi không được làm hỏng toàn bộ quá trình nạp dữ liệu.
                # EN: A failing root_id should not break the entire data-loading process.
                # JP: 1つの root_id が失敗しても、全体のデータ取得は止めません。
                continue

        try:
            # VN: Lưu cache sau khi nạp từ API để lần chạy sau không phải gọi lại toàn bộ.
            # EN: Save the cache after loading from the API so the next run does not need to fetch everything again.
            # JP: API 取得後にキャッシュを保存し、次回実行時に全件再取得しなくて済むようにします。
            with open(cache_file, "w", encoding="utf-8") as cache_handle:
                json.dump(teacher_map, cache_handle, ensure_ascii=False, indent=4)
        except Exception as error:
            print(f"Không thể lưu file cache: {error}")

    # VN: Dữ liệu nhập tay được áp sau cùng để đảm bảo các bản ghi đặc biệt luôn có mặt.
    # EN: Manually curated data is applied last so special records are always present.
    # JP: 特殊なレコードを必ず含めるため、手入力データは最後に適用します。
    teacher_map.update(MANUAL_TEACHER_DATA)

    # VN: In tổng quan cuối cùng để người chạy biết mapping đã đủ lớn đến mức nào.
    # EN: Print a final summary so the user can see how large the mapping has become.
    # JP: 最後に概要を表示し、マッピングの規模を把握できるようにします。
    print(
        f"--- Tổng cộng: {len(teacher_map)} giảng viên "
        f"(đã bao gồm {len(MANUAL_TEACHER_DATA)} người nhập tay). ---"
    )
    return teacher_map
