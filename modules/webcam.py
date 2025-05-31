import face_recognition
import cv2
import numpy as np
from modules.camera_utils import select_camera

def recognize_from_webcam(known_face_encodings, known_face_names, user_info=None, camera_id=None):
    """
    Nhận diện khuôn mặt qua webcam và hiển thị thông tin người dùng
    """
    # Cho phép người dùng chọn camera nếu không chỉ định
    if camera_id is None:
        camera_id = select_camera()
    
    # Mở webcam
    video_capture = cv2.VideoCapture(camera_id)
    
    if not video_capture.isOpened():
        print(f"Lỗi: Không thể mở camera {camera_id}")
        return
    
    print(f"Đang sử dụng camera {camera_id}. Nhấn 'q' để thoát.")
    
    process_this_frame = True

    while True:
        # Đọc frame từ webcam
        ret, frame = video_capture.read()

        if not ret:
            print("Error: Failed to capture image")
            break

        # Chỉ xử lý 1 frame bỏ qua 1 frame để tối ưu hiệu năng
        if process_this_frame:
            # Giảm kích thước frame để xử lý nhanh hơn
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            
            # Chuyển từ BGR (OpenCV) sang RGB (face_recognition)
            rgb_small_frame = small_frame[:, :, ::-1]

            # Tìm khuôn mặt trong frame
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            face_names = []
            for face_encoding in face_encodings:
                # So sánh với khuôn mặt đã biết
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"

                # Tìm khuôn mặt gần giống nhất
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                if len(face_distances) > 0:
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = known_face_names[best_match_index]

                face_names.append(name)

        process_this_frame = not process_this_frame

        # Hiển thị kết quả
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Thay đổi tỉ lệ vị trí khuôn mặt về kích thước gốc
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Vẽ hộp quanh khuôn mặt
            if name == 'Unknown':
                color = (0, 0, 255)  # Đỏ cho unknown
                text = name
            else:
                color = (0, 255, 0)  # Xanh lá cho khuôn mặt đã biết
                text = name
                
                # Hiển thị thông tin người dùng nếu có
                if user_info and name in user_info:
                    info = user_info.get(name, {})
                    age = info.get("age", "N/A")
                    address = info.get("address", "N/A")
                    
                    # Thêm thông tin người dùng
                    cv2.putText(frame, f"Age: {age}", (left, bottom + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                    
                    # Địa chỉ có thể dài, nên giới hạn hiển thị
                    if len(address) > 20:
                        address_text = f"Address: {address[:20]}..."
                    else:
                        address_text = f"Address: {address}"
                    cv2.putText(frame, address_text, (left, bottom + 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, text, (left, top-10), cv2.FONT_HERSHEY_DUPLEX, 1.0, color, 2)
            
        # Hiển thị khung hình kết quả
        cv2.imshow('Face Recognition', frame)

        # Thoát khi nhấn 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Dọn dẹp
    video_capture.release()
    cv2.destroyAllWindows()