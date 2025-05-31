"""
Ứng dụng GUI đơn giản cho hệ thống nhận diện khuôn mặt
Sử dụng Tkinter để tạo giao diện thân thiện với người dùng
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import cv2
from PIL import Image, ImageTk
import os
import datetime
import json

# Import các module từ dự án
from modules.face_loader import FaceEncoder
from modules.webcam import recognize_from_webcam
from modules.image_processor import recognize_from_image
from modules.attendance import AttendanceSystem

class SimpleFaceRecognitionApp:
    def __init__(self, root):
        """Khởi tạo ứng dụng"""
        self.root = root
        self.setup_window()
        
        # Khởi tạo các đối tượng xử lý
        self.encoder = FaceEncoder()
        self.attendance_system = AttendanceSystem()
        
        # Tạo giao diện
        self.create_interface()
        
        # Tải dữ liệu ban đầu
        self.load_initial_data()

    def setup_window(self):
        """Thiết lập cửa sổ chính"""
        self.root.title("🎯 Hệ Thống Nhận Diện Khuôn Mặt")
        self.root.geometry("900x600")
        self.root.configure(bg='#f0f0f0')
        
        # Đặt cửa sổ ở giữa màn hình
        self.center_window()
        
        # Xử lý sự kiện đóng cửa sổ
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def center_window(self):
        """Đặt cửa sổ ở giữa màn hình"""
        self.root.update_idletasks()
        width = 900
        height = 600
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def create_interface(self):
        """Tạo giao diện người dùng"""
        # Frame chính
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Tiêu đề
        title_label = ttk.Label(
            main_frame, 
            text="🎯 HỆ THỐNG NHẬN DIỆN KHUÔN MẶT", 
            font=("Arial", 18, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Thông tin hệ thống
        self.info_label = ttk.Label(
            main_frame,
            text="👥 Đang tải dữ liệu...",
            font=("Arial", 10)
        )
        self.info_label.pack(pady=(0, 20))
        
        # Tạo notebook cho các tab
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True)
        
        # Tab 1: Nhận diện
        self.create_recognition_tab()
        
        # Tab 2: Quản lý người dùng
        self.create_user_management_tab()
        
        # Tab 3: Điểm danh
        self.create_attendance_tab()
        
        # Tab 4: Báo cáo
        self.create_report_tab()
        
        # Thanh trạng thái
        self.status_label = ttk.Label(
            main_frame,
            text="🟢 Sẵn sàng",
            font=("Arial", 9)
        )
        self.status_label.pack(side="bottom", pady=(10, 0))

    def create_recognition_tab(self):
        """Tạo tab nhận diện"""
        recognition_frame = ttk.Frame(self.notebook)
        self.notebook.add(recognition_frame, text="🔍 Nhận Diện")
        
        # Frame cho các nút
        button_frame = ttk.LabelFrame(recognition_frame, text="Chọn phương thức nhận diện", padding="20")
        button_frame.pack(fill="x", padx=20, pady=20)
        
        # Nút nhận diện qua webcam
        webcam_btn = ttk.Button(
            button_frame,
            text="📷 Nhận Diện Qua Webcam",
            command=self.start_webcam_recognition,
            width=30
        )
        webcam_btn.pack(pady=10)
        
        # Nút nhận diện từ ảnh
        image_btn = ttk.Button(
            button_frame,
            text="🖼️ Nhận Diện Từ Ảnh",
            command=self.start_image_recognition,
            width=30
        )
        image_btn.pack(pady=10)
        
        # Frame hiển thị kết quả
        result_frame = ttk.LabelFrame(recognition_frame, text="Kết quả", padding="10")
        result_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.recognition_result = scrolledtext.ScrolledText(
            result_frame,
            wrap=tk.WORD,
            height=10,
            font=("Consolas", 9)
        )
        self.recognition_result.pack(fill="both", expand=True)

    def create_user_management_tab(self):
        """Tạo tab quản lý người dùng"""
        user_frame = ttk.Frame(self.notebook)
        self.notebook.add(user_frame, text="👥 Quản Lý Người Dùng")
        
        # Frame cho các nút
        button_frame = ttk.LabelFrame(user_frame, text="Chức năng", padding="20")
        button_frame.pack(fill="x", padx=20, pady=20)
        
        # Tạo grid cho các nút
        ttk.Button(
            button_frame,
            text="📋 Xem Danh Sách",
            command=self.view_users,
            width=25
        ).grid(row=0, column=0, padx=10, pady=5)
        
        ttk.Button(
            button_frame,
            text="➕ Thêm Người Dùng",
            command=self.add_user,
            width=25
        ).grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Button(
            button_frame,
            text="✏️ Sửa Thông Tin",
            command=self.edit_user,
            width=25
        ).grid(row=1, column=0, padx=10, pady=5)
        
        ttk.Button(
            button_frame,
            text="🗑️ Xóa Người Dùng",
            command=self.delete_user,
            width=25
        ).grid(row=1, column=1, padx=10, pady=5)
        
        # Frame hiển thị danh sách người dùng
        list_frame = ttk.LabelFrame(user_frame, text="Danh sách người dùng", padding="10")
        list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Treeview để hiển thị danh sách
        columns = ("Tên", "Tuổi", "Địa chỉ")
        self.user_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=8)
        
        for col in columns:
            self.user_tree.heading(col, text=col)
            self.user_tree.column(col, width=150)
        
        # Scrollbar cho treeview
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.user_tree.yview)
        self.user_tree.configure(yscrollcommand=scrollbar.set)
        
        self.user_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_attendance_tab(self):
        """Tạo tab điểm danh"""
        attendance_frame = ttk.Frame(self.notebook)
        self.notebook.add(attendance_frame, text="📊 Điểm Danh")
        
        # Frame cho các nút
        button_frame = ttk.LabelFrame(attendance_frame, text="Chức năng điểm danh", padding="20")
        button_frame.pack(fill="x", padx=20, pady=20)
        
        ttk.Button(
            button_frame,
            text="✅ Check-in",
            command=self.start_checkin,
            width=20
        ).pack(side="left", padx=10)
        
        ttk.Button(
            button_frame,
            text="📤 Check-out",
            command=self.start_checkout,
            width=20
        ).pack(side="left", padx=10)
        
        ttk.Button(
            button_frame,
            text="🔄 Tải Lại Dữ Liệu",
            command=self.reload_data,
            width=20
        ).pack(side="left", padx=10)
        
        # Frame hiển thị thông tin điểm danh hôm nay
        today_frame = ttk.LabelFrame(attendance_frame, text="Điểm danh hôm nay", padding="10")
        today_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.attendance_text = scrolledtext.ScrolledText(
            today_frame,
            wrap=tk.WORD,
            height=12,
            font=("Consolas", 9)
        )
        self.attendance_text.pack(fill="both", expand=True)

    def create_report_tab(self):
        """Tạo tab báo cáo"""
        report_frame = ttk.Frame(self.notebook)
        self.notebook.add(report_frame, text="📈 Báo Cáo")
        
        # Frame cho các tùy chọn
        options_frame = ttk.LabelFrame(report_frame, text="Tùy chọn báo cáo", padding="15")
        options_frame.pack(fill="x", padx=20, pady=20)
        
        # Chọn ngày
        ttk.Label(options_frame, text="Ngày:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.date_var = tk.StringVar(value=datetime.date.today().isoformat())
        date_entry = ttk.Entry(options_frame, textvariable=self.date_var, width=12)
        date_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Button(options_frame, text="Hôm nay", command=self.set_today).grid(row=0, column=2, padx=5, pady=5)
        
        # Các nút báo cáo
        ttk.Button(
            options_frame,
            text="📊 Xem Báo Cáo",
            command=self.show_report,
            width=15
        ).grid(row=1, column=0, padx=5, pady=10)
        
        ttk.Button(
            options_frame,
            text="📋 Xuất Excel",
            command=self.export_excel,
            width=15
        ).grid(row=1, column=1, padx=5, pady=10)
        
        # Frame hiển thị báo cáo
        report_display_frame = ttk.LabelFrame(report_frame, text="Báo cáo", padding="10")
        report_display_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.report_text = scrolledtext.ScrolledText(
            report_display_frame,
            wrap=tk.WORD,
            font=("Consolas", 9)
        )
        self.report_text.pack(fill="both", expand=True)

    def load_initial_data(self):
        """Tải dữ liệu ban đầu"""
        self.log_message("🚀 Đang khởi động hệ thống...")
        self.update_status("Đang tải dữ liệu...")
        
        def load_worker():
            try:
                # Tải dữ liệu khuôn mặt
                if not self.encoder.load_encodings():
                    if self.encoder.load_photos():
                        self.encoder.save_encodings()
                        self.root.after(0, lambda: self.log_message("✅ Đã tải dữ liệu từ ảnh"))
                    else:
                        self.root.after(0, lambda: self.log_message("❌ Không thể tải dữ liệu khuôn mặt"))
                else:
                    self.root.after(0, lambda: self.log_message("✅ Đã tải dữ liệu từ file encodings"))
                
                # Cập nhật giao diện
                self.root.after(0, self.update_user_info)
                self.root.after(0, self.refresh_user_list)
                self.root.after(0, self.refresh_attendance_today)
                self.root.after(0, lambda: self.update_status("🟢 Sẵn sàng"))
                self.root.after(0, lambda: self.log_message("🎉 Hệ thống sẵn sàng hoạt động!"))
                
            except Exception as e:
                self.root.after(0, lambda: self.log_message(f"❌ Lỗi khởi tạo: {str(e)}"))
                self.root.after(0, lambda: self.update_status("❌ Lỗi khởi tạo"))
        
        threading.Thread(target=load_worker, daemon=True).start()

    def log_message(self, message, target=None):
        """Ghi log message"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        if target is None:
            target = self.recognition_result
        
        target.insert(tk.END, log_entry)
        target.see(tk.END)

    def update_status(self, message):
        """Cập nhật trạng thái"""
        self.status_label.config(text=message)

    def update_user_info(self):
        """Cập nhật thông tin người dùng"""
        try:
            users = self.encoder.get_all_users()
            count = len(users)
            self.info_label.config(text=f"👥 {count} người dùng trong hệ thống")
        except:
            self.info_label.config(text="👥 0 người dùng trong hệ thống")

    # ==================== CHỨC NĂNG NHẬN DIỆN ====================

    def start_webcam_recognition(self):
        """Bắt đầu nhận diện qua webcam"""
        self.log_message("📷 Đang khởi động nhận diện qua webcam...")
        self.update_status("Đang mở webcam...")
        
        def worker():
            try:
                known_face_encodings, known_face_names = self.encoder.get_encodings()
                recognize_from_webcam(
                    known_face_encodings,
                    known_face_names,
                    self.encoder.get_all_users(),
                    camera_id=1
                )
                self.root.after(0, lambda: self.log_message("✅ Đã hoàn thành nhận diện qua webcam"))
                self.root.after(0, lambda: self.update_status("🟢 Sẵn sàng"))
            except Exception as e:
                self.root.after(0, lambda: self.log_message(f"❌ Lỗi webcam: {str(e)}"))
                self.root.after(0, lambda: self.update_status("❌ Lỗi webcam"))
        
        threading.Thread(target=worker, daemon=True).start()

    def start_image_recognition(self):
        """Bắt đầu nhận diện từ ảnh"""
        file_path = filedialog.askopenfilename(
            title="Chọn ảnh để nhận diện",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp *.gif"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        self.log_message(f"🖼️ Đang nhận diện ảnh: {os.path.basename(file_path)}")
        self.update_status("Đang xử lý ảnh...")
        
        def worker():
            try:
                known_face_encodings, known_face_names = self.encoder.get_encodings()
                recognize_from_image(
                    file_path,
                    known_face_encodings,
                    known_face_names,
                    self.encoder.get_all_users()
                )
                self.root.after(0, lambda: self.log_message("✅ Đã hoàn thành nhận diện ảnh"))
                self.root.after(0, lambda: self.update_status("🟢 Sẵn sàng"))
            except Exception as e:
                self.root.after(0, lambda: self.log_message(f"❌ Lỗi nhận diện ảnh: {str(e)}"))
                self.root.after(0, lambda: self.update_status("❌ Lỗi nhận diện"))
        
        threading.Thread(target=worker, daemon=True).start()

    # ==================== CHỨC NĂNG NGƯỜI DÙNG ====================

    def view_users(self):
        """Xem danh sách người dùng"""
        self.refresh_user_list()
        messagebox.showinfo("Thông báo", "Đã cập nhật danh sách người dùng")

    def refresh_user_list(self):
        """Làm mới danh sách người dùng"""
        # Xóa dữ liệu cũ
        for item in self.user_tree.get_children():
            self.user_tree.delete(item)
        
        # Thêm dữ liệu mới
        users = self.encoder.get_all_users()
        for name, info in users.items():
            age = info.get("age", "Chưa rõ")
            address = info.get("address", "Chưa rõ")
            self.user_tree.insert("", tk.END, values=(name, age, address))

    def add_user(self):
        """Thêm người dùng mới"""
        AddUserDialog(self.root, self.encoder, self.on_user_updated)

    def edit_user(self):
        """Sửa thông tin người dùng"""
        selection = self.user_tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một người dùng để sửa")
            return
        
        item = self.user_tree.item(selection[0])
        user_name = item['values'][0]
        EditUserDialog(self.root, self.encoder, user_name, self.on_user_updated)

    def delete_user(self):
        """Xóa người dùng"""
        selection = self.user_tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một người dùng để xóa")
            return
        
        item = self.user_tree.item(selection[0])
        user_name = item['values'][0]
        
        if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa người dùng '{user_name}'?\nHành động này không thể hoàn tác."):
            if self.encoder.delete_user(user_name):
                self.refresh_user_list()
                self.update_user_info()
                messagebox.showinfo("Thành công", f"Đã xóa người dùng '{user_name}'")
            else:
                messagebox.showerror("Lỗi", "Không thể xóa người dùng")

    def on_user_updated(self):
        """Callback khi có cập nhật người dùng"""
        self.refresh_user_list()
        self.update_user_info()

    # ==================== CHỨC NĂNG ĐIỂM DANH ====================

    def start_checkin(self):
        """Bắt đầu check-in"""
        self.start_attendance_process(is_checkout=False)

    def start_checkout(self):
        """Bắt đầu check-out"""
        self.start_attendance_process(is_checkout=True)

    def start_attendance_process(self, is_checkout=False):
        """Xử lý điểm danh"""
        action = "check-out" if is_checkout else "check-in"
        self.log_message(f"📊 Bắt đầu {action}", self.attendance_text)
        self.update_status(f"Đang thực hiện {action}...")
        
        def worker():
            try:
                known_face_encodings, known_face_names = self.encoder.get_encodings()
                self.attendance_system.take_attendance_webcam(
                    known_face_encodings,
                    known_face_names,
                    self.encoder.get_all_users(),
                    is_checkout=is_checkout,
                    camera_id=1
                )
                self.root.after(0, lambda: self.log_message(f"✅ Hoàn thành {action}", self.attendance_text))
                self.root.after(0, lambda: self.update_status("🟢 Sẵn sàng"))
                self.root.after(0, self.refresh_attendance_today)
            except Exception as e:
                self.root.after(0, lambda: self.log_message(f"❌ Lỗi {action}: {str(e)}", self.attendance_text))
                self.root.after(0, lambda: self.update_status("❌ Lỗi điểm danh"))
        
        threading.Thread(target=worker, daemon=True).start()

    def refresh_attendance_today(self):
        """Làm mới dữ liệu điểm danh hôm nay"""
        self.attendance_text.delete("1.0", tk.END)
        
        today_data = self.attendance_system.get_today_attendance()
        
        self.log_message("📊 ĐIỂM DANH HÔM NAY", self.attendance_text)
        self.log_message("=" * 50, self.attendance_text)
        
        if not today_data:
            self.log_message("Chưa có ai điểm danh hôm nay", self.attendance_text)
            return
        
        for name, info in today_data.items():
            checkin = info.get('checkin', 'Chưa check-in')
            checkout = info.get('checkout', 'Chưa check-out')
            self.log_message(f"👤 {name}: Check-in {checkin}, Check-out {checkout}", self.attendance_text)

    def reload_data(self):
        """Tải lại dữ liệu"""
        self.load_initial_data()

    # ==================== CHỨC NĂNG BÁO CÁO ====================

    def set_today(self):
        """Đặt ngày hôm nay"""
        self.date_var.set(datetime.date.today().isoformat())

    def show_report(self):
        """Hiển thị báo cáo"""
        date = self.date_var.get()
        try:
            datetime.date.fromisoformat(date)
        except ValueError:
            messagebox.showerror("Lỗi", "Định dạng ngày không hợp lệ. Vui lòng sử dụng định dạng YYYY-MM-DD")
            return
        
        self.report_text.delete("1.0", tk.END)
        
        # Lấy dữ liệu điểm danh
        attendance_data = self.attendance_system.get_date_attendance(date)
        absent_list = self.attendance_system.get_absent_list(self.encoder.get_unique_users(), date)
        
        # Hiển thị báo cáo
        self.log_message(f"📊 BÁO CÁO ĐIỂM DANH NGÀY {date}", self.report_text)
        self.log_message("=" * 50, self.report_text)
        self.log_message(f"Tổng số: {len(self.encoder.get_unique_users())} người", self.report_text)
        self.log_message(f"Có mặt: {len(attendance_data)} người", self.report_text)
        self.log_message(f"Vắng mặt: {len(absent_list)} người", self.report_text)
        self.log_message("", self.report_text)
        
        # Danh sách có mặt
        self.log_message("📋 DANH SÁCH CÓ MẶT:", self.report_text)
        if attendance_data:
            for i, (name, info) in enumerate(attendance_data.items(), 1):
                checkin = info.get('checkin', 'N/A')
                checkout = info.get('checkout', 'N/A')
                self.log_message(f"{i}. {name} - Check-in: {checkin}, Check-out: {checkout}", self.report_text)
        else:
            self.log_message("(Không có)", self.report_text)
        
        self.log_message("", self.report_text)
        
        # Danh sách vắng mặt
        self.log_message("❌ DANH SÁCH VẮNG MẶT:", self.report_text)
        if absent_list:
            for i, name in enumerate(absent_list, 1):
                self.log_message(f"{i}. {name}", self.report_text)
        else:
            self.log_message("(Không có)", self.report_text)

    def export_excel(self):
        """Xuất báo cáo ra Excel"""
        date = self.date_var.get()
        try:
            datetime.date.fromisoformat(date)
        except ValueError:
            messagebox.showerror("Lỗi", "Định dạng ngày không hợp lệ. Vui lòng sử dụng định dạng YYYY-MM-DD")
            return
        
        if self.attendance_system.export_to_excel(self.encoder.get_unique_users(), date):
            messagebox.showinfo("Thành công", f"Đã xuất báo cáo cho ngày {date}")
        else:
            messagebox.showerror("Lỗi", "Không thể xuất báo cáo")

    def on_closing(self):
        """Xử lý khi đóng ứng dụng"""
        if messagebox.askyesno("Xác nhận", "Bạn có muốn thoát ứng dụng?"):
            self.root.destroy()


class AddUserDialog:
    """Dialog thêm người dùng mới"""
    def __init__(self, parent, encoder, callback):
        self.encoder = encoder
        self.callback = callback
        
        self.window = tk.Toplevel(parent)
        self.window.title("➕ Thêm Người Dùng Mới")
        self.window.geometry("400x350")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_widgets()

    def create_widgets(self):
        """Tạo các widget"""
        # Frame chính
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Thông tin người dùng
        ttk.Label(main_frame, text="Tên:").grid(row=0, column=0, sticky="w", pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.name_var, width=30).grid(row=0, column=1, pady=5, padx=(10, 0))
        
        ttk.Label(main_frame, text="Tuổi:").grid(row=1, column=0, sticky="w", pady=5)
        self.age_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.age_var, width=30).grid(row=1, column=1, pady=5, padx=(10, 0))
        
        ttk.Label(main_frame, text="Địa chỉ:").grid(row=2, column=0, sticky="w", pady=5)
        self.address_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.address_var, width=30).grid(row=2, column=1, pady=5, padx=(10, 0))
        
        # Phương thức thêm
        method_frame = ttk.LabelFrame(main_frame, text="Phương thức", padding="10")
        method_frame.grid(row=3, column=0, columnspan=2, pady=20, sticky="ew")
        
        self.method_var = tk.StringVar(value="webcam")
        ttk.Radiobutton(method_frame, text="📷 Webcam", variable=self.method_var, value="webcam").pack(anchor="w")
        ttk.Radiobutton(method_frame, text="📁 File ảnh", variable=self.method_var, value="file").pack(anchor="w")
        
        # Nút
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="➕ Thêm", command=self.add_user).pack(side="left", padx=5)
        ttk.Button(button_frame, text="❌ Hủy", command=self.window.destroy).pack(side="left", padx=5)

    def add_user(self):
        """Thêm người dùng"""
        name = self.name_var.get().strip()
        age = self.age_var.get().strip()
        address = self.address_var.get().strip()
        
        if not name:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập tên người dùng")
            return
        
        self.window.destroy()
        
        def worker():
            try:
                if self.method_var.get() == "webcam":
                    success = self.encoder.add_user_from_webcam(name, age, address, num_photos=3)
                else:
                    file_path = filedialog.askopenfilename(
                        title="Chọn ảnh người dùng",
                        filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")]
                    )
                    if file_path:
                        success = self.encoder.add_user_from_image(file_path, name, age, address)
                    else:
                        return
                
                if success:
                    messagebox.showinfo("Thành công", f"Đã thêm người dùng '{name}' thành công!")
                    self.callback()
                else:
                    messagebox.showerror("Lỗi", f"Không thể thêm người dùng '{name}'")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi thêm người dùng: {str(e)}")
        
        threading.Thread(target=worker, daemon=True).start()


