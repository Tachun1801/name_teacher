import json
from typing import Any

from src.services.person_extractor.add_person_pair import add_person_pair
from src.services.person_extractor.is_person_key import is_person_key
from src.services.person_extractor.split_names import split_names


def collect_person_pairs_from_dict(obj: dict[str, Any], result_set: set[tuple[str, str]]) -> None:
    """Thu thập cặp id-name từ các pattern key thường gặp trong dữ liệu."""
    lowered_keys = {key.lower(): key for key in obj.keys()}

    for lower_key, original_key in lowered_keys.items():
        if lower_key.endswith("name") and is_person_key(lower_key):
            stem = lower_key[:-4]
            id_key = lowered_keys.get(stem + "id")
            if id_key:
                id_value = obj.get(id_key)
                for person_name in split_names(obj.get(original_key)):
                    add_person_pair(result_set, id_value, person_name)

    for lower_key, original_key in lowered_keys.items():
        if lower_key.endswith("names") and is_person_key(lower_key):
            stem = lower_key[:-5]
            ids_key = lowered_keys.get(stem + "ids")
            if not ids_key:
                continue
            names_value = obj.get(original_key)
            ids_value = obj.get(ids_key)
            if isinstance(names_value, list) and isinstance(ids_value, list):
                for index in range(min(len(names_value), len(ids_value))):
                    current_names = split_names(names_value[index])
                    if not current_names and isinstance(names_value[index], str):
                        current_names = [names_value[index].strip()]
                    for person_name in current_names:
                        add_person_pair(result_set, ids_value[index], person_name)

    if "id" in lowered_keys and "fullname" in lowered_keys:
        for person_name in split_names(obj.get(lowered_keys["fullname"])):
            add_person_pair(result_set, obj.get(lowered_keys["id"]), person_name)

    if "gradelogs" in lowered_keys and isinstance(obj.get(lowered_keys["gradelogs"]), list):
        for item in obj.get(lowered_keys["gradelogs"]):
            if isinstance(item, str) and "staffName" in item and "staffId" in item:
                try:
                    parsed_item = json.loads(item)
                    for person_name in split_names(parsed_item.get("staffName")):
                        add_person_pair(result_set, parsed_item.get("staffId"), person_name)
                except Exception:
                    continue
