from typing import Any

from src.services.person_extractor.to_string_id import to_string_id


def add_person_pair(result_set: set[tuple[str, str]], person_id: Any, person_name: Any) -> None:
    """Thêm cặp id-name nếu hợp lệ."""
    normalized_id = to_string_id(person_id)
    if not normalized_id:
        return
    if not isinstance(person_name, str):
        return
    normalized_name = person_name.strip()
    if not normalized_name:
        return
    result_set.add((normalized_id, normalized_name))
