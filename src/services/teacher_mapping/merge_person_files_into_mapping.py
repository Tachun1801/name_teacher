"""VN: Gộp các file mapping người vào teacher mapping hiện có.
EN: Merge person mapping files into the existing teacher mapping.
JP: 人物マッピングのファイルを既存の教員マッピングへ統合します。
"""

import json
import os


def merge_person_files_into_mapping(teacher_mapping: dict[str, str], *json_files: str) -> None:
    """VN: Bổ sung các file person id-name vào mapping hiện có (không ghi đè).
    EN: Merge person id-name files into the existing mapping without overwriting.
    JP: 既存のマッピングを上書きせずに、人物 id-名前ファイルを統合します。
    """
    total_added = 0
    for filepath in json_files:
        # VN: File nào không tồn tại thì bỏ qua âm thầm, vì đây là dữ liệu bổ trợ chứ không phải bắt buộc.
        # EN: Silently skip missing files because these are supplemental inputs, not mandatory ones.
        # JP: これらは補助入力なので、存在しないファイルは静かにスキップします。
        if not os.path.exists(filepath):
            continue
        try:
            with open(filepath, "r", encoding="utf-8") as mapping_handle:
                persons = json.load(mapping_handle)
            added = 0
            for person_id, person_name in persons.items():
                # VN: Chỉ thêm khi id chưa có sẵn để tránh làm mất dữ liệu giảng viên đã biết trước đó.
                # EN: Only add entries when the id does not already exist, so previously known teacher data is preserved.
                # JP: 既存の id がある場合は追加せず、すでに知っている教員データを守ります。
                if person_id not in teacher_mapping:
                    teacher_mapping[person_id] = person_name
                    added += 1
            print(f"--- [{filepath}] Bổ sung {added}/{len(persons)} bản ghi mới ---")
            total_added += added
        except Exception as error:
            print(f"Không đọc được {filepath}: {error}")
    # VN: Báo tổng số bản ghi đã merge để dễ kiểm tra mức độ phủ dữ liệu.
    # EN: Report the total mapping size so data coverage is easy to verify.
    # JP: マージ後の総件数を表示し、データの網羅度を確認しやすくします。
    print(f"--- Tổng cộng sau merge: {len(teacher_mapping)} giảng viên ---")
