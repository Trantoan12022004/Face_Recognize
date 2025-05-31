"""
Module quản lý menu chính của ứng dụng nhận diện khuôn mặt
"""

def display_main_menu():
    """Hiển thị menu chính của ứng dụng"""
    print("\nOptions:")
    print("1. Recognize from webcam")
    print("2. Recognize from image file")
    print("3. Reload face data")
    print("4. User management")
    print("5. Quản lý điểm danh")
    print("6. Exit")

def handle_main_menu(encoder):
    """Xử lý menu chính của ứng dụng"""
    from modules.webcam import recognize_from_webcam
    from modules.image_processor import recognize_from_image
    from modules.user_management import user_management_menu
    from modules.attendance_management import attendance_management
    
    # Lấy dữ liệu khuôn mặt
    known_face_encodings, known_face_names = encoder.get_encodings()
    
    if len(known_face_encodings) == 0:
        print("No face data available. Please add face images to the 'photo' directory.")
        return False
    
    while True:
        display_main_menu()
        choice = input("Choose an option (1-6): ")
        
        if choice == '1':
            # Nhận diện từ webcam
            recognize_from_webcam(
                known_face_encodings, 
                known_face_names, 
                encoder.get_all_users(), 
                camera_id=1  # Sử dụng camera 1 mặc định
            )
        elif choice == '2':
            # Nhận diện từ file ảnh
            image_path = input("Enter image path: ")
            recognize_from_image(
                image_path, 
                known_face_encodings, 
                known_face_names, 
                encoder.get_all_users()
            )
        elif choice == '3':
            # Tải lại dữ liệu khuôn mặt
            print("Reloading face data...")
            encoder.load_photos()
            encoder.save_encodings()
            known_face_encodings, known_face_names = encoder.get_encodings()
            print("Face data reloaded.")
        elif choice == '4':
            # Quản lý người dùng
            user_management_menu(encoder)
            # Tải lại danh sách người dùng nếu có thay đổi
            known_face_encodings, known_face_names = encoder.get_encodings()
            print("Face data reloaded.")
        elif choice == '5':
            # Quản lý điểm danh
            attendance_management(encoder)
        elif choice == '6':
            # Thoát chương trình
            print("Exiting program...")
            return True
        else:
            print("Invalid choice. Please try again.")
    
    return False