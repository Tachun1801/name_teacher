from src.services.person_extractor.constants import PERSON_EXCLUDE_HINTS, PERSON_KEY_HINTS


def is_person_key(key_name: str) -> bool:
    """Nhận diện key có khả năng chứa tên người."""
    lower_key = key_name.lower()
    if any(part in lower_key for part in PERSON_EXCLUDE_HINTS):
        return False
    return any(part in lower_key for part in PERSON_KEY_HINTS)
