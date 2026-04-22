"""VN: Quét một dict để thu thập các cặp id-name theo nhiều mẫu dữ liệu.
EN: Scan a dict to collect id-name pairs from multiple data shapes.
JP: 複数のデータ形に対応して dict から id-名前ペアを収集します。
"""

import json
from typing import Any

from src.services.person_extractor.add_person_pair import add_person_pair
from src.services.person_extractor.is_person_key import is_person_key
from src.services.person_extractor.split_names import split_names


def collect_person_pairs_from_dict(obj: dict[str, Any], result_set: set[tuple[str, str]]) -> None:
    """VN: Thu thập cặp id-name từ các pattern key thường gặp trong dữ liệu.
    EN: Collect id-name pairs from common key patterns in the data.
    JP: データ内でよく見られるキー形式から、id-名前ペアを収集します。
    """
    # VN: Tạo một view không phân biệt hoa thường cho các key hiện tại.
    # EN: Build a case-insensitive view of the current dictionary keys.
    # JP: 現在の辞書キーを大文字小文字に依存しない形で扱えるようにします。
    # VN: Giữ cả key gốc lẫn key đã lower để tra cứu giá trị mà không mất chính tả ban đầu trong payload.
    # EN: Keep both the original key and the lowered key so values can be looked up without losing the exact spelling from the payload.
    # JP: 元のキーと lower したキーの両方を保持し、payload 内の正確な綴りを失わずに参照できるようにします。
    lowered_keys = {key.lower(): key for key in obj.keys()}

    # VN: Tổng quan: hàm này không cố đoán duy nhất một schema; thay vào đó nó quét nhiều mẫu dữ liệu khác nhau để tăng xác suất lấy đủ cặp id-name.
    # EN: Overall, this function does not assume only one schema; instead it scans multiple data shapes to maximize the chance of collecting complete id-name pairs.
    # JP: この関数は 1 つの schema だけを前提にせず、複数のデータ形を走査して id-名前ペアの取りこぼしを減らします。

    # VN: Pattern 1: các field số ít như `teacherName` đi với `teacherId`.
    # EN: Pattern 1: singular fields such as `teacherName` paired with `teacherId`.
    # JP: Pattern 1: `teacherName` と `teacherId` のような単数系フィールドです。
    # VN: Đây là dạng phổ biến nhất trong raw payload, nên được quét đầu tiên.
    # EN: This is the most common shape in the raw payloads, so we scan for it first.
    # JP: 生ペイロードで最も多い形式なので、最初に確認します。
    for lower_key, original_key in lowered_keys.items():
        if lower_key.endswith("name") and is_person_key(lower_key):
            stem = lower_key[:-4]
            id_key = lowered_keys.get(stem + "id")
            if id_key:
                id_value = obj.get(id_key)
                # VN: Một số API dùng name ở dạng chuỗi ghép nhiều người, nên cần tách trước khi đưa vào set kết quả.
                # EN: Some APIs store multiple people in one name string, so we split it before storing.
                # JP: API によっては 1 つの name 文字列に複数人が入るため、保存前に分割します。
                for person_name in split_names(obj.get(original_key)):
                    add_person_pair(result_set, id_value, person_name)

    # VN: Pattern 2: các field dạng số nhiều như `teacherNames` đi với `teacherIds`.
    # EN: Pattern 2: plural array fields such as `teacherNames` paired with `teacherIds`.
    # JP: Pattern 2: `teacherNames` と `teacherIds` のような複数系配列です。
    # VN: Ta ghép hai mảng theo index vì API thường giữ danh sách tên và danh sách id song song.
    # EN: We align both arrays by index because the API often keeps the name list and the id list in parallel.
    # JP: API は名前一覧と id 一覧を並列で持つことが多いので、index 単 vịで対応付けます。
    for lower_key, original_key in lowered_keys.items():
        if lower_key.endswith("names") and is_person_key(lower_key):
            stem = lower_key[:-5]
            ids_key = lowered_keys.get(stem + "ids")
            if not ids_key:
                continue
            names_value = obj.get(original_key)
            ids_value = obj.get(ids_key)
            if isinstance(names_value, list) and isinstance(ids_value, list):
                # VN: Chỉ ghép tới độ dài ngắn hơn để không index vượt quá dữ liệu khi payload bị thiếu.
                # EN: Only pair up to the shorter list so we never index past the available data when the payload is incomplete.
                # JP: 足りない payload でも範囲外アクセスしないよう、短い方の長さまでだけ対応付けます。
                for index in range(min(len(names_value), len(ids_value))):
                    current_names = split_names(names_value[index])
                    # VN: Một số payload lưu chuỗi thô thay vì chuỗi phân tách bằng dấu phẩy mà split_names có thể xử lý. Giữ lại nhánh dự phòng đó.
                    # EN: Some payloads store a raw string instead of a comma-separated string that split_names can parse, so keep that fallback.
                    # JP: split_names で分割できない生文字列が入ることもあるので、そのフォールバックを残します。
                    if not current_names and isinstance(names_value[index], str):
                        current_names = [names_value[index].strip()]
                    for person_name in current_names:
                        add_person_pair(result_set, ids_value[index], person_name)

    # VN: Pattern 3: một cặp `id` + `fullname` tổng quát.
    # EN: Pattern 3: a generic `id` + `fullname` pair.
    # JP: Pattern 3: 汎用的な `id` + `fullname` の組です。
    # VN: Đây là fallback hẹp hơn cho các record không dùng quy ước đặt tên person-key rõ ràng.
    # EN: This is a narrower fallback for records that do not use the explicit person-key naming convention.
    # JP: これは、明示的な person-key の命名規則を使わないレコード向けの限定的なフォールバックです。
    if "id" in lowered_keys and "fullname" in lowered_keys:
        for person_name in split_names(obj.get(lowered_keys["fullname"])):
            add_person_pair(result_set, obj.get(lowered_keys["id"]), person_name)

    # VN: Pattern 4: JSON chuỗi lồng trong `gradelogs`.
    # EN: Pattern 4: nested JSON strings inside `gradelogs`.
    # JP: Pattern 4: `gradelogs` 内に埋め込まれた JSON 文字列です。
    # VN: Một số entry được lưu dưới dạng JSON đã serialize, nên cần parse trước khi trích staff names.
    # EN: Some entries are stored as serialized JSON, so we decode them before extracting staff names.
    # JP: 一部のエントリはシリアライズ済み JSON として保存されているため、staff 名を取る前にデコードします。
    if "gradelogs" in lowered_keys and isinstance(obj.get(lowered_keys["gradelogs"]), list):
        for item in obj.get(lowered_keys["gradelogs"]):
            # VN: Chỉ thử parse các entry có vẻ là bản ghi staff.
            # EN: Only attempt to parse entries that look like staff records.
            # JP: staff レコードらしいエントリだけを parse します。
            if isinstance(item, str) and "staffName" in item and "staffId" in item:
                try:
                    parsed_item = json.loads(item)
                    # VN: staffName cũng có thể chứa nhiều giá trị, nên dùng lại cùng một quy tắc tách để giữ hành vi nhất quán giữa các pattern.
                    # EN: `staffName` may also contain multiple values, so reuse the same splitting rule to keep behavior consistent across patterns.
                    # JP: `staffName` にも複数値が入ることがあるため、同じ分割ルールを再利用して挙動を揃えます。
                    for person_name in split_names(parsed_item.get("staffName")):
                        add_person_pair(result_set, parsed_item.get("staffId"), person_name)
                except Exception:
                    # VN: JSON lỗi không nên làm dừng việc trích xuất phần còn lại của payload, nên ta bỏ qua lỗi và tiếp tục quét.
                    # EN: Malformed JSON should not stop extraction from the rest of the payload, so we fail softly and keep scanning.
                    # JP: JSON が壊れていても残りの payload の抽出を止めないよう、失敗は握りつぶして継続します。
                    continue
