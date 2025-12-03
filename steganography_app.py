import customtkinter as ctk
from tkinter import filedialog, messagebox
from cryptography.fernet import Fernet
from PIL import Image, ImageTk
import smtplib
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import threading
import subprocess
import webbrowser
import http.server
import socketserver
import sys
import os


# Color Palette
COLORS = {
    "bg_primary": "#1a1a1a",
    "bg_secondary": "#2b2b2b",
    "text_primary": "#e0e0e0",
    "text_secondary": "#a0a0a0",
    "accent": "#00D9FF",
    "success": "#00FF88",
    "error": "#FF4444",
    "border": "#404040"
}


class SteganographyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("StegoExpress - Image Steganography Tool")
        self.root.geometry("1000x750")
        
        # Set appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Variables
        self.image_path = ctk.StringVar()
        self.generated_key = ctk.StringVar()
        self.stego_image_path = None
        
        # Main container
        self.main_frame = ctk.CTkFrame(self.root, fg_color=COLORS["bg_primary"])
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title_label = ctk.CTkLabel(
            self.main_frame,
            text="🔒 StegoExpress - Image Steganography Tool",
            font=("Helvetica", 24, "bold"),
            text_color=COLORS["accent"]
        )
        title_label.pack(pady=(10, 20))
        
        # Tabview for Hide/Extract modes
        self.tabview = ctk.CTkTabview(self.main_frame, fg_color=COLORS["bg_secondary"])
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create tabs
        self.tab_hide = self.tabview.add("🔐 Hide Message")
        self.tab_extract = self.tabview.add("🔓 Extract Message")
        
        # Build UI for each tab
        self.build_hide_tab()
        self.build_extract_tab()
        
        # Status bar
        self.status_frame = ctk.CTkFrame(self.main_frame, fg_color=COLORS["bg_secondary"], height=40)
        self.status_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Ready",
            font=("Arial", 11),
            text_color=COLORS["text_secondary"],
            anchor="w"
        )
        self.status_label.pack(side="left", padx=10, pady=5)
        
    def build_hide_tab(self):
        """Build the Hide Message tab UI"""
        # Create scrollable frame for all content
        scrollable_frame = ctk.CTkScrollableFrame(
            self.tab_hide, 
            fg_color=COLORS["bg_primary"],
            scrollbar_button_color=COLORS["accent"],
            scrollbar_button_hover_color="#0099CC"
        )
        scrollable_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Image selection section
        image_frame = ctk.CTkFrame(scrollable_frame, fg_color=COLORS["bg_secondary"])
        image_frame.pack(fill="x", padx=15, pady=(5, 5))
        
        ctk.CTkLabel(
            image_frame,
            text="Select Cover Image:",
            font=("Arial", 13, "bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left", padx=10, pady=10)
        
        self.hide_image_entry = ctk.CTkEntry(
            image_frame,
            textvariable=self.image_path,
            width=400,
            height=35,
            font=("Arial", 11)
        )
        self.hide_image_entry.pack(side="left", padx=10, pady=10)
        
        ctk.CTkButton(
            image_frame,
            text="Browse",
            command=self.browse_hide_image,
            width=100,
            height=35,
            fg_color=COLORS["accent"],
            hover_color="#0099CC",
            font=("Arial", 12, "bold")
        ).pack(side="left", padx=10, pady=10)
        
        # Image preview
        preview_frame = ctk.CTkFrame(scrollable_frame, fg_color=COLORS["bg_secondary"])
        preview_frame.pack(fill="x", padx=15, pady=5)
        
        self.hide_preview_label = ctk.CTkLabel(
            preview_frame,
            text="📷 Image Preview\n\nNo image selected",
            font=("Arial", 14),
            text_color=COLORS["text_secondary"]
        )
        self.hide_preview_label.pack(pady=20)
        
        # Message input
        message_frame = ctk.CTkFrame(scrollable_frame, fg_color=COLORS["bg_secondary"])
        message_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(
            message_frame,
            text="Secret Message:",
            font=("Arial", 13, "bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left", padx=10, pady=10)
        
        self.message_entry = ctk.CTkEntry(
            message_frame,
            width=500,
            height=35,
            placeholder_text="Enter your secret message here...",
            font=("Arial", 11)
        )
        self.message_entry.pack(side="left", padx=10, pady=10, fill="x", expand=True)
        
        # Encrypt button
        ctk.CTkButton(
            scrollable_frame,
            text="🔐 Encrypt Message",
            command=self.encrypt_action,
            width=200,
            height=40,
            fg_color=COLORS["accent"],
            hover_color="#0099CC",
            font=("Arial", 14, "bold")
        ).pack(pady=10)
        
        # Key display section (initially hidden)
        self.key_frame = ctk.CTkFrame(scrollable_frame, fg_color=COLORS["bg_secondary"])
        self.key_frame.pack(fill="x", padx=15, pady=5)
        self.key_frame.pack_forget()  # Hide initially
        
        ctk.CTkLabel(
            self.key_frame,
            text="🔑 Encryption Key (Save this!):",
            font=("Arial", 13, "bold"),
            text_color=COLORS["success"]
        ).pack(side="left", padx=10, pady=10)
        
        self.key_display = ctk.CTkEntry(
            self.key_frame,
            textvariable=self.generated_key,
            width=400,
            height=35,
            font=("Arial", 10),
            state="readonly"
        )
        self.key_display.pack(side="left", padx=10, pady=10)
        
        ctk.CTkButton(
            self.key_frame,
            text="📋 Copy Key",
            command=self.copy_key_to_clipboard,
            width=100,
            height=35,
            fg_color=COLORS["success"],
            hover_color="#00CC66",
            font=("Arial", 12, "bold")
        ).pack(side="left", padx=10, pady=10)
        
        # Email section (initially hidden)
        self.email_frame = ctk.CTkFrame(scrollable_frame, fg_color=COLORS["bg_secondary"])
        self.email_frame.pack(fill="x", padx=15, pady=5)
        self.email_frame.pack_forget()  # Hide initially
        
        ctk.CTkLabel(
            self.email_frame,
            text="📧 Email Configuration (Optional)",
            font=("Arial", 13, "bold"),
            text_color=COLORS["accent"]
        ).pack(pady=(10, 5))
        
        # Sender email
        sender_frame = ctk.CTkFrame(self.email_frame, fg_color="transparent")
        sender_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(sender_frame, text="Sender Email:", width=120, anchor="w").pack(side="left", padx=5)
        self.sender_email_entry = ctk.CTkEntry(sender_frame, width=300, height=30)
        self.sender_email_entry.pack(side="left", padx=5)
        
        # Sender password
        password_frame = ctk.CTkFrame(self.email_frame, fg_color="transparent")
        password_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(password_frame, text="Sender Password:", width=120, anchor="w").pack(side="left", padx=5)
        self.sender_password_entry = ctk.CTkEntry(password_frame, width=300, height=30, show="*")
        self.sender_password_entry.pack(side="left", padx=5)
        
        # Recipient email
        recipient_frame = ctk.CTkFrame(self.email_frame, fg_color="transparent")
        recipient_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(recipient_frame, text="Recipient Email:", width=120, anchor="w").pack(side="left", padx=5)
        self.recipient_email_entry = ctk.CTkEntry(recipient_frame, width=300, height=30)
        self.recipient_email_entry.pack(side="left", padx=5)
        
        # Send button
        ctk.CTkButton(
            self.email_frame,
            text="📤 Send via Email",
            command=self.send_email_action,
            width=200,
            height=35,
            fg_color=COLORS["accent"],
            hover_color="#0099CC",
            font=("Arial", 12, "bold")
        ).pack(pady=10)
        
        
    def build_extract_tab(self):
        """Build the Extract Message tab UI"""
        # Create scrollable frame for all content
        scrollable_frame = ctk.CTkScrollableFrame(
            self.tab_extract, 
            fg_color=COLORS["bg_primary"],
            scrollbar_button_color=COLORS["accent"],
            scrollbar_button_hover_color="#0099CC"
        )
        scrollable_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Image selection section
        image_frame = ctk.CTkFrame(scrollable_frame, fg_color=COLORS["bg_secondary"])
        image_frame.pack(fill="x", padx=15, pady=(5, 5))
        
        ctk.CTkLabel(
            image_frame,
            text="Select Stego-Image:",
            font=("Arial", 13, "bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left", padx=10, pady=10)
        
        self.extract_image_path = ctk.StringVar()
        self.extract_image_entry = ctk.CTkEntry(
            image_frame,
            textvariable=self.extract_image_path,
            width=400,
            height=35,
            font=("Arial", 11)
        )
        self.extract_image_entry.pack(side="left", padx=10, pady=10)
        
        ctk.CTkButton(
            image_frame,
            text="Browse",
            command=self.browse_extract_image,
            width=100,
            height=35,
            fg_color=COLORS["accent"],
            hover_color="#0099CC",
            font=("Arial", 12, "bold")
        ).pack(side="left", padx=10, pady=10)
        
        # Image preview
        preview_frame = ctk.CTkFrame(scrollable_frame, fg_color=COLORS["bg_secondary"])
        preview_frame.pack(fill="x", padx=15, pady=5)
        
        self.extract_preview_label = ctk.CTkLabel(
            preview_frame,
            text="📷 Image Preview\n\nNo image selected",
            font=("Arial", 14),
            text_color=COLORS["text_secondary"]
        )
        self.extract_preview_label.pack(pady=20)
        
        # Key input
        key_frame = ctk.CTkFrame(scrollable_frame, fg_color=COLORS["bg_secondary"])
        key_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(
            key_frame,
            text="🔑 Decryption Key:",
            font=("Arial", 13, "bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left", padx=10, pady=10)
        
        self.decrypt_key_entry = ctk.CTkEntry(
            key_frame,
            width=500,
            height=35,
            placeholder_text="Paste your decryption key here...",
            font=("Arial", 11)
        )
        self.decrypt_key_entry.pack(side="left", padx=10, pady=10, fill="x", expand=True)
        
        # Decrypt button
        ctk.CTkButton(
            scrollable_frame,
            text="🔓 Decrypt Message",
            command=self.decrypt_action,
            width=200,
            height=40,
            fg_color=COLORS["accent"],
            hover_color="#0099CC",
            font=("Arial", 14, "bold")
        ).pack(pady=10)
        
        # Decrypted message display
        result_frame = ctk.CTkFrame(scrollable_frame, fg_color=COLORS["bg_secondary"])
        result_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(
            result_frame,
            text="📝 Decrypted Message:",
            font=("Arial", 13, "bold"),
            text_color=COLORS["success"]
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.decrypted_message_box = ctk.CTkTextbox(
            result_frame,
            height=150,
            font=("Arial", 12),
            wrap="word"
        )
        self.decrypted_message_box.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        
        
    def browse_hide_image(self):
        """Browse and select image for hiding message"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg")]
        )
        if file_path:
            self.image_path.set(file_path)
            self.update_image_preview(file_path, self.hide_preview_label)
            self.update_status(f"Selected: {os.path.basename(file_path)}", COLORS["success"])
            
    def browse_extract_image(self):
        """Browse and select stego-image for extraction"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg")]
        )
        if file_path:
            self.extract_image_path.set(file_path)
            self.update_image_preview(file_path, self.extract_preview_label)
            self.update_status(f"Selected: {os.path.basename(file_path)}", COLORS["success"])
            
    def update_image_preview(self, image_path, label_widget):
        """Update image preview in the specified label"""
        try:
            image = Image.open(image_path)
            image.thumbnail((500, 400))
            photo = ImageTk.PhotoImage(image)
            label_widget.configure(image=photo, text="")
            label_widget.image = photo
        except Exception as e:
            self.update_status(f"Failed to load image: {str(e)}", COLORS["error"])
            
    def encrypt_action(self):
        """Encrypt message and embed in image"""
        image_file = self.image_path.get()
        message = self.message_entry.get()
        
        if not image_file or not message:
            messagebox.showerror("Error", "Please select an image and enter a message.")
            return
            
        try:
            self.update_status("Encrypting message...", COLORS["accent"])
            
            # Generate encryption key
            key = Fernet.generate_key()
            f = Fernet(key)
            secret_message = f.encrypt(message.encode())
            
            # Open the image
            image = Image.open(image_file)
            pixels = list(image.getdata())
            
            # Convert encrypted message to binary
            binary_secret = "".join(format(byte, "08b") for byte in secret_message)
            new_pixels = []
            pixel_index = 0
            
            # Embed binary data into LSB
            for pixel in pixels:
                r, g, b = pixel
                if pixel_index < len(binary_secret):
                    r = r & 0xFE | int(binary_secret[pixel_index])
                    pixel_index += 1
                if pixel_index < len(binary_secret):
                    g = g & 0xFE | int(binary_secret[pixel_index])
                    pixel_index += 1
                if pixel_index < len(binary_secret):
                    b = b & 0xFE | int(binary_secret[pixel_index])
                    pixel_index += 1
                new_pixels.append((r, g, b))
                
            image.putdata(new_pixels)
            output_image_path = f"{os.path.splitext(os.path.basename(image_file))[0]}_stego.png"
            image.save(output_image_path, "PNG")
            self.stego_image_path = output_image_path
            
            # Display key and show email section
            self.generated_key.set(key.decode())
            self.key_frame.pack(fill="x", padx=20, pady=5)
            self.email_frame.pack(fill="x", padx=20, pady=5)
            
            # Update preview with stego image
            self.update_image_preview(output_image_path, self.hide_preview_label)
            
            self.update_status(f"✓ Message encrypted successfully! Stego-image saved: {output_image_path}", COLORS["success"])
            messagebox.showinfo("Success", f"Message encrypted!\n\nStego-image saved as: {output_image_path}\n\nPlease save your encryption key!")
            
        except Exception as e:
            self.update_status(f"Encryption failed: {str(e)}", COLORS["error"])
            messagebox.showerror("Error", f"Encryption failed: {str(e)}")
            
    def copy_key_to_clipboard(self):
        """Copy encryption key to clipboard"""
        key = self.generated_key.get()
        if key:
            self.root.clipboard_clear()
            self.root.clipboard_append(key)
            self.update_status("✓ Key copied to clipboard!", COLORS["success"])
            messagebox.showinfo("Success", "Encryption key copied to clipboard!")
                
    def send_email_action(self):
        """Send stego-image via email"""
        sender_email = self.sender_email_entry.get()
        sender_password = self.sender_password_entry.get()
        recipient_email = self.recipient_email_entry.get()
        
        if not all([sender_email, sender_password, recipient_email]):
            messagebox.showerror("Error", "Please fill in all email fields.")
            return
            
        if not self.stego_image_path:
            messagebox.showerror("Error", "Please encrypt a message first.")
            return
            
        try:
            self.update_status("Sending email...", COLORS["accent"])
            self.send_email(
                self.stego_image_path,
                self.generated_key.get(),
                sender_email,
                sender_password,
                recipient_email
            )
            self.update_status(f"✓ Email sent to {recipient_email}", COLORS["success"])
            messagebox.showinfo("Success", f"Stego-image and key sent to {recipient_email}!")
            
        except Exception as e:
            self.update_status(f"Email failed: {str(e)}", COLORS["error"])
            messagebox.showerror("Error", f"Failed to send email: {str(e)}")
            
    def send_email(self, image_path, key, sender_email, sender_password, recipient_email):
        """Send email with stego-image attachment"""
        try:
            msg = MIMEMultipart()
            msg["From"] = sender_email
            msg["To"] = recipient_email
            msg["Subject"] = "StegoExpress - Encrypted Image"
            
            body = f"You have received an encrypted image via StegoExpress.\n\nEncryption Key: {key}\n\nPlease save this key to decrypt the hidden message."
            msg.attach(MIMEText(body, "plain"))
            
            # Attach image
            with open(image_path, "rb") as image_attachment:
                img_base = MIMEBase("application", "octet-stream")
                img_base.set_payload(image_attachment.read())
                encoders.encode_base64(img_base)
                img_base.add_header(
                    "Content-Disposition",
                    f'attachment; filename="{os.path.basename(image_path)}"'
                )
                msg.attach(img_base)
                
            # Send email
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
            server.quit()
            
        except Exception as e:
            raise Exception(f"Email sending failed: {str(e)}")
            
    def decrypt_action(self):
        """Decrypt message from stego-image"""
        encrypted_image_path = self.extract_image_path.get()
        key = self.decrypt_key_entry.get()
        
        if not encrypted_image_path or not key:
            messagebox.showerror("Error", "Please select an image and provide the decryption key.")
            return
            
        # Run in thread to keep UI responsive
        threading.Thread(target=self.perform_decryption, args=(encrypted_image_path, key), daemon=True).start()
        
    def perform_decryption(self, encrypted_image_path, key):
        """Perform decryption in background thread"""
        try:
            self.root.after(0, self.update_status, "Decrypting message...", COLORS["accent"])
            
            # Convert key to bytes
            f = Fernet(key.encode())
            
            # Open encrypted image
            encoded_image = Image.open(encrypted_image_path)
            pixels = list(encoded_image.getdata())
            
            # Extract binary data from LSB
            binary_secret = ''
            for pixel in pixels:
                r, g, b = pixel
                binary_secret += str(r & 1)
                binary_secret += str(g & 1)
                binary_secret += str(b & 1)
                
            # Convert binary to bytes
            byte_array = bytearray()
            for i in range(0, len(binary_secret), 8):
                byte = binary_secret[i:i + 8]
                if len(byte) == 8:
                    byte_array.append(int(byte, 2))
                    
            # Remove padding and decrypt
            extracted_message = bytes(byte_array).decode('utf-8', errors='ignore').rstrip('\x00')
            original_message = f.decrypt(extracted_message.encode()).decode()
            
            # Display result
            self.root.after(0, self.display_decrypted_message, original_message)
            self.root.after(0, self.update_status, "✓ Message decrypted successfully!", COLORS["success"])
            
        except Exception as e:
            self.root.after(0, self.update_status, f"Decryption failed: {str(e)}", COLORS["error"])
            self.root.after(0, messagebox.showerror, "Error", f"Decryption failed: {str(e)}")
            
    def display_decrypted_message(self, message):
        """Display decrypted message in textbox"""
        self.decrypted_message_box.delete("1.0", "end")
        self.decrypted_message_box.insert("1.0", message)
        messagebox.showinfo("Success", "Message decrypted successfully!")
        
    def update_status(self, message, color):
        """Update status bar with message and color"""
        self.status_label.configure(text=message, text_color=color)


# Main program execution
if __name__ == "__main__":
    root = ctk.CTk()
    app = SteganographyApp(root)
    root.mainloop()
