# Runtime Behavior and Detailed Flow (English)

## 1) End-to-end goal
The runtime pipeline continuously listens for the class-registration response, updates local JSON snapshots, extracts person mappings, and prints a teacher-resolved schedule in terminal output.

## 2) Startup phase

1. User runs `python app.py` (or `python src/main.py`).
2. `app.py` delegates execution to `src.main.main()`.
3. `main()` calls `ensure_output_directories()`.
4. `main()` loads teacher mapping by calling `get_teacher_mapping(cache_file)`:
   - read cache from `data/cache/teacher_directory_cache.json` if exists.
   - if cache is small, fetch additional teachers from remote API.
   - merge `MANUAL_TEACHER_DATA` as final override layer.
5. `main()` opens Playwright context and invokes `run_automation(playwright, teacher_mapping)`.

## 3) Browser automation lifecycle

Inside `run_automation()`:

1. Launch Chromium with `headless=False`.
2. Create browser context and page.
3. Register response handler:
   - each response is passed to `process_class_registration_response(response, teacher_mapping)`.
4. Navigate to class registration page.
5. Wait for user confirmation (manual login/captcha done).

## 4) Class-registration response handling

`process_class_registration_response()` behavior:

1. Ignore response unless URL contains `TARGET_URL_PART`.
2. Parse JSON and save to `data/raw/class_registration_response.json`.
3. Clear terminal screen.
4. Call `extract_hust_schedule_final()` to parse and print schedule:
   - parse class/course/calendar blocks.
   - resolve teacher IDs via `teacher_mapping`.
   - sort sessions by day/session/period.
   - print readable schedule and credit total.

This handler runs repeatedly whenever relevant responses appear.

## 5) One-time data capture after login confirmation

Still in `run_automation()` after ENTER:

1. Call `fetch_and_save_student_course_members(page)`:
   - navigate to personal transcript page.
   - wait for GET response matching `STUDENT_COURSE_MEMBERS_API_PART`.
   - save full response to `data/raw/student_course_members_response.json`.
   - call `save_person_id_name_file()` to create
     `data/derived/student_course_members_person_map.json`.

2. Call `fetch_and_save_student_timetable(page)`:
   - navigate to timetable page.
   - wait for POST response matching `STUDENT_TIMETABLE_API_PART`.
   - save full response to `data/raw/student_timetable_response.json`.
   - call `save_person_id_name_file()` to create
     `data/derived/student_timetable_person_map.json`.

3. Merge new person maps into in-memory teacher mapping with
   `merge_person_files_into_mapping(...)`.

## 6) Person map extraction mechanics

`save_person_id_name_file(input_file, output_file)` pipeline:

1. Load source JSON.
2. Recursively traverse all objects/lists (`walk_and_collect_person_pairs`).
3. For each dict, detect known person patterns (`collect_person_pairs_from_dict`):
   - `<prefix>Id + <prefix>Name`
   - `<prefix>Ids + <prefix>Names`
   - `id + fullName`
   - `gradeLogs` entries containing serialized `staffId + staffName`
4. Normalize and validate IDs/names.
5. Skip invalid and unknown id `-1`.
6. Resolve conflicts deterministically (first valid name kept).
7. Sort and write final ID->name JSON.

## 7) Continuous refresh loop

After initial setup, `run_automation()` loops forever:

1. Re-open class registration page every 5 seconds.
2. Response handler keeps listening and re-rendering schedule when new target responses arrive.
3. Browser closes only when loop exits due to exception/termination.

## 8) Data consistency model

- `data/raw/*` is immutable snapshot style (latest overwrite by filename).
- `data/derived/*` is deterministic extraction from corresponding raw files.
- `teacher_mapping` in memory is composed from:
  1) cached/API teacher list,
  2) manual overrides,
  3) merged runtime person maps.

## 9) Error tolerance

- Most network capture steps are wrapped in retry (2 attempts for expected response wait).
- Parsing/IO failures are caught and logged, allowing process continuation in many cases.
- Missing fields fallback to defaults, so schedule rendering stays resilient.
