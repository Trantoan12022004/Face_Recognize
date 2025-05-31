"""
Module quản lý người dùng trong hệ thống nhận diện khuôn mặt
"""

def display_user_management_menu():
    """Hiển thị menu quản lý người dùng"""
    print("\nUser Management:")
    print("1. View all users")
    print("2. Update user information")
    print("3. Add new user")
    print("4. Delete user")  # Tùy chọn mới
    print("5. Return to main menu")

def view_all_users(encoder):
    """Xem danh sách tất cả người dùng"""
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
    """Cập nhật thông tin người dùng"""
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
        
        success = encoder.add_user_from_webcam(user_name, age, address, num_photos)
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

def delete_user(encoder):
    """Xóa người dùng khỏi hệ thống"""
    print("\n===== Delete User =====")
    
    # Show available users first
    view_all_users(encoder)
    
    # If no users, exit function
    if not encoder.get_all_users():
        return
    
    # Get user to delete
    name = input("\nEnter user name to delete: ")
    
    # Check if user exists
    all_users = encoder.get_all_users()
    if name not in all_users and name not in encoder.known_face_names:
        print(f"User '{name}' not found in database.")
        return
    
    # Confirm deletion
    confirm = input(f"Are you sure you want to delete user '{name}'? This cannot be undone (y/n): ")
    if confirm.lower() != 'y':
        print("Deletion cancelled.")
        return
        
    # Delete the user
    if encoder.delete_user(name):
        print(f"User '{name}' has been deleted successfully.")
    else:
        print(f"Failed to delete user '{name}'.")

def user_management_menu(encoder):
    """Menu chính quản lý người dùng"""
    while True:
        display_user_management_menu()
        choice = input("Choose an option (1-5): ")
        
        if choice == '1':
            view_all_users(encoder)
        elif choice == '2':
            update_user_info(encoder)
        elif choice == '3':
            add_new_user(encoder)
        elif choice == '4':
            delete_user(encoder)
        elif choice == '5':
            print("Returning to main menu...")
            break
        else:
            print("Invalid choice. Please try again.")