"""VN: Chuẩn hóa giá trị id về chuỗi để dùng làm khóa mapping.
EN: Normalize id values into strings for mapping keys.
JP: id の値をマッピング用の文字列に正規化します。
"""

from typing import Any


def to_string_id(value: Any) -> str | None:
    """VN: Chuẩn hóa id về chuỗi, bỏ qua id rỗng/không hợp lệ.
    EN: Normalize ids into strings and ignore empty or invalid ids.
    JP: id を文字列へ正規化し、空または不正な id は無視します。
    """
    # VN: None và bool không phải id hợp lệ trong ngữ cảnh này.
    # EN: None and bool are not valid ids in this context.
    # JP: この文脈では None と bool は有効な id ではありません。
    if value is None or isinstance(value, bool):
        return None
    # VN: Số được ép sang chuỗi số nguyên để tránh dạng 123.0 làm hỏng khóa mapping.
    # EN: Numeric values are converted to integer strings so values like 123.0 do not break the mapping key.
    # JP: 数値は整数文字列に変換し、123.0 のような表現でキーが壊れないようにします。
    if isinstance(value, (int, float)):
        return str(int(value))
    # VN: String thì chỉ trim khoảng trắng thừa, giữ nguyên nội dung thực tế.
    # EN: Strings are only trimmed; the actual content is preserved.
    # JP: 文字列は余分な空白だけを削り、内容そのものは保持します。
    if isinstance(value, str):
        normalized = value.strip()
        return normalized if normalized else None
    # VN: Mọi kiểu khác đều bị loại để tránh đưa object lạ vào mapping.
    # EN: All other types are rejected to avoid placing unexpected objects into the mapping.
    # JP: それ以外の型は、想定外のオブジェクトがマッピングに入らないよう除外します。
    return None
