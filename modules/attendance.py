import os
import json
import datetime
import cv2
import face_recognition
import numpy as np
from time import sleep
import pandas as pd
from datetime import datetime as dt

class AttendanceSystem:
    def __init__(self, attendance_file='data/attendance.json'):
        self.attendance_file = attendance_file
        # Đảm bảo thư mục data tồn tại
        os.makedirs(os.path.dirname(attendance_file), exist_ok=True)
        self.attendance_data = self.load_attendance_data()
        
    def load_attendance_data(self):
        """Tải dữ liệu điểm danh từ file"""
        if not os.path.exists(self.attendance_file):
            return {}
        
        try:
            with open(self.attendance_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Lỗi khi tải dữ liệu điểm danh: {e}")
            return {}
            
    def save_attendance_data(self):
        """Lưu dữ liệu điểm danh vào file"""
        with open(self.attendance_file, 'w', encoding='utf-8') as f:
            json.dump(self.attendance_data, f, ensure_ascii=False, indent=2)
        print(f"Đã lưu dữ liệu điểm danh vào {self.attendance_file}")
    
    def mark_attendance(self, name, timestamp=None):
        """Điểm danh một người dùng (check-in)"""
        # Lấy ngày hiện tại
        today = datetime.date.today().isoformat()
        
        # Lấy thời gian hiện tại nếu không được cung cấp
        if timestamp is None:
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        # Tạo mục cho ngày hôm nay nếu chưa có
        if today not in self.attendance_data:
            self.attendance_data[today] = {}
        
        # Kiểm tra xem người này đã điểm danh chưa
        if name in self.attendance_data[today]:
            # Nếu đã checkout thì không cho check-in lại
            if "checkout" in self.attendance_data[today][name]:
                print(f"{name} đã hoàn thành cả check-in và check-out.")
                return False
            # Nếu chỉ có check-in thì không làm gì
            print(f"{name} đã điểm danh trước đó lúc {self.attendance_data[today][name]['checkin']}")
            return True
        
        # Đánh dấu người này đã điểm danh (check-in)
        self.attendance_data[today][name] = {"checkin": timestamp}
        
        # Lưu dữ liệu
        self.save_attendance_data()
        return True
        
    def checkout(self, name, timestamp=None):
        """Đánh dấu checkout cho một người dùng"""
        today = datetime.date.today().isoformat()
        
        # Lấy thời gian hiện tại nếu không được cung cấp
        if timestamp is None:
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        # Kiểm tra xem người này đã điểm danh chưa
        if today not in self.attendance_data or name not in self.attendance_data[today]:
            print(f"{name} chưa điểm danh hôm nay, không thể checkout.")
            return False
        
        # Kiểm tra xem đã checkout chưa
        if "checkout" in self.attendance_data[today][name]:
            print(f"{name} đã checkout trước đó lúc {self.attendance_data[today][name]['checkout']}")
        else:
            # Đánh dấu checkout
            self.attendance_data[today][name]["checkout"] = timestamp
            self.save_attendance_data()
            print(f"Đã ghi nhận checkout cho {name} lúc {timestamp}")
        
        return True
        
    def get_today_attendance(self):
        """Lấy danh sách điểm danh cho ngày hôm nay"""
        today = datetime.date.today().isoformat()
        attendance_data = self.attendance_data.get(today, {})
        
        # Chuyển đổi định dạng dữ liệu cũ nếu cần
        converted_data = {}
        for name, value in attendance_data.items():
            if isinstance(value, str):  # Định dạng cũ chỉ lưu thời gian check-in
                converted_data[name] = {"checkin": value}
            else:
                converted_data[name] = value
                
        return converted_data
        
    def get_date_attendance(self, date):
        """Lấy danh sách điểm danh cho một ngày cụ thể"""
        attendance_data = self.attendance_data.get(date, {})
        
        # Chuyển đổi định dạng dữ liệu cũ nếu cần
        converted_data = {}
        for name, value in attendance_data.items():
            if isinstance(value, str):  # Định dạng cũ chỉ lưu thời gian check-in
                converted_data[name] = {"checkin": value}
            else:
                converted_data[name] = value
                
        return converted_data
        
    def get_absent_list(self, all_users, date=None):
        """Lấy danh sách người vắng mặt"""
        if date is None:
            date = datetime.date.today().isoformat()
            
        # Lấy danh sách người đã điểm danh
        attendance_data = self.get_date_attendance(date)
        
        # Đảm bảo all_users không có trùng lặp (vì một người có thể có nhiều ảnh)
        unique_users = list(set(all_users))
        
        # Tạo danh sách người vắng mặt
        absent_list = [user for user in unique_users if user not in attendance_data]
        return absent_list

    def take_attendance_webcam(self, known_face_encodings, known_face_names, user_info=None, is_checkout=False, camera_id=1):
        """Điểm danh thông qua webcam (có thể là check-in hoặc check-out)"""
        # Sử dụng camera mặc định là 1, bỏ phần chọn camera
        # Nếu có truyền camera_id thì sử dụng, nếu không thì mặc định là 1
        if camera_id is None:
            camera_id = 1  # Mặc định sử dụng camera 1
    
        # Mở webcam
        video_capture = cv2.VideoCapture(camera_id)
        
        if not video_capture.isOpened():
            print(f"Lỗi: Không thể mở camera {camera_id}")
            return
        
        action_type = "check-out" if is_checkout else "điểm danh"
        print(f"Bắt đầu {action_type} qua camera {camera_id}. Nhấn 'q' để kết thúc.")
        
        # Lấy danh sách người đã điểm danh hôm nay
        today_attendance = self.get_today_attendance()
        attended_users = list(today_attendance.keys())
        
        # Hiển thị thông tin về người đã điểm danh
        print(f"\nĐã có {len(attended_users)} người điểm danh hôm nay:")
        for user in attended_users:
            checkin_time = today_attendance[user].get('checkin', 'N/A')
            checkout_time = today_attendance[user].get('checkout', 'N/A')
            print(f"- {user} (Check-in: {checkin_time}, Check-out: {checkout_time})")
        
        process_this_frame = True
        confirmed_users = set()  # Set lưu những người đã được xác nhận điểm danh hoặc checkout
        
        while True:
            # Đọc frame từ webcam
            ret, frame = video_capture.read()
            
            if not ret:
                print("Lỗi: Không thể đọc hình ảnh từ webcam")
                break
                
            # Thêm thông tin điểm danh vào góc màn hình
            title = "CHECK-OUT" if is_checkout else "ĐIỂM DANH"
            cv2.putText(frame, f"{title}: {len(attended_users)}", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Hiển thị 3 người điểm danh gần đây nhất
            y_pos = 60
            for i, user in enumerate(attended_users[-3:]):
                checkin_time = today_attendance[user].get('checkin', 'N/A')
                checkout_time = today_attendance[user].get('checkout', 'N/A')
                status = f"CI: {checkin_time}, CO: {checkout_time}"
                cv2.putText(frame, f"{user} - {status}", (10, y_pos), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                y_pos += 25
            
            # Chỉ xử lý 1 frame, bỏ qua 1 frame để tối ưu hiệu năng
            if process_this_frame:
                # Thu nhỏ frame để xử lý nhanh hơn
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                
                # Chuyển từ BGR sang RGB
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
                            
                            # Nếu nhận dạng được người và chưa được xác nhận
                            if name != "Unknown" and name not in confirmed_users:
                                timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                                
                                if is_checkout:
                                    # Xử lý checkout
                                    if name in today_attendance and "checkout" not in today_attendance[name]:
                                        self.checkout(name, timestamp)
                                        # Thêm vào danh sách đã xác nhận
                                        confirmed_users.add(name)
                                        # Cập nhật danh sách
                                        today_attendance = self.get_today_attendance()
                                        # Thông báo
                                        print(f"Check-out thành công: {name} - {timestamp}")
                                else:
                                    # Xử lý check-in
                                    self.mark_attendance(name, timestamp)
                                    # Thêm vào danh sách đã xác nhận
                                    confirmed_users.add(name)
                                    # Cập nhật danh sách
                                    today_attendance = self.get_today_attendance()
                                    # Thông báo
                                    print(f"Điểm danh thành công: {name} - {timestamp}")
                                
                                # Cập nhật danh sách người đã điểm danh
                                attended_users = list(today_attendance.keys())
                    
                    face_names.append(name)
            
            process_this_frame = not process_this_frame
            
            # Hiển thị kết quả
            for (top, right, bottom, left), name in zip(face_locations, face_names):
                # Đổi kích thước vị trí về kích thước gốc
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4
                
                # Vẽ khung và tên
                if name == "Unknown":
                    color = (0, 0, 255)  # Đỏ cho người không xác định
                    status_text = "Unknown"
                else:
                    # Kiểm tra trạng thái điểm danh
                    if name in today_attendance:
                        if is_checkout:
                            # Đang trong chế độ check-out
                            if "checkout" in today_attendance[name]:
                                color = (0, 255, 0)  # Xanh lá cho người đã checkout
                                status_text = "Checkout completed"
                        else:
                            # Đang trong chế độ check-in
                            color = (0, 255, 0)  # Xanh lá cho người đã điểm danh
                            status_text = "Attendance confirmed"
                    else:
                        if is_checkout:
                            color = (0, 0, 255)  # Đỏ cho người chưa check-in
                            status_text = "No check-in record"
                        else:
                            color = (255, 165, 0)  # Cam cho người chưa điểm danh
                            status_text = "Processing..."
                        
                    # Vẽ khung và thông tin
                    cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                    cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_DUPLEX, 0.8, color, 2)
                    cv2.putText(frame, status_text, (left, bottom + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                    
                    # Nếu có thông tin người dùng, hiển thị thêm
                    if user_info and name in user_info:
                        info = user_info.get(name, {})
                        age = info.get("age", "N/A")
                        cv2.putText(frame, f"Age: {age}", (left, bottom + 45), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            # Hiển thị kết quả
            cv2.imshow('Attendance System', frame)
            
            # Nhấn 'q' để thoát
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
        # Dọn dẹp
        video_capture.release()
        cv2.destroyAllWindows()
        
        print(f"\nKết thúc phiên {action_type}!")
        return list(set(attended_users))  # Trả về danh sách không trùng lặp
        
    def calculate_duration(self, checkin, checkout):
        """Tính thời gian tham gia (giờ:phút:giây)"""
        if not checkin or not checkout:
            return "N/A"
        
        try:
            # Chuyển đổi chuỗi thời gian thành đối tượng time
            t1 = dt.strptime(checkin, "%H:%M:%S")
            t2 = dt.strptime(checkout, "%H:%M:%S")
            
            # Tính chênh lệch thời gian
            delta = t2 - t1
            
            # Đổi giây thành giờ:phút:giây
            hours, remainder = divmod(delta.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        except:
            return "Error"
    
    def export_to_excel(self, all_users, date=None, file_path=None):
        """Xuất báo cáo điểm danh ra file Excel"""
        if date is None:
            date = datetime.date.today().isoformat()
            
        # Tạo tên file mặc định nếu không được cung cấp
        if file_path is None:
            os.makedirs('reports', exist_ok=True)
            file_path = f"reports/attendance_report_{date}.xlsx"
        
        # Lấy dữ liệu điểm danh
        attendance_data = self.get_date_attendance(date)
        
        # Tạo danh sách dữ liệu cho DataFrame
        data = []
        
        # Thêm người đã điểm danh
        for name, info in attendance_data.items():
            checkin = info.get('checkin', 'N/A')
            checkout = info.get('checkout', 'N/A')
            duration = self.calculate_duration(checkin, checkout) if checkout != 'N/A' else 'Chưa checkout'
            data.append({
                'Họ và tên': name,
                'Trạng thái': 'Có mặt',
                'Thời gian Check-in': checkin,
                'Thời gian Check-out': checkout,
                'Thời lượng': duration
            })
        
        # Thêm người vắng mặt
        for name in self.get_absent_list(all_users, date):
            data.append({
                'Họ và tên': name,
                'Trạng thái': 'Vắng mặt',
                'Thời gian Check-in': 'N/A',
                'Thời gian Check-out': 'N/A',
                'Thời lượng': 'N/A'
            })
        
        # Tạo DataFrame
        df = pd.DataFrame(data)
        
        # Sắp xếp: người có mặt lên trước, sau đó theo thứ tự tên
        df = df.sort_values(by=['Trạng thái', 'Họ và tên'], ascending=[False, True])
        
        # Xuất ra file Excel
        try:
            df.to_excel(file_path, index=False, sheet_name=f'Điểm danh {date}')
            print(f"Đã xuất báo cáo ra file: {file_path}")
            return True
        except Exception as e:
            print(f"Lỗi khi xuất báo cáo: {e}")
            return False
    
    def display_attendance_report(self, all_users, date=None):
        """Hiển thị báo cáo điểm danh"""
        if date is None:
            date = datetime.date.today().isoformat()
            date_str = "hôm nay"
        else:
            date_str = date
        
        attendance_data = self.get_date_attendance(date)
        absent_list = self.get_absent_list(all_users, date)
        
        print(f"\n===== BÁO CÁO ĐIỂM DANH {date_str} =====")
        print(f"Tổng số: {len(set(all_users))} người")
        print(f"Có mặt: {len(attendance_data)} người")
        print(f"Vắng mặt: {len(absent_list)} người")
        
        print("\n----- DANH SÁCH CÓ MẶT -----")
        if attendance_data:
            for i, (name, info) in enumerate(attendance_data.items(), 1):
                checkin = info.get('checkin', 'N/A')
                checkout = info.get('checkout', 'N/A')
                duration = self.calculate_duration(checkin, checkout) if checkout != 'N/A' else 'Chưa checkout'
                print(f"{i}. {name} - Check-in: {checkin}, Check-out: {checkout}, Thời lượng: {duration}")
        else:
            print("(Không có)")
            
        print("\n----- DANH SÁCH VẮNG MẶT -----")
        if absent_list:
            for i, name in enumerate(absent_list, 1):
                print(f"{i}. {name}")
        else:
            print("(Không có)")
        
        print("============================")