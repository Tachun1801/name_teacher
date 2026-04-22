import json  # Dùng để đọc/ghi và parse dữ liệu JSON.
import time  # Dùng để lấy thời gian hiện tại khi log dữ liệu mới.
import requests  # Dùng để gọi API lấy danh sách giảng viên.
import os  # Dùng cho thao tác hệ điều hành (xóa màn hình, kiểm tra file).
from playwright.sync_api import sync_playwright  # Dùng Playwright bản sync để tự động hóa trình duyệt.

TARGET_URL_PART = "student-requests?ignorePhase=true"  # Chuỗi nhận diện API response cần bắt.

# ==========================================
# PHẦN 1: CÁC HÀM XỬ LÝ DỮ LIỆU VÀ HIỂN THỊ THỜI KHÓA BIỂU
# ==========================================

def get_teacher_mapping(cache_file='teachers_cache.json'):
    """Lấy danh sách giảng viên và hợp nhất với dữ liệu nhập tay."""
    
    # ---------------------------------------------------------
    # KHU VỰC NHẬP TAY (MANUAL DATA - まにゅある でーた)
    # Bạn hãy thêm ID và Tên giảng viên vào đây. 
    # Định dạng: "ID": "Tên Giảng Viên"
    # ---------------------------------------------------------
    MANUAL_TEACHER_DATA = {
        "4615741525458944": "Trương Minh Toàn",
        "4617949795057664": "Phạm Văn San",
        "4623128231673857": "Lê Đức Giang",
        "4770575788539905": "Nguyễn Xuân Hải",
        "4793298531123201": "Hoàng Việt Dũng",
        "4819206440747008": "Nguyễn Quốc Hưng",
        "4998574869839873": "Nguyễn Huy Tuân",
        "5210989632946176": "Trần Việt Thắng",
        "5235633853300736": "Trần Thanh Tú",
        "5250693149491200": "Phạm Thị Phương Giang",
        "5326822048792576": "Trần Anh Tú",
        "5629934265434113": "Trịnh Xuân Dũng",
        "5637900658016257": "Đinh Cao Tài",
        "5670847217926144": "Nguyễn Tiến Đạt",
        "5689497945636864": "Vũ Quang",
        "5778346726129664": "Phạm Văn Toàn",
        "5888940791824384": "Lương Minh Hạnh",
        "5995679136612352": "Trần Nhật Hoá",
        "6006299013677056": "Cấn Mạnh Tưởng",
        "6038868910407681": "Bùi Thị Quý",
        "6162933906145281": "Vũ Quang Ngọc",
        "6200850611437569": "Nguyễn Văn Hoạt",
        "6257620155367425": "Bùi Trung Kiên",
        "6409719031791616": "Nguyễn Long Giang",
        "6462169440845824": "Nguyễn Long Giang",
        "6483870333534208": "Trần Đức Quyết",
        "6503441543200769": "Umezawa Ayumi",
        "6592628233601024": "Phạm Thị Mai Duyên",
        "6635353540657153": "Nguyễn Đăng Khoa",
        "6649847734075392": "Vũ Thị Bích Tuyến",
        "6674983528955904": "Nguyễn Thị Thanh Dần",
    }
    # ---------------------------------------------------------

    teacher_map = {}

    # 1. Đọc từ Cache (Cache - Bộ nhớ đệm / きゃっしゅ) nếu có
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                teacher_map = json.load(f)
        except Exception as e:
            print(f"Lỗi đọc file cache: {e}")

    # 2. Nếu cache trống hoặc quá ít, tải từ API (API - Giao diện lập trình ứng dụng / えーぴーあい)
    if len(teacher_map) < 700:
        url = 'https://student.hust.edu.vn/api/v1/projects/project-topics/query'
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        root_ids = [
            6170508018057217, 6234759713783809, 5606644603944960, 5107078788022273,
            4618805103820801, 4560738412658689, 6534081428848641, 4836798626791424,
            4767095241834497, 5058924227067905, 5043694650523648, 4759934910595073,
        ]
        
        print("--- Đang tải bổ sung dữ liệu giảng viên từ API... ---")
        for rid in root_ids:
            payload = {"rootId": rid, "unitIds": [], "supervisorIds": None, "limited": False, "majorId": -1, "projectFrom": 1}
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    for item in data.get('data', []):
                        t_id = str(item.get('teacherId'))
                        t_name = item.get('teacherName')
                        if t_id and t_name:
                            teacher_map[t_id] = t_name
            except Exception:
                continue
        
        # Lưu cache sau khi tải xong
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(teacher_map, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Không thể lưu file cache: {e}")

    # 3. Hợp nhất (Merge - Hợp nhất / まーじ) dữ liệu nhập tay
    # Dữ liệu trong MANUAL_TEACHER_DATA sẽ ghi đè nếu trùng ID trong cache/API.
    teacher_map.update(MANUAL_TEACHER_DATA)
    
    print(f"--- Tổng cộng: {len(teacher_map)} giảng viên (đã bao gồm {len(MANUAL_TEACHER_DATA)} người nhập tay). ---")
    return teacher_map

def extract_hust_schedule_final(file_path, teacher_lookup):  # Hàm đọc class.json và in thời khóa biểu.
    try:  # Bắt lỗi đọc file hoặc parse JSON.
        with open(file_path, 'r', encoding='utf-8') as file:  # Mở file dữ liệu lớp ở chế độ đọc.
            content = file.read()  # Đọc toàn bộ nội dung file thành chuỗi.
            start_idx = content.find('{')  # Tìm vị trí dấu { đầu tiên để xác định JSON bắt đầu.
            end_idx = content.rfind('}')  # Tìm vị trí dấu } cuối cùng để xác định JSON kết thúc.
            if start_idx != -1 and end_idx != -1:  # Nếu tìm thấy biên JSON hợp lệ.
                data = json.loads(content[start_idx:end_idx+1])  # Cắt phần JSON và parse sang dict.
            else:  # Nếu không tìm được JSON hợp lệ.
                print("Không tìm thấy định dạng JSON hợp lệ.")  # Thông báo lỗi dữ liệu vào.
                return  # Dừng hàm vì không có dữ liệu để xử lý.
    except Exception as e:  # Nếu lỗi đọc file hoặc parse JSON.
        print(f"Lỗi đọc file: {e}")  # In chi tiết lỗi.
        return  # Dừng hàm.

    all_sessions = []  # Danh sách chứa toàn bộ buổi học để sắp xếp và in.
    counted_courses = set()  # Set để tránh cộng tín chỉ trùng học phần.
    total_credits = 0  # Tổng số tín chỉ.

    if "data" in data:  # Chỉ xử lý khi key data tồn tại.
        for item in data["data"]:  # Duyệt từng bản ghi đăng ký/lớp học.
            if item.get("processStatus") == 5:  # Bỏ qua các lớp có trạng thái processStatus = 5.
                continue  # Sang bản ghi kế tiếp.

            course_info = item.get("_course", {})  # Lấy thông tin học phần.
            credit = course_info.get("credit", 0)  # Lấy số tín chỉ, mặc định 0.
            course_id = item.get("courseId")  # Lấy mã học phần.

            class_info = item.get("_class", {})  # Lấy thông tin lớp học phần.
            course_name = class_info.get("courseName")  # Lấy tên học phần.
            class_id = item.get("classId")  # Lấy mã lớp.

            teacher_ids = class_info.get("teacherIds", [])  # Lấy danh sách teacherId của lớp.

            teacher_names = []  # Tạo list tên giảng viên tương ứng teacherIds.
            for t_id in teacher_ids:  # Duyệt từng teacherId.
                name = teacher_lookup.get(str(t_id), f"ID:{t_id}")  # Tra tên từ mapping, fallback về ID.
                teacher_names.append(name)  # Thêm tên vừa tra được vào danh sách.

            if course_id not in counted_courses:  # Nếu học phần chưa được tính tín chỉ.
                total_credits += credit  # Cộng tín chỉ vào tổng.
                counted_courses.add(course_id)  # Đánh dấu học phần đã tính.

            calendars = class_info.get("_calendars", [])  # Lấy danh sách lịch học của lớp.
            for cal in calendars:  # Duyệt từng lịch học chi tiết.
                day_time = cal.get("dayTime")  # Lấy buổi học (1 thường là sáng).
                session_name = "SÁNG" if day_time == 1 else "CHIỀU"  # Đổi dayTime sang nhãn dễ đọc.

                all_sessions.append({  # Thêm một buổi học vào danh sách tổng.
                    "day": cal.get("day"),  # Thứ trong tuần.
                    "from": cal.get("from"),  # Tiết bắt đầu.
                    "to": cal.get("to"),  # Tiết kết thúc.
                    "room": cal.get("place"),  # Phòng học.
                    "week": cal.get("week"),  # Tuần học.
                    "name": course_name,  # Tên học phần.
                    "class_id": class_id,  # Mã lớp.
                    "course_id": course_id,  # Mã học phần.
                    "teacher_names": teacher_names,  # Danh sách tên giảng viên.
                    "day_time": day_time,  # Giá trị buổi học gốc.
                    "session_name": session_name  # Nhãn buổi học hiển thị.
                })  # Kết thúc dict một session.

    all_sessions.sort(key=lambda x: (x['day'], x['day_time'], x['from']))  # Sắp xếp theo thứ, buổi, tiết bắt đầu.

    print(f"\n{' THỜI KHÓA BIỂU HUST (HIỂN THỊ TÊN GIẢNG VIÊN) ':=^70}")  # In tiêu đề bảng thời khóa biểu.
    print(f"Tổng số tín chỉ: {total_credits}")  # In tổng số tín chỉ.
    print("-" * 70)  # In đường kẻ phân cách.

    current_day = None  # Biến nhớ thứ hiện tại đang in.
    current_session = None  # Biến nhớ buổi hiện tại đang in.

    for s in all_sessions:  # Duyệt từng session đã sắp xếp.
        if s['day'] != current_day:  # Nếu sang ngày mới.
            day_text = f"THỨ {s['day']}" if s['day'] < 8 else "CHỦ NHẬT"  # Đổi số ngày thành text hiển thị.
            print(f"\n==== {day_text} ====")  # In header của ngày.
            current_day = s['day']  # Cập nhật ngày hiện tại.
            current_session = None  # Reset buổi để in lại nhãn buổi.

        if s['day_time'] != current_session:  # Nếu sang buổi mới trong cùng ngày.
            print(f"  [{s['session_name']}]")  # In nhãn buổi (SÁNG/CHIỀU).
            current_session = s['day_time']  # Cập nhật buổi hiện tại.

        time_slot = f"{s['from']}-{s['to']}"  # Tạo chuỗi tiết học từ-to.
        teachers_display = ", ".join(s['teacher_names']) if s['teacher_names'] else "Chưa cập nhật"  # Ghép tên GV thành chuỗi.

        print(f"    > Tiết {time_slot.ljust(6)} | {s['name']} ({s['course_id']})")  # In dòng tóm tắt môn học.
        print(f"      Phòng: {str(s['room']).ljust(10)} | Lớp: {s['class_id']} | GV: {teachers_display}")  # In phòng, lớp, giảng viên.


# ==========================================
# PHẦN 2: TỰ ĐỘNG HÓA VÀ KẾT NỐI VỚI PLAYWRIGHT
# ==========================================

def run(playwright):  # Hàm (Function - 関数 / かんすう) điều phối chính cho quá trình tự động hóa.
    # 1. Chuẩn bị dữ liệu giảng viên trước khi mở trình duyệt (Browser - ブラウザ / ぶらうざ)
    teacher_mapping = get_teacher_mapping()  

    # 2. Khởi tạo Playwright
    browser = playwright.chromium.launch(headless=False)  
    context = browser.new_context()  
    page = context.new_page()  

    print("\n" + "="*50)  
    print("HỆ THỐNG BẮT ĐẦU CHẠY...")  
    print("1. Hãy thao tác đăng nhập và giải Captcha trên cửa sổ trình duyệt (Browser - ブラウザ).")  
    print("2. SAU KHI ĐĂNG NHẬP THÀNH CÔNG, hãy quay lại cửa sổ dòng lệnh (Terminal - ターミナル) này và nhấn phím ENTER để hệ thống bắt đầu quét.")  
    print("="*50)  

    def handle_response(response):  
        if TARGET_URL_PART in response.url:  
            try:  
                json_data = response.json()  
                filename = "class.json"  
                with open(filename, "w", encoding="utf-8") as f:  
                    json.dump(json_data, f, ensure_ascii=False, indent=4)  

                os.system('cls' if os.name == 'nt' else 'clear')  
                print(f"[!] Đã bắt được dữ liệu mới lúc: {time.strftime('%H:%M:%S')}")  
                extract_hust_schedule_final(filename, teacher_mapping)  
                print("\n...Đang tiếp tục lắng nghe dữ liệu mới...")  

            except Exception as e:  
                print(f"Lỗi khi parse JSON: {e}")  

    # Đăng ký lắng nghe sự kiện response
    page.on("response", handle_response)  

    # Mở trang lần đầu
    page.goto("https://qldt.hust.edu.vn/students/learn/class-registration")  

    # THAY ĐỔI Ở ĐÂY: Dùng input() để người dùng tự quyết định thời gian chờ (Timeout - タイムアウト / たいむあうと)
    input("\n>>> [CHỜ XÁC NHẬN] Bấm phím ENTER tại đây SAU KHI bạn đã vào đến trang đăng ký... <<<")

    # Vòng lặp (Loop - ループ / るーぷ) tải lại trang
    try:  
        while True:  
            page.goto("https://qldt.hust.edu.vn/students/learn/class-registration")  
            page.wait_for_timeout(5000)  
    except Exception as e:  
        print(f"\nDừng chương trình: {e}")  
    finally:  
        browser.close()  

if __name__ == "__main__":  
    with sync_playwright() as playwright:  
        run(playwright)