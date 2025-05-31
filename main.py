import os
from modules.face_loader import FaceEncoder
from modules.webcam import recognize_from_webcam
from modules.image_processor import recognize_from_image
from modules.attendance import AttendanceSystem
import datetime

def display_user_management_menu():
    print("\nUser Management:")
    print("1. View all users")
    print("2. Update user information")
    print("3. Add new user")  # Tùy chọn mới
    print("4. Return to main menu")

def view_all_users(encoder):
    users = encoder.get_all_users()
    if not users:
        print("\nNo users in database.")
        return
        
    print("\n===== USER DATABASE =====")
    for name, info in users.items():
        age = info.get("age", "Not set")
        address = info.get("address", "Not set")
        print(f"\nName: {name}")
        print(f"Age: {age}")
        print(f"Address: {address}")
    print("=======================")

def update_user_info(encoder):
    view_all_users(encoder)
    
    name = input("\nEnter user name to update: ")
    
    # Kiểm tra người dùng có tồn tại không
    all_users = encoder.get_all_users()
    if name not in all_users and name not in encoder.known_face_names:
        print(f"User {name} not found in database.")
        return
    
    print(f"Updating information for {name}")
    
    # Lấy thông tin hiện tại
    current_info = encoder.get_user_info(name) or {}
    current_age = current_info.get("age")
    current_address = current_info.get("address")
    
    # Hiển thị thông tin hiện tại
    print(f"Current age: {current_age if current_age else 'Not set'}")
    print(f"Current address: {current_address if current_address else 'Not set'}")
    
    # Cập nhật thông tin
    age_input = input("Enter new age (leave empty to keep current): ")
    age = age_input if age_input else current_age
    
    address_input = input("Enter new address (leave empty to keep current): ")
    address = address_input if address_input else current_address
    
    # Lưu thông tin mới
    if encoder.update_user_info(name, age, address):
        print(f"Information for {name} has been updated.")
    else:
        print("Failed to update user information.")

def add_new_user(encoder):
    """Thêm người dùng mới vào hệ thống"""
    print("\n===== Add New User =====")
    
    # Nhập tên người dùng mới
    user_name = input("Enter name for the new user: ")
    
    # Kiểm tra xem người dùng đã tồn tại chưa
    all_users = encoder.get_all_users()
    if user_name in all_users:
        print(f"User '{user_name}' already exists in the system.")
        overwrite = input("Do you want to add more photos for this user? (y/n): ")
        if overwrite.lower() != 'y':
            return
    
    # Nhập thông tin người dùng
    age = input("Enter age (leave empty if unknown): ")
    address = input("Enter address (leave empty if unknown): ")
    
    # Chọn phương thức thêm người dùng
    print("\nHow would you like to add user photos?")
    print("1. Capture from webcam")
    print("2. Use existing image file")
    
    choice = input("Choose an option (1-2): ")
    
    if choice == '1':
        # Thêm người dùng từ webcam
        num_photos = input("How many photos to take (default: 3): ")
        try:
            num_photos = int(num_photos) if num_photos else 3
        except ValueError:
            num_photos = 3
        
        # Gọi hàm với tham số camera_id=None để hỏi người dùng
        success = encoder.add_user_from_webcam(user_name, age, address, num_photos, camera_id=None)
        if success:
            print(f"Successfully added new user: {user_name}")
        else:
            print(f"Failed to add new user: {user_name}")
    
    elif choice == '2':
        # Thêm người dùng từ file ảnh
        image_path = input("Enter path to image file: ")
        
        success = encoder.add_user_from_image(image_path, user_name, age, address)
        if success:
            print(f"Successfully added new user: {user_name}")
        else:
            print(f"Failed to add new user: {user_name}")
    
    else:
        print("Invalid option selected.")

