import json
import os


def merge_person_files_into_mapping(teacher_mapping: dict[str, str], *json_files: str) -> None:
    """Bổ sung các file person id-name vào mapping hiện có (không ghi đè)."""
    total_added = 0
    for filepath in json_files:
        if not os.path.exists(filepath):
            continue
        try:
            with open(filepath, "r", encoding="utf-8") as mapping_handle:
                persons = json.load(mapping_handle)
            added = 0
            for person_id, person_name in persons.items():
                if person_id not in teacher_mapping:
                    teacher_mapping[person_id] = person_name
                    added += 1
            print(f"--- [{filepath}] Bổ sung {added}/{len(persons)} bản ghi mới ---")
            total_added += added
        except Exception as error:
            print(f"Không đọc được {filepath}: {error}")
    print(f"--- Tổng cộng sau merge: {len(teacher_mapping)} giảng viên ---")
