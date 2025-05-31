"""
Module quản lý điểm danh trong hệ thống nhận diện khuôn mặt
"""
import datetime

def display_attendance_menu():
    """Hiển thị menu quản lý điểm danh"""
    print("\nQuản lý điểm danh:")
    print("1. Điểm danh (Check-in) qua webcam")
    print("2. Checkout khi kết thúc")
    print("3. Xem báo cáo điểm danh hôm nay")
    print("4. Xem báo cáo điểm danh theo ngày")
    print("5. Xuất báo cáo điểm danh ra Excel")
    print("6. Quay lại menu chính")

def attendance_management(encoder):
    """Chức năng quản lý điểm danh"""
    # Khởi tạo hệ thống điểm danh
    from modules.attendance import AttendanceSystem
    attendance_system = AttendanceSystem()
    
    while True:
        display_attendance_menu()
        choice = input("Chọn chức năng (1-6): ")
        
        if choice == '1':
            # Lấy dữ liệu khuôn mặt
            known_face_encodings, known_face_names = encoder.get_encodings()
            
            # Tiến hành điểm danh (check-in)
            attendance_system.take_attendance_webcam(
                known_face_encodings, 
                known_face_names,
                encoder.get_all_users(),
                is_checkout=False,
                camera_id=1  # Sử dụng camera 1 mặc định
            )
        elif choice == '2':
            # Checkout khi kết thúc
            known_face_encodings, known_face_names = encoder.get_encodings()
            attendance_system.take_attendance_webcam(
                known_face_encodings,
                known_face_names,
                encoder.get_all_users(),
                is_checkout=True,
                camera_id=1  # Sử dụng camera 1 mặc định
            )
        elif choice == '3':
            # Hiển thị báo cáo điểm danh hôm nay
            attendance_system.display_attendance_report(encoder.get_unique_users())
        elif choice == '4':
            # Nhập ngày cần xem báo cáo
            date_input = input("Nhập ngày cần xem (YYYY-MM-DD): ")
            try:
                # Kiểm tra định dạng ngày
                datetime.date.fromisoformat(date_input)
                attendance_system.display_attendance_report(encoder.get_unique_users(), date_input)
            except ValueError:
                print("Định dạng ngày không hợp lệ. Vui lòng sử dụng định dạng YYYY-MM-DD.")
        elif choice == '5':
            # Xuất báo cáo điểm danh ra Excel
            date_input = input("Nhập ngày cần xuất báo cáo (YYYY-MM-DD), để trống cho ngày hôm nay: ")
            
            if not date_input:
                date = None
            else:
                try:
                    # Kiểm tra định dạng ngày
                    datetime.date.fromisoformat(date_input)
                    date = date_input
                except ValueError:
                    print("Định dạng ngày không hợp lệ. Đang sử dụng ngày hôm nay.")
                    date = None
            
            # Xuất báo cáo ra Excel
            attendance_system.export_to_excel(encoder.get_unique_users(), date)
        elif choice == '6':
            print("Quay lại menu chính...")
            break
        else:
            print("Lựa chọn không hợp lệ. Vui lòng thử lại.")