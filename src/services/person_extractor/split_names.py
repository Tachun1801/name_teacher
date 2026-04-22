from typing import Any


def split_names(value: Any) -> list[str]:
    """Tách tên khi chuỗi có nhiều người ngăn cách bởi dấu phẩy."""
    names: list[str] = []
    if isinstance(value, str):
        names = [part.strip() for part in value.split(",") if part.strip()]
    elif isinstance(value, list):
        for item in value:
            if isinstance(item, str):
                names.extend([part.strip() for part in item.split(",") if part.strip()])
    return names