def user_management_menu(encoder):
    while True:
        display_user_management_menu()
        choice = input("Choose an option (1-4): ")  # Đã thay đổi từ 1-3 thành 1-4
        
        if choice == '1':
            view_all_users(encoder)
        elif choice == '2':
            update_user_info(encoder)
        elif choice == '3':
            add_new_user(encoder)  # Gọi chức năng mới
        elif choice == '4':  # Đã thay đổi từ 3 thành 4
            print("Returning to main menu...")
            break
        else:
            print("Invalid choice. Please try again.")

def display_attendance_menu():
    print("\nQuản lý điểm danh:")
    print("1. Điểm danh (Check-in) qua webcam")
    print("2. Checkout khi kết thúc")
    print("3. Xem báo cáo điểm danh hôm nay")
    print("4. Xem báo cáo điểm danh theo ngày")
    print("5. Xuất báo cáo điểm danh ra Excel")
    print("6. Quay lại menu chính")

def attendance_management(encoder):
    # Khởi tạo hệ thống điểm danh
    attendance_system = AttendanceSystem()
    
    while True:
        display_attendance_menu()
        choice = input("Chọn chức năng (1-6): ")
        
        if choice == '1':
            # Lấy dữ liệu khuôn mặt
            known_face_encodings, known_face_names = encoder.get_encodings()
            
            # Tiến hành điểm danh (check-in), cho phép chọn camera
            attendance_system.take_attendance_webcam(
                known_face_encodings, 
                known_face_names,
                encoder.get_all_users(),
                is_checkout=False,
                camera_id=None  # Sẽ yêu cầu người dùng chọn
            )
        elif choice == '2':
            # Checkout khi kết thúc, cho phép chọn camera
            known_face_encodings, known_face_names = encoder.get_encodings()
            attendance_system.take_attendance_webcam(
                known_face_encodings,
                known_face_names,
                encoder.get_all_users(),
                is_checkout=True,
                camera_id=None  # Sẽ yêu cầu người dùng chọn
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
                    date = datetime.date.fromisoformat(date_input)
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

def main():
    print("===== FACE RECOGNITION SYSTEM =====")
    
    # Khởi tạo FaceEncoder
    encoder = FaceEncoder()
    
    # Thử tải từ file có sẵn
    if not encoder.load_encodings():
        # Nếu không có file có sẵn hoặc lỗi, tải từ ảnh gốc
        if encoder.load_photos():
            # Lưu lại để lần sau dùng
            encoder.save_encodings()
        else:
            print("Error: Could not load face data.")
            return
    
    # Lấy dữ liệu khuôn mặt
    known_face_encodings, known_face_names = encoder.get_encodings()
    
    if len(known_face_encodings) == 0:
        print("No face data available. Please add face images to the 'photo' directory.")
        return
    
    # Menu chọn chức năng
    while True:
        print("\nOptions:")
        print("1. Recognize from webcam")
        print("2. Recognize from image file")
        print("3. Reload face data")
        print("4. User management")
        print("5. Quản lý điểm danh")  # Thêm tùy chọn mới
        print("6. Exit")
        
        choice = input("Choose an option (1-6): ")
        
        if choice == '1':
            # Nhận diện từ webcam, cho phép chọn camera
            recognize_from_webcam(known_face_encodings, known_face_names, encoder.get_all_users(), camera_id=None)
        elif choice == '2':
            image_path = input("Enter image path: ")
            recognize_from_image(image_path, known_face_encodings, known_face_names, encoder.get_all_users())
        elif choice == '3':
            print("Reloading face data...")
            encoder.load_photos()
            encoder.save_encodings()
            known_face_encodings, known_face_names = encoder.get_encodings()
            print("Face data reloaded.")
        elif choice == '4':
            user_management_menu(encoder)
            # Tải lại danh sách người dùng nếu có thay đổi
            known_face_encodings, known_face_names = encoder.get_encodings()
            print("Face data reloaded.")
        elif choice == '5':
            attendance_management(encoder)  # Chức năng quản lý điểm danh
        elif choice == '6':
            print("Exiting program...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == '__main__':
    main()