import cv2
import time

def list_available_cameras(max_cameras=5):
    """
    Tìm và liệt kê các camera có sẵn trong hệ thống
    """
    available_cameras = []
    
    print("Đang quét tìm camera có sẵn...")
    
    for i in range(max_cameras):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                camera_name = f"Camera {i}"
                # Thử đọc tên camera nếu có thể (không phải tất cả camera đều hỗ trợ)
                try:
                    vendor = cap.getBackendName()
                    if vendor:
                        camera_name = f"Camera {i} ({vendor})"
                except:
                    pass
                    
                available_cameras.append((i, camera_name))
            cap.release()
        time.sleep(0.1)  # Đợi một chút giữa các lần thử để tránh lỗi
    
    return available_cameras

def select_camera():
    """
    Hiển thị menu để người dùng chọn camera
    """
    cameras = list_available_cameras()
    
    if not cameras:
        print("Không tìm thấy camera nào. Sử dụng camera mặc định (0).")
        return 0
        
    print("\nCamera có sẵn:")
    for idx, (cam_id, cam_name) in enumerate(cameras, 1):
        print(f"{idx}. {cam_name}")
    
    try:
        choice = int(input("Chọn camera (1-{}): ".format(len(cameras))))
        if 1 <= choice <= len(cameras):
            selected_camera = cameras[choice-1][0]
            print(f"Đã chọn: {cameras[choice-1][1]}")
            return selected_camera
        else:
            print("Lựa chọn không hợp lệ. Sử dụng camera mặc định (0).")
            return 0
    except ValueError:
        print("Nhập không hợp lệ. Sử dụng camera mặc định (0).")
        return 0