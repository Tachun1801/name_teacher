"""VN: Duyệt đệ quy JSON và gom mọi cặp id-name tìm được.
EN: Recursively walk JSON and gather every id-name pair found.
JP: JSON を再帰的に辿って見つかった id-名前ペアを集めます。
"""

from typing import Any

from src.services.person_extractor.collect_person_pairs_from_dict import collect_person_pairs_from_dict


def walk_and_collect_person_pairs(data: Any, result_set: set[tuple[str, str]]) -> None:
    """VN: Duyệt đệ quy toàn bộ JSON để thu thập cặp id-name.
    EN: Recursively walk the entire JSON tree to collect id-name pairs.
    JP: JSON 全体を再帰的に辿って、id-名前ペアを収集します。
    """
    if isinstance(data, dict):
        # VN: Mỗi dict có thể chứa key mang thông tin người, nên xử lý node hiện tại trước rồi mới tiếp tục đi xuống các nhánh con.
        # EN: Each dict may contain person-related keys, so process the current node before descending into children.
        # JP: 各 dict には人物情報のキーが含まれる可能性があるため、子へ降りる前に現在ノードを処理します。
        collect_person_pairs_from_dict(data, result_set)
        for value in data.values():
            # VN: Duyệt sâu toàn bộ cây JSON để không bỏ lỡ object lồng nhau.
            # EN: Recurse through the entire JSON tree so nested objects are not missed.
            # JP: ネストしたオブジェクトを見逃さないよう、JSON ツリー全体を深く走査します。
            walk_and_collect_person_pairs(value, result_set)
    elif isinstance(data, list):
        # VN: Danh sách cũng có thể chứa dict hoặc list lồng nhau, nên recurse từng phần tử.
        # EN: Lists can also contain nested dicts or lists, so recurse into each item.
        # JP: リストにもネストした dict や list が入るため、各要素ごとに再帰します。
        for item in data:
            walk_and_collect_person_pairs(item, result_set)
