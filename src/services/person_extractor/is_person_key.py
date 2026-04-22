"""VN: Kiểm tra một key có khả năng chứa thông tin người hay không.
EN: Check whether a key likely contains person-related information.
JP: そのキーが人物情報を含む可能性があるかを判定します。
"""

from src.services.person_extractor.constants import PERSON_EXCLUDE_HINTS, PERSON_KEY_HINTS


def is_person_key(key_name: str) -> bool:
    """VN: Nhận diện key có khả năng chứa tên người.
    EN: Detect whether a key is likely to contain person-related data.
    JP: そのキーが人物関連データを含む可能性があるかを判定します。
    """
    # VN: So sánh trên bản lowercase để tránh phụ thuộc vào cách viết hoa của API.
    # EN: Compare in lowercase so the result does not depend on the API's capitalization style.
    # JP: API の大文字小文字の違いに依存しないよう、lowercase で比較します。
    lower_key = key_name.lower()
    # VN: Loại bỏ sớm các key rõ ràng thuộc về course/class/department thay vì người.
    # EN: Exclude obvious course/class/department keys early because they are not person data.
    # JP: course/class/department など明らかに人物でないキーは早めに除外します。
    if any(part in lower_key for part in PERSON_EXCLUDE_HINTS):
        return False
    # VN: Chỉ cần một hint phù hợp là coi key đó có khả năng chứa thông tin người.
    # EN: A single matching hint is enough to treat the key as person-related.
    # JP: 1つでも一致するヒントがあれば、人物関連のキーとして扱います。
    return any(part in lower_key for part in PERSON_KEY_HINTS)
