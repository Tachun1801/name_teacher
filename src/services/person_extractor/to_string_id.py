from typing import Any


def to_string_id(value: Any) -> str | None:
    """Chuẩn hóa id về chuỗi, bỏ qua id rỗng/không hợp lệ."""
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return str(int(value))
    if isinstance(value, str):
        normalized = value.strip()
        return normalized if normalized else None
    return None
