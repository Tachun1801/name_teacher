"""VN: Lọc dữ liệu nguồn và ghi ra file mapping id -> tên.
EN: Filter source data and write an id-to-name mapping file.
JP: 元データを絞り込み、id から名前へのマッピングを書き出します。
"""

import json

from src.services.person_extractor.walk_and_collect_person_pairs import walk_and_collect_person_pairs


def save_person_id_name_file(input_file: str, output_file: str) -> None:
    """VN: Đọc file JSON nguồn và sinh file mapping id->name giống teacher cache.
    EN: Read the source JSON file and generate an id-to-name mapping like the teacher cache.
    JP: 元の JSON ファイルを読み込み、教員キャッシュと同様の id-名前マッピングを生成します。
    """
    with open(input_file, "r", encoding="utf-8") as source_file:
        source_data = json.load(source_file)

    pairs_set: set[tuple[str, str]] = set()
    walk_and_collect_person_pairs(source_data, pairs_set)

    id_to_name: dict[str, str] = {}
    conflict_count = 0
    skipped_unknown_id = 0

    for person_id, person_name in sorted(pairs_set, key=lambda pair: (pair[0], pair[1].lower())):
        if person_id == "-1":
            skipped_unknown_id += 1
            continue

        existing_name = id_to_name.get(person_id)
        if existing_name is None:
            id_to_name[person_id] = person_name
        elif existing_name != person_name:
            conflict_count += 1

    id_to_name = dict(sorted(id_to_name.items(), key=lambda item: item[1].lower()))

    with open(output_file, "w", encoding="utf-8") as destination_file:
        json.dump(id_to_name, destination_file, ensure_ascii=False, indent=4)

    print(
        f"--- Đã lọc và lưu {len(id_to_name)} cặp id->name vào {output_file} "
        f"(bỏ qua {skipped_unknown_id} bản ghi id=-1, xung đột id: {conflict_count}) ---"
    )
