from pathlib import Path
import sys

from playwright.sync_api import sync_playwright

if __package__ is None or __package__ == "":
    # Allow running via `python src/main.py` by adding project root to sys.path.
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config import TEACHER_DIRECTORY_CACHE_FILE, ensure_output_directories
from src.services.browser.run_automation import run_automation
from src.services.teacher_mapping.get_teacher_mapping import get_teacher_mapping


def main() -> None:
    ensure_output_directories()
    teacher_mapping = get_teacher_mapping(str(TEACHER_DIRECTORY_CACHE_FILE))

    with sync_playwright() as playwright:
        run_automation(playwright, teacher_mapping)
