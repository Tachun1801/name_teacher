"""VN: Thêm cặp id-name đã chuẩn hóa vào tập kết quả.
EN: Add a normalized id-name pair to the result set.
JP: 正規化済みの id-名前ペアを結果セットへ追加します。
"""

from typing import Any

from src.services.person_extractor.to_string_id import to_string_id


def add_person_pair(result_set: set[tuple[str, str]], person_id: Any, person_name: Any) -> None:
    """VN: Thêm cặp id-name nếu hợp lệ.
    EN: Add an id-name pair only when it is valid.
    JP: 妥当な場合にのみ id-名前ペアを追加します。
    """
    # VN: Bước đầu tiên là chuẩn hóa id sang chuỗi; nếu không chuẩn hóa được thì bỏ qua luôn.
    # EN: First normalize the id into a string; if that fails, skip the record.
    # JP: まず id を文字列に正規化し、失敗したらそのレコードをスキップします。
    normalized_id = to_string_id(person_id)
    if not normalized_id:
        return
    # VN: Chỉ chấp nhận tên dạng chuỗi; các kiểu khác thường là dữ liệu lỗi hoặc không mong muốn.
    # EN: Accept only string names; other types are usually invalid or unwanted data.
    # JP: 名前は文字列だけを受け付け、それ以外は通常エラー値か不要なデータです。
    if not isinstance(person_name, str):
        return
    normalized_name = person_name.strip()
    # VN: Tên trống sau khi trim thì không mang ý nghĩa để đưa vào mapping.
    # EN: A name that becomes empty after trimming is not useful for the mapping.
    # JP: trim 後に空になる名前は、マッピングに入れる意味がありません。
    if not normalized_name:
        return
    # VN: Set giúp tự động loại bỏ trùng lặp giữa các nguồn dữ liệu khác nhau.
    # EN: A set automatically removes duplicates across different data sources.
    # JP: set を使うことで、異なるデータソース間の重複を自動で除去できます。
    result_set.add((normalized_id, normalized_name))
