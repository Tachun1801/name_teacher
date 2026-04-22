import json


def extract_hust_schedule_final(file_path: str, teacher_lookup: dict[str, str]) -> None:
    """Đọc dữ liệu lớp và in thời khóa biểu kèm tên giảng viên."""
    try:
        with open(file_path, "r", encoding="utf-8") as file_handle:
            content = file_handle.read()
            start_idx = content.find("{")
            end_idx = content.rfind("}")
            if start_idx != -1 and end_idx != -1:
                data = json.loads(content[start_idx : end_idx + 1])
            else:
                print("Không tìm thấy định dạng JSON hợp lệ.")
                return
    except Exception as error:
        print(f"Lỗi đọc file: {error}")
        return

    all_sessions: list[dict] = []
    counted_courses = set()
    total_credits = 0

    if "data" in data:
        for item in data["data"]:
            if item.get("processStatus") == 5:
                continue

            course_info = item.get("_course", {})
            credit = course_info.get("credit", 0)
            course_id = item.get("courseId")

            class_info = item.get("_class", {})
            course_name = class_info.get("courseName")
            class_id = item.get("classId")

            teacher_ids = class_info.get("teacherIds", [])
            teacher_names = []
            for teacher_id in teacher_ids:
                name = teacher_lookup.get(str(teacher_id), f"ID:{teacher_id}")
                teacher_names.append(name)

            if course_id not in counted_courses:
                total_credits += credit
                counted_courses.add(course_id)

            calendars = class_info.get("_calendars", [])
            for calendar in calendars:
                day_time = calendar.get("dayTime")
                session_name = "SÁNG" if day_time == 1 else "CHIỀU"

                all_sessions.append(
                    {
                        "day": calendar.get("day"),
                        "from": calendar.get("from"),
                        "to": calendar.get("to"),
                        "room": calendar.get("place"),
                        "week": calendar.get("week"),
                        "name": course_name,
                        "class_id": class_id,
                        "course_id": course_id,
                        "teacher_names": teacher_names,
                        "day_time": day_time,
                        "session_name": session_name,
                    }
                )

    all_sessions.sort(key=lambda item: (item["day"], item["day_time"], item["from"]))

    print(f"\n{' THỜI KHÓA BIỂU HUST (HIỂN THỊ TÊN GIẢNG VIÊN) ':=^70}")
    print(f"Tổng số tín chỉ: {total_credits}")
    print("-" * 70)

    current_day = None
    current_session = None

    for session in all_sessions:
        if session["day"] != current_day:
            day_text = f"THỨ {session['day']}" if session["day"] < 8 else "CHỦ NHẬT"
            print(f"\n==== {day_text} ====")
            current_day = session["day"]
            current_session = None

        if session["day_time"] != current_session:
            print(f"  [{session['session_name']}]")
            current_session = session["day_time"]

        time_slot = f"{session['from']}-{session['to']}"
        teachers_display = ", ".join(session["teacher_names"]) if session["teacher_names"] else "Chưa cập nhật"

        print(f"    > Tiết {time_slot.ljust(6)} | {session['name']} ({session['course_id']})")
        print(
            f"      Phòng: {str(session['room']).ljust(10)} "
            f"| Lớp: {session['class_id']} | GV: {teachers_display}"
        )
