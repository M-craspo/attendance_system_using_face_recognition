import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import face_recognition
import os
import shutil
from datetime import datetime
import PIL.Image
import PIL.ImageTk

class RegistrationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("User Registration System")
        
        # Set window size and position
        window_width = 800
        window_height = 600
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        
        # Image directory
        self.IMAGE_DIR = "/Users/mahmoudahmed/Desktop/face_recognition/images"
        if not os.path.exists(self.IMAGE_DIR):
            os.makedirs(self.IMAGE_DIR)
            
        # Variables
        self.image_path = None
        self.photo = None  # Keep reference to avoid garbage collection
        
        self.create_widgets()
        self.load_existing_users()

    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Left side - Registration Form
        form_frame = ttk.LabelFrame(main_frame, text="Registration Form", padding="10")
        form_frame.grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # User Code
        ttk.Label(form_frame, text="User Code:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.user_code_var = tk.StringVar()
        self.user_code_entry = ttk.Entry(form_frame, textvariable=self.user_code_var)
        self.user_code_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Name
        ttk.Label(form_frame, text="Name:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(form_frame, textvariable=self.name_var)
        self.name_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Image Preview
        self.preview_label = ttk.Label(form_frame, text="No image selected")
        self.preview_label.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Select Image", command=self.select_image).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Register", command=self.register_user).grid(row=0, column=1, padx=5)
        
        # Right side - User List
        list_frame = ttk.LabelFrame(main_frame, text="Registered Users", padding="10")
        list_frame.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Treeview for user list
        self.tree = ttk.Treeview(list_frame, columns=('Name', 'Code'), show='headings')
        self.tree.heading('Name', text='Name')
        self.tree.heading('Code', text='User Code')
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Delete button
        ttk.Button(list_frame, text="Delete Selected", command=self.delete_user).grid(row=1, column=0, pady=5)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

    def load_existing_users(self):
        """Load existing users into the treeview"""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for filename in os.listdir(self.IMAGE_DIR):
            if filename.endswith(('.jpg', '.jpeg', '.png')):
                name = os.path.splitext(filename)[0]
                user_code = name.split('_')[-1]
                display_name = name.replace(f"_{user_code}", "")
                self.tree.insert('', 'end', values=(display_name, user_code))

    def validate_face_image(self, image_path):
        """Validate if the image contains exactly one face"""
        try:
            image = cv2.imread(image_path)
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_image)
            
            if len(face_locations) == 0:
                messagebox.showerror("Error", "No face detected in the image")
                return False
            elif len(face_locations) > 1:
                messagebox.showerror("Error", "Multiple faces detected. Please upload an image with a single face")
                return False
            
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Error processing image: {str(e)}")
            return False

    def select_image(self):
        """Handle image selection"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png")]
        )
        if file_path:
            self.image_path = file_path
            # Show image preview
            image = PIL.Image.open(file_path)
            image.thumbnail((200, 200))  # Resize for preview
            photo = PIL.ImageTk.PhotoImage(image)
            self.photo = photo  # Keep reference
            self.preview_label.configure(image=photo, text="")

    def register_user(self):
        """Handle user registration"""
        if not self.image_path:
            messagebox.showerror("Error", "Please select an image")
            return
            
        user_code = self.user_code_var.get().strip()
        name = self.name_var.get().strip()
        
        if not user_code:
            messagebox.showerror("Error", "Please enter a user code")
            return
            
        if not user_code.isalnum() or len(user_code) < 4:
            messagebox.showerror("Error", "User code must be alphanumeric and at least 4 characters long")
            return
            
        # Validate image
        if not self.validate_face_image(self.image_path):
            return
            
        # Create filename
        filename = f"{user_code}.jpg"
        destination = os.path.join(self.IMAGE_DIR, filename)
        
        # Check if user already exists
        if os.path.exists(destination):
            messagebox.showerror("Error", "User with this code already exists")
            return
            
        try:
            # Copy image to destination
            shutil.copy2(self.image_path, destination)
            
            # Log registration
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "user_code": user_code,
                "name": name or user_code,
                "file_path": destination
            }
            
            with open(os.path.join(self.IMAGE_DIR, "registration_log.txt"), "a") as log_file:
                log_file.write(f"{str(log_entry)}\n")
            
            # Clear form
            self.user_code_var.set("")
            self.name_var.set("")
            self.image_path = None
            self.preview_label.configure(image="", text="No image selected")
            
            # Refresh user list
            self.load_existing_users()
            
            messagebox.showinfo("Success", "User registered successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error registering user: {str(e)}")

    def delete_user(self):
        """Delete selected user"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a user to delete")
            return
            
        user = self.tree.item(selected_item[0])['values']
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete user {user[0]}?"):
            try:
                # Find and delete the user's image file
                user_code = user[1]
                for filename in os.listdir(self.IMAGE_DIR):
                    if filename.endswith(('.jpg', '.jpeg', '.png')) and f"_{user_code}." in filename:
                        os.remove(os.path.join(self.IMAGE_DIR, filename))
                        break
                
                # Refresh user list
                self.load_existing_users()
                messagebox.showinfo("Success", "User deleted successfully")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting user: {str(e)}")

def main():
    root = tk.Tk()
    app = RegistrationApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()