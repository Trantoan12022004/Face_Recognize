import face_recognition
import cv2
import numpy as np
import os

def recognize_from_image(image_path, known_face_encodings, known_face_names, user_info=None):
    """
    Nhận diện khuôn mặt từ file ảnh và hiển thị thông tin người dùng
    """
    # Kiểm tra file ảnh có tồn tại
    if not os.path.exists(image_path):
        print(f"Error: Image file '{image_path}' not found.")
        return
    
    try:
        # Tải ảnh và tìm khuôn mặt
        print(f"Processing image: {image_path}")
        img = face_recognition.load_image_file(image_path)
        face_locations = face_recognition.face_locations(img)
        
        if len(face_locations) == 0:
            print("No faces found in the image.")
            return
            
        print(f"Found {len(face_locations)} face(s) in the image.")
        face_encodings = face_recognition.face_encodings(img, face_locations)
        
        # Xử lý từng khuôn mặt trong ảnh
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # So sánh với khuôn mặt đã biết
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = 'Unknown'
            
            # Tìm khuôn mặt gần giống nhất
            if len(known_face_encodings) > 0:
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]
            
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
                    cv2.putText(img, f"Age: {age}", (left, bottom + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 1)
                    # Thêm địa chỉ (có thể dài nên chia thành 2 dòng nếu cần)
                    if len(address) > 20:
                        cv2.putText(img, f"Address: {address[:20]}...", (left, bottom + 45), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 1)
                    else:
                        cv2.putText(img, f"Address: {address}", (left, bottom + 45), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 1)
                
            cv2.rectangle(img, (left, top), (right, bottom), color, 2)
            cv2.putText(img, text, (left, top-10), cv2.FONT_HERSHEY_DUPLEX, 1.0, color, 2)
            
        # Chuyển từ RGB sang BGR (cho OpenCV)
        image_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        
        # Hiển thị ảnh với kết quả
        cv2.imshow('Face Recognition', image_bgr)
        print("Press any key to close the image.")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
    except Exception as e:
        print(f"Error processing image: {e}")