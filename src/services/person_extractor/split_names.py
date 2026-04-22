"""VN: Tách chuỗi tên có nhiều người thành danh sách tên riêng lẻ.
EN: Split a multi-person name string into individual names.
JP: 複数人の名前文字列を個別の名前リストに分割します。
"""

from typing import Any


def split_names(value: Any) -> list[str]:
    """VN: Tách tên khi chuỗi có nhiều người ngăn cách bởi dấu phẩy.
    EN: Split names when a string contains multiple people separated by commas.
    JP: カンマ区切りで複数人が入っている文字列を名前ごとに分割します。
    """
    names: list[str] = []
    if isinstance(value, str):
        # VN: Đây là trường hợp phổ biến nhất: một chuỗi chứa nhiều tên ngăn bởi dấu phẩy.
        # EN: This is the most common case: a single string containing multiple comma-separated names.
        # JP: 最も一般的なのは、カンマ区切りで複数の名前が入った1つの文字列です。
        names = [part.strip() for part in value.split(",") if part.strip()]
    elif isinstance(value, list):
        # VN: Một số payload đã trả list, nhưng từng phần tử vẫn có thể chứa nhiều tên.
        # EN: Some payloads already return a list, but each item may still contain multiple names.
        # JP: すでに list で返る payload もありますが、各要素に複数の名前が入っていることがあります。
        for item in value:
            if isinstance(item, str):
                names.extend([part.strip() for part in item.split(",") if part.strip()])
    return names
