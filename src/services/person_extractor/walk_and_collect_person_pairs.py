from typing import Any

from src.services.person_extractor.collect_person_pairs_from_dict import collect_person_pairs_from_dict


def walk_and_collect_person_pairs(data: Any, result_set: set[tuple[str, str]]) -> None:
    """Duyệt đệ quy toàn bộ JSON để thu thập cặp id-name."""
    if isinstance(data, dict):
        collect_person_pairs_from_dict(data, result_set)
        for value in data.values():
            walk_and_collect_person_pairs(value, result_set)
    elif isinstance(data, list):
        for item in data:
            walk_and_collect_person_pairs(item, result_set)
