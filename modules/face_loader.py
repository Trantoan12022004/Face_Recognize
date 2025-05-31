import face_recognition
import os
import pickle
import numpy as np
import json
import shutil
import cv2
import uuid
from modules.camera_utils import select_camera

class FaceEncoder:
    def __init__(self, photos_dir='photo', encodings_file='data/face_encodings.pkl', user_info_file='data/user_info.json'):
        self.photos_dir = photos_dir
        self.encodings_file = encodings_file
        self.user_info_file = user_info_file
        self.known_face_encodings = []
        self.known_face_names = []
        self.user_info = {}  # Dictionary lưu thông tin người dùng
        
        # Tạo thư mục data nếu chưa tồn tại
        os.makedirs(os.path.dirname(self.encodings_file), exist_ok=True)
        
        # Tải thông tin người dùng nếu có
        self.load_user_info()
        
    def load_photos(self):
        """Load face encodings from photo directory"""
        print("Loading face photos...")
        # Đảm bảo thư mục photos tồn tại
        if not os.path.exists(self.photos_dir):
            print(f"Error: Directory '{self.photos_dir}' not found.")
            return False
            
        # Reset danh sách để tải lại
        self.known_face_encodings = []
        self.known_face_names = []
        
        # Duyệt từng thư mục con trong photo (mỗi thư mục là tên người)
        for person_name in os.listdir(self.photos_dir):
            person_folder = os.path.join(self.photos_dir, person_name)
            
            if not os.path.isdir(person_folder):
                continue
                
            print(f"Processing photos for {person_name}...")
            
            # Thêm người dùng vào danh sách thông tin nếu chưa có
            if person_name not in self.user_info:
                self.user_info[person_name] = {
                    "age": None,
                    "address": None
                }
            
            # Duyệt từng ảnh trong thư mục con
            for filename in os.listdir(person_folder):
                if filename.endswith(('.jpg', '.jpeg', '.png')):
                    image_path = os.path.join(person_folder, filename)
                    print(f"  Processing {filename}")
                    
                    try:
                        # Tải và mã hóa khuôn mặt
                        image = face_recognition.load_image_file(image_path)
                        encodings = face_recognition.face_encodings(image)
                        
                        if len(encodings) > 0:
                            self.known_face_encodings.append(encodings[0])
                            self.known_face_names.append(person_name)
                        else:
                            print(f"  Warning: No face found in {filename}")
                    except Exception as e:
                        print(f"  Error processing {filename}: {e}")
        
        print(f"Loaded {len(self.known_face_encodings)} faces")
        # Lưu thông tin người dùng sau khi tải ảnh
        self.save_user_info()
        return len(self.known_face_encodings) > 0
    
    def save_encodings(self):
        """Save encodings to file"""
        data = {
            "encodings": self.known_face_encodings,
            "names": self.known_face_names
        }
        
        with open(self.encodings_file, 'wb') as f:
            pickle.dump(data, f)
        
        print(f"Saved {len(self.known_face_encodings)} face encodings to {self.encodings_file}")
    
    def load_encodings(self):
        """Load encodings from file"""
        if not os.path.exists(self.encodings_file):
            print(f"Encodings file {self.encodings_file} not found. Will create after loading photos.")
            return False
        
        try:
            with open(self.encodings_file, 'rb') as f:
                data = pickle.load(f)
                
            self.known_face_encodings = data["encodings"]
            self.known_face_names = data["names"]
            
            print(f"Loaded {len(self.known_face_encodings)} face encodings from file")
            return True
        except Exception as e:
            print(f"Error loading encodings: {e}")
            return False
    
    def get_encodings(self):
        """Return the current encodings and names"""
        return self.known_face_encodings, self.known_face_names
        
    def save_user_info(self):
        """Lưu thông tin người dùng vào file JSON"""
        with open(self.user_info_file, 'w', encoding='utf-8') as f:
            json.dump(self.user_info, f, ensure_ascii=False, indent=2)
        print(f"Saved user information to {self.user_info_file}")
        
    def load_user_info(self):
        """Tải thông tin người dùng từ file JSON"""
        if not os.path.exists(self.user_info_file):
            print(f"User info file {self.user_info_file} not found. Will create a new one.")
            self.user_info = {}
            return False
            
        try:
            with open(self.user_info_file, 'r', encoding='utf-8') as f:
                self.user_info = json.load(f)
            print(f"Loaded information for {len(self.user_info)} users")
            return True
        except Exception as e:
            print(f"Error loading user info: {e}")
            self.user_info = {}
            return False
            
    def update_user_info(self, name, age=None, address=None):
        """Cập nhật thông tin cho người dùng cụ thể"""
        if name not in self.known_face_names and name not in self.user_info:
            print(f"User {name} not found in database")
            return False
            
        # Tạo mới nếu chưa có thông tin
        if name not in self.user_info:
            self.user_info[name] = {}
            
        # Cập nhật thông tin
        if age is not None:
            self.user_info[name]["age"] = age
        if address is not None:
            self.user_info[name]["address"] = address
            
        # Lưu thông tin vào file
        self.save_user_info()
        return True
        
    def get_all_users(self):
        """Trả về danh sách tất cả người dùng và thông tin của họ"""
        return self.user_info
        
    def get_user_info(self, name):
        """Trả về thông tin của một người dùng cụ thể"""
        if name in self.user_info:
            return self.user_info[name]
        return None
    
    def get_unique_users(self):
        """Trả về danh sách tên người dùng không trùng lặp"""
        return list(set(self.known_face_names))
    
    def add_user_from_image(self, image_path, user_name, age=None, address=None):
        """
        Thêm người dùng mới từ ảnh có sẵn
        """
        # Kiểm tra file ảnh có tồn tại không
        if not os.path.exists(image_path):
            print(f"Lỗi: File ảnh '{image_path}' không tồn tại.")
            return False
            
        # Kiểm tra ảnh có chứa khuôn mặt không
        image = face_recognition.load_image_file(image_path)
        face_locations = face_recognition.face_locations(image)
        
        if not face_locations:
            print("Lỗi: Không tìm thấy khuôn mặt trong ảnh.")
            return False
        
        # Tạo thư mục cho người dùng mới nếu chưa tồn tại
        user_folder = os.path.join(self.photos_dir, user_name)
        os.makedirs(user_folder, exist_ok=True)
        
        # Lưu ảnh vào thư mục người dùng
        # Tạo tên file mới với định dạng: name_001.jpg
        file_extension = os.path.splitext(image_path)[1].lower()
        if not file_extension:
            file_extension = '.jpg'  # Mặc định là jpg nếu không có phần mở rộng
        
        # Đếm số file ảnh đã có trong thư mục
        existing_files = [f for f in os.listdir(user_folder) if f.endswith(('.jpg', '.jpeg', '.png'))]
        new_file_name = f"{user_name}_{len(existing_files) + 1:03d}{file_extension}"
        
        dest_path = os.path.join(user_folder, new_file_name)
        shutil.copy2(image_path, dest_path)
        
        print(f"Đã lưu ảnh vào: {dest_path}")
        
        # Thêm thông tin người dùng
        self.update_user_info(user_name, age, address)
        
        # Cập nhật danh sách khuôn mặt
        encoding = face_recognition.face_encodings(image)[0]
        self.known_face_encodings.append(encoding)
        self.known_face_names.append(user_name)
        
        # Lưu dữ liệu
        self.save_encodings()
        
        print(f"Đã thêm người dùng mới: {user_name}")
        return True

    def add_user_from_webcam(self, user_name, age=None, address=None, num_photos=3):
        """
        Thêm người dùng mới bằng cách chụp ảnh từ webcam
        """
        # Tạo thư mục cho người dùng mới nếu chưa tồn tại
        user_folder = os.path.join(self.photos_dir, user_name)
        os.makedirs(user_folder, exist_ok=True)
        
        # Sử dụng WebcamManager để mở cửa sổ webcam riêng
        webcam_mgr = WebcamManager()
        
        def process_captured_images(images, username):
            if not images:
                return False
                
            encodings_added = 0
            
            for i, image in enumerate(images):
                # Lưu ảnh vào thư mục người dùng
                new_file_name = f"{username}_{i + 1:03d}.jpg"
                image_path = os.path.join(user_folder, new_file_name)
                
                # Lưu ảnh
                cv2.imwrite(image_path, image)
                
                try:
                    # Thêm encoding vào danh sách
                    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    face_locations = face_recognition.face_locations(rgb_image)
                    
                    if face_locations:
                        encoding = face_recognition.face_encodings(rgb_image, face_locations)[0]
                        self.known_face_encodings.append(encoding)
                        self.known_face_names.append(username)
                        encodings_added += 1
                except Exception as e:
                    print(f"Lỗi khi mã hóa khuôn mặt: {e}")
            
            # Thêm thông tin người dùng và lưu encoding
            if encodings_added > 0:
                self.update_user_info(username, age, address)
                self.save_encodings()
                messagebox.showinfo("Thành công", 
                                 f"Đã thêm người dùng {username} với {encodings_added} ảnh khuôn mặt!")
                return True
            else:
                messagebox.showerror("Lỗi", "Không thể mã hóa khuôn mặt từ ảnh chụp")
                return False
        
        # Mở cửa sổ webcam để chụp ảnh
        webcam_mgr.open_webcam_window(
            parent=None,  # Cần truyền parent từ app.py
            title=f"Chụp ảnh cho {user_name}",
            callback_fn=process_captured_images,
            is_capture_mode=True,
            num_photos=num_photos,
            username=user_name
        )
        
        return True  # Trả về True vì kết quả thực sự sẽ được xử lý trong callback
    
    def process_user_images(self, user_name, images, age=None, address=None):
        """
        Xử lý ảnh chụp cho người dùng mới
        """
        # Tạo thư mục cho người dùng nếu chưa tồn tại
        user_folder = os.path.join(self.photos_dir, user_name)
        os.makedirs(user_folder, exist_ok=True)
        
        encodings_added = 0
        
        for i, image in enumerate(images):
            # Lưu ảnh vào thư mục người dùng
            new_file_name = f"{user_name}_{i + 1:03d}.jpg"
            image_path = os.path.join(user_folder, new_file_name)
            
            # Lưu ảnh
            cv2.imwrite(image_path, image)
            
            try:
                # Thêm encoding vào danh sách
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                face_locations = face_recognition.face_locations(rgb_image)
                
                if face_locations:
                    encoding = face_recognition.face_encodings(rgb_image, face_locations)[0]
                    self.known_face_encodings.append(encoding)
                    self.known_face_names.append(user_name)
                    encodings_added += 1
            except Exception as e:
                print(f"Lỗi khi mã hóa khuôn mặt: {e}")
        
        # Thêm thông tin người dùng nếu đã thêm ít nhất một encoding
        if encodings_added > 0:
            self.update_user_info(user_name, age, address)
            self.save_encodings()
            return True
            
        return False