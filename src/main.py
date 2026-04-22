"""VN: Tập trung luồng chạy chính của chương trình.
EN: Central place for the main execution flow.
JP: プログラムの主要な実行フローをまとめる場所です。
"""

from pathlib import Path
import sys

from playwright.sync_api import sync_playwright

if __package__ is None or __package__ == "":
    # VN: Cho phép chạy trực tiếp bằng `python src/main.py`.
    # EN: Allow direct execution via `python src/main.py`.
    # JP: `python src/main.py` で直接実行できるようにします。
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config import TEACHER_DIRECTORY_CACHE_FILE, ensure_output_directories
from src.services.browser.run_automation import run_automation
from src.services.teacher_mapping.get_teacher_mapping import get_teacher_mapping


def main() -> None:
    # VN: Tạo sẵn các thư mục output để các bước ghi file phía sau không phải tự kiểm tra từng thư mục một.
    # EN: Pre-create output folders so later file-writing steps do not need to check each directory individually.
    # JP: 後続の書き込み処理が各ディレクトリを個別確認しなくて済むよう、出力フォルダを先に作成します。
    ensure_output_directories()

    # VN: Teacher mapping là dữ liệu nền quan trọng nhất, nên load nó trước khi khởi động Playwright để luồng chạy chính luôn có sẵn lookup table.
    # EN: The teacher mapping is the core reference data, so load it before starting Playwright and keep the main flow ready with a lookup table.
    # JP: 教員マッピングは最重要の基盤データなので、Playwright を起動する前に読み込み、主処理で参照できる状態にします。
    teacher_mapping = get_teacher_mapping(str(TEACHER_DIRECTORY_CACHE_FILE))

    # VN: Playwright được mở ở đây để gom toàn bộ thao tác trình duyệt vào một vòng đời rõ ràng, dễ đóng lại khi chương trình kết thúc.
    # EN: Playwright is opened here so all browser operations stay inside one clear lifecycle that is easy to close at the end.
    # JP: ここで Playwright を開き、ブラウザ操作全体を明確なライフサイクルにまとめて、終了時に確実に閉じやすくします。
    with sync_playwright() as playwright:
        run_automation(playwright, teacher_mapping)
