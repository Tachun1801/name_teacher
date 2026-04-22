"""VN: Các gợi ý key để nhận diện dữ liệu người trong JSON.
EN: Key hints used to detect person-related data in JSON.
JP: JSON 内の人物関連データを見つけるためのキー候補です。
"""

PERSON_KEY_HINTS = ("student", "teacher", "staff", "coord", "assistant", "supervisor", "advisor", "full")
PERSON_EXCLUDE_HINTS = ("course", "class", "program", "department", "school", "root", "major", "semester", "group")
