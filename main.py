"""
File chính của ứng dụng nhận diện khuôn mặt
"""
from modules.face_loader import FaceEncoder
from modules.menu_management import handle_main_menu

def main():
    """Hàm chính khởi chạy ứng dụng"""
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
    
    # Chạy menu chính
    should_exit = handle_main_menu(encoder)
    
    # Kết thúc chương trình
    if should_exit:
        print("Program terminated.")

if __name__ == '__main__':
    main()