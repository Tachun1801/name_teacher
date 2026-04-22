# Project Structure (English)

## 1) High-level purpose
This project automates data capture from HUST student pages using Playwright, then parses and enriches captured JSON data to print a readable class schedule with teacher names.

## 2) Main directories

- `app.py`
  - Thin launcher. Calls `src.main.main()`.
- `src/`
  - Main source code.
- `data/`
  - Captured and derived JSON data.
- `.venv/`
  - Python virtual environment.
- `docs/`
  - Documentation (this folder).

## 3) Source structure in detail

### `src/main.py`
- `main()`
  - Application orchestrator.
  - Ensures output directories exist.
  - Loads teacher mapping.
  - Starts Playwright and runs browser automation.

### `src/config.py`
- Defines all configuration constants:
  - URLs and API path hints.
  - timeout values.
  - output file paths.
- `ensure_output_directories()`
  - Creates `data/raw`, `data/derived`, `data/cache` if missing.

### `src/services/browser/`
- `run_automation.py`
  - Main browser workflow loop.
- `process_class_registration_response.py`
  - Handles response filtering for class-registration API and triggers schedule rendering.
- `fetch_and_save_student_course_members.py`
  - Captures and saves student course-member response.
  - Also generates a person-id-name map from that response.
- `fetch_and_save_student_timetable.py`
  - Captures and saves student timetable response.
  - Also generates a person-id-name map from that response.

### `src/services/teacher_mapping/`
- `manual_teacher_data.py`
  - Manual teacher ID -> name dictionary.
- `get_teacher_mapping.py`
  - Loads cache, optionally fetches supplemental teacher data from API, merges manual data.
- `merge_person_files_into_mapping.py`
  - Merges derived person maps into the working teacher mapping without overwriting existing keys.

### `src/services/person_extractor/`
- `constants.py`
  - Key-hint constants used to detect person-like fields.
- `is_person_key.py`
  - Checks whether a JSON key likely represents person information.
- `to_string_id.py`
  - Normalizes IDs to safe string format.
- `split_names.py`
  - Splits multi-name values into clean list form.
- `add_person_pair.py`
  - Validates and inserts `(id, name)` pairs into a set.
- `collect_person_pairs_from_dict.py`
  - Extracts person pairs from one dictionary object based on known patterns.
- `walk_and_collect_person_pairs.py`
  - Recursively walks nested JSON structures and collects person pairs.
- `save_person_id_name_file.py`
  - Produces deterministic ID->name mapping JSON from a source JSON file.

### `src/services/schedule_printer.py`
- `extract_hust_schedule_final()`
  - Reads class-registration JSON.
  - Aggregates classes/calendars.
  - Prints formatted schedule and total credits.

## 4) Data directory layout

### `data/raw/`
Raw API responses captured from website traffic:
- `class_registration_response.json`
- `student_course_members_response.json`
- `student_timetable_response.json`

### `data/derived/`
Generated mappings extracted from raw data:
- `student_course_members_person_map.json`
- `student_timetable_person_map.json`

### `data/cache/`
Persisted cache used to speed up startup and reduce repeated API fetching:
- `teacher_directory_cache.json`

## 5) Runtime relationship summary

1. Entry: `app.py` -> `src/main.py`.
2. Config creates output folders.
3. Teacher map is loaded and enriched.
4. Browser automation captures required API responses.
5. Raw data is written under `data/raw`.
6. Person maps are generated to `data/derived`.
7. Mappings are merged.
8. Class-registration responses trigger schedule parsing and terminal rendering.