class EditUserDialog:
    """Dialog sửa thông tin người dùng"""
    def __init__(self, parent, encoder, user_name, callback):
        self.encoder = encoder
        self.user_name = user_name
        self.callback = callback
        
        self.window = tk.Toplevel(parent)
        self.window.title(f"✏️ Sửa Thông Tin: {user_name}")
        self.window.geometry("400x250")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_widgets()

    def create_widgets(self):
        """Tạo các widget"""
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Lấy thông tin hiện tại
        current_info = self.encoder.get_user_info(self.user_name) or {}
        
        # Thông tin người dùng
        ttk.Label(main_frame, text="Tên:").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Label(main_frame, text=self.user_name, font=("Arial", 10, "bold")).grid(row=0, column=1, sticky="w", pady=5, padx=(10, 0))
        
        ttk.Label(main_frame, text="Tuổi:").grid(row=1, column=0, sticky="w", pady=5)
        self.age_var = tk.StringVar(value=current_info.get("age", ""))
        ttk.Entry(main_frame, textvariable=self.age_var, width=30).grid(row=1, column=1, pady=5, padx=(10, 0))
        
        ttk.Label(main_frame, text="Địa chỉ:").grid(row=2, column=0, sticky="w", pady=5)
        self.address_var = tk.StringVar(value=current_info.get("address", ""))
        ttk.Entry(main_frame, textvariable=self.address_var, width=30).grid(row=2, column=1, pady=5, padx=(10, 0))
        
        # Nút
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="💾 Lưu", command=self.save_changes).pack(side="left", padx=5)
        ttk.Button(button_frame, text="❌ Hủy", command=self.window.destroy).pack(side="left", padx=5)

    def save_changes(self):
        """Lưu thay đổi"""
        age = self.age_var.get().strip()
        address = self.address_var.get().strip()
        
        if self.encoder.update_user_info(self.user_name, age, address):
            messagebox.showinfo("Thành công", f"Đã cập nhật thông tin cho '{self.user_name}'")
            self.callback()
            self.window.destroy()
        else:
            messagebox.showerror("Lỗi", "Không thể cập nhật thông tin người dùng")


def main():
    """Hàm main chạy ứng dụng"""
    try:
        root = tk.Tk()
        app = SimpleFaceRecognitionApp(root)
        root.mainloop()
    except Exception as e:
        print(f"Lỗi khởi động ứng dụng: {str(e)}")


if __name__ == "__main__":
    main()