import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import os
import sys
import json
import threading
import time
from tkinter import font as tkfont
import re
import platform
import base64
import urllib.parse
import unicodedata
import random
import winsound  # For Windows sound effects

class TextEncoder:
    @staticmethod
    def encode_for_adb(text):
        """Encode text for ADB command, handling all special characters and languages."""
        # First normalize the text to handle any special Unicode characters
        text = unicodedata.normalize('NFC', text)
        
        # Convert to base64 to handle all characters safely
        text_bytes = text.encode('utf-8')
        base64_text = base64.b64encode(text_bytes).decode('utf-8')
        
        # Create the ADB command with base64 encoded text
        return f'adb shell am broadcast -a ADB_INPUT_B64 --es msg "{base64_text}"'

    @staticmethod
    def encode_single_char(char):
        """Encode a single character for ADB command."""
        char = unicodedata.normalize('NFC', char)
        char_bytes = char.encode('utf-8')
        base64_char = base64.b64encode(char_bytes).decode('utf-8')
        return f'adb shell am broadcast -a ADB_INPUT_B64 --es msg "{base64_char}"'

    @staticmethod
    def decode_preview(text):
        """Decode text for preview, showing exactly how it will appear."""
        return text

class SuccessNotification(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Success")
        
        # Configure window
        self.geometry("300x150")
        self.resizable(False, False)
        
        # Make window stay on top
        self.attributes('-topmost', True)
        
        # Center the window
        self.center_window()
        
        # Create content
        self.create_widgets()
        
        # Play success sound
        self.play_success_sound()
        
        # Auto close after 2 seconds
        self.after(2000, self.destroy)
    
    def center_window(self):
        """Center the window on the screen."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Create the notification widgets."""
        # Main frame
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Success icon
        icon_label = ttk.Label(
            main_frame,
            text="✅",
            font=("Segoe UI", 32)
        )
        icon_label.pack(pady=(0, 10))
        
        # Success message
        message_label = ttk.Label(
            main_frame,
            text="Text sent successfully!",
            font=("Segoe UI", 12, "bold")
        )
        message_label.pack()
    
    def play_success_sound(self):
        """Play a success sound effect."""
        try:
            # Play a simple beep sound
            winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
        except:
            # If sound fails, just continue silently
            pass

class AutoInputApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Input for Android")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")
        
        # Initialize variables
        self.is_connected = False
        self.device_info = {}
        self.preview_window = None
        self.last_sent_text = ""
        self.text_encoder = TextEncoder()
        self.min_typing_speed = tk.DoubleVar(value=50)   # Default min speed: 50ms
        self.max_typing_speed = tk.DoubleVar(value=150)  # Default max speed: 150ms
        self.is_typing = False
        self.typing_thread = None
        
        # Set custom font
        self.custom_font = tkfont.Font(family="Segoe UI", size=10)
        self.title_font = tkfont.Font(family="Segoe UI", size=16, weight="bold")
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create top frame for device info
        self.top_frame = ttk.Frame(self.main_frame)
        self.top_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Device info label
        self.device_label = ttk.Label(
            self.top_frame,
            text="No device connected",
            font=self.custom_font
        )
        self.device_label.pack(side=tk.LEFT)
        
        # Refresh button
        self.refresh_button = ttk.Button(
            self.top_frame,
            text="Refresh Connection",
            command=self.check_adb_connection,
            style="Accent.TButton"
        )
        self.refresh_button.pack(side=tk.RIGHT)
        
        # Title label
        title_label = ttk.Label(
            self.main_frame,
            text="Auto Input for Android",
            font=self.title_font
        )
        title_label.pack(pady=(0, 20))
        
        # Create text input frame
        input_frame = ttk.LabelFrame(self.main_frame, text="Input Text", padding="10")
        input_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Text input area with scrollbar
        self.text_input = scrolledtext.ScrolledText(
            input_frame,
            height=8,  # Reduced height for better proportions
            width=60,  # Increased width for better readability
            font=self.custom_font,
            wrap=tk.WORD,
            padx=10,   # Added padding
            pady=10    # Added padding
        )
        self.text_input.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)  # Added padding around the text area
        
        # Create typing speed control frame
        speed_frame = ttk.LabelFrame(self.main_frame, text="Typing Speed Control", padding="10")
        speed_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Min speed control
        min_speed_frame = ttk.Frame(speed_frame)
        min_speed_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(
            min_speed_frame,
            text="Min Speed (ms):",
            font=self.custom_font
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.min_speed_slider = ttk.Scale(
            min_speed_frame,
            from_=10,    # Minimum delay: 10ms
            to=200,      # Maximum delay: 200ms
            orient=tk.HORIZONTAL,
            variable=self.min_typing_speed,
            command=self.update_speed_labels
        )
        self.min_speed_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.min_speed_label = ttk.Label(
            min_speed_frame,
            text="50",
            font=self.custom_font,
            width=4
        )
        self.min_speed_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Max speed control
        max_speed_frame = ttk.Frame(speed_frame)
        max_speed_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(
            max_speed_frame,
            text="Max Speed (ms):",
            font=self.custom_font
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.max_speed_slider = ttk.Scale(
            max_speed_frame,
            from_=50,    # Minimum delay: 50ms
            to=500,      # Maximum delay: 500ms
            orient=tk.HORIZONTAL,
            variable=self.max_typing_speed,
            command=self.update_speed_labels
        )
        self.max_speed_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.max_speed_label = ttk.Label(
            max_speed_frame,
            text="150",
            font=self.custom_font,
            width=4
        )
        self.max_speed_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Current speed indicator
        self.speed_label = ttk.Label(
            speed_frame,
            text="Current Speed Range: 50-150ms per character",
            font=self.custom_font
        )
        self.speed_label.pack(pady=(5, 0))
        
        # Create button frame
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Preview button
        self.preview_button = ttk.Button(
            button_frame,
            text="Preview Text",
            command=self.show_preview,
            style="Accent.TButton"
        )
        self.preview_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Send button
        self.send_button = ttk.Button(
            button_frame,
            text="Send to Android",
            command=self.send_text,
            style="Accent.TButton"
        )
        self.send_button.pack(side=tk.LEFT)
        
        # Stop button
        self.stop_button = ttk.Button(
            button_frame,
            text="Stop Typing",
            command=self.stop_typing,
            style="Accent.TButton",
            state="disabled"
        )
        self.stop_button.pack(side=tk.LEFT, padx=(10, 0))
        
        # Create status frame with custom style
        self.status_frame = ttk.Frame(self.main_frame)
        self.status_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Configure custom style for status frame
        style = ttk.Style()
        style.configure(
            "Status.TFrame",
            background="#f8f9fa",
            relief="solid",
            borderwidth=1
        )
        self.status_frame.configure(style="Status.TFrame")
        
        # Left section for status icon and text
        left_frame = ttk.Frame(self.status_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=5)
        
        # Status icon with custom style
        self.status_icon = ttk.Label(
            left_frame,
            text="🟢",
            font=("Segoe UI", 14, "bold")
        )
        self.status_icon.pack(side=tk.LEFT, padx=(0, 10))
        
        # Status text with custom style
        self.status_label = ttk.Label(
            left_frame,
            text="Ready",
            font=("Segoe UI", 10),
            foreground="#495057"  # Dark gray
        )
        self.status_label.pack(side=tk.LEFT)
        
        # Right section for progress and success message
        right_frame = ttk.Frame(self.status_frame)
        right_frame.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # Success message with custom style
        self.success_label = ttk.Label(
            right_frame,
            text="✓ Text sent successfully!",
            font=("Segoe UI", 10, "bold"),
            foreground="#28a745"  # Success green
        )
        self.success_label.pack(side=tk.LEFT, padx=(0, 10))
        self.success_label.pack_forget()  # Hide initially
        
        # Progress bar with custom style
        style.configure(
            "Status.Horizontal.TProgressbar",
            troughcolor="#e9ecef",
            background="#007bff",
            thickness=15
        )
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            right_frame,
            variable=self.progress_var,
            mode='determinate',
            length=200,
            style="Status.Horizontal.TProgressbar"
        )
        self.progress_bar.pack(side=tk.LEFT)
        self.progress_bar.pack_forget()  # Hide initially
        
        # Add success notification flag
        self.show_notifications = tk.BooleanVar(value=True)
        
        # Add notification toggle to status frame
        self.notification_toggle = ttk.Checkbutton(
            self.status_frame,
            text="Show Notifications",
            variable=self.show_notifications,
            style="Switch.TCheckbutton"
        )
        self.notification_toggle.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Configure styles
        self.configure_styles()
        
        # Start periodic connection check
        self.start_connection_check()
        
        # Initial connection check
        self.check_adb_connection()

    def configure_styles(self):
        style = ttk.Style()
        style.configure("Accent.TButton", font=self.custom_font)
        style.configure("TLabelframe.Label", font=self.custom_font)

    def start_connection_check(self):
        def check_loop():
            while True:
                self.check_adb_connection(silent=True)
                time.sleep(5)  # Check every 5 seconds
        
        thread = threading.Thread(target=check_loop, daemon=True)
        thread.start()

    def get_device_info(self):
        try:
            # Get device model
            model = subprocess.run(
                ["adb", "shell", "getprop", "ro.product.model"],
                capture_output=True,
                text=True
            ).stdout.strip()
            
            # Get Android version
            version = subprocess.run(
                ["adb", "shell", "getprop", "ro.build.version.release"],
                capture_output=True,
                text=True
            ).stdout.strip()
            
            # Get device ID
            devices = subprocess.run(
                ["adb", "devices"],
                capture_output=True,
                text=True
            ).stdout.strip()
            
            device_id = re.search(r'(\S+)\s+device', devices)
            device_id = device_id.group(1) if device_id else "Unknown"
            
            return {
                "model": model,
                "version": version,
                "id": device_id
            }
        except Exception:
            return {}

    def check_adb_connection(self, silent=False):
        try:
            result = subprocess.run(
                ["adb", "devices"],
                capture_output=True,
                text=True
            )
            
            if "device" in result.stdout:
                self.is_connected = True
                self.device_info = self.get_device_info()
                device_text = f"Connected: {self.device_info.get('model', 'Unknown')} (Android {self.device_info.get('version', 'Unknown')})"
                self.device_label.config(text=device_text)
                self.update_status("Device connected", "success")
                self.send_button.config(state="normal")
                self.preview_button.config(state="normal")
            else:
                self.is_connected = False
                self.device_label.config(text="No device connected")
                self.update_status("Waiting for device...", "warning")
                self.send_button.config(state="disabled")
                self.preview_button.config(state="disabled")
                if not silent:
                    messagebox.showwarning(
                        "Connection Error",
                        "Please connect your Android device and ensure ADB is enabled"
                    )
        except FileNotFoundError:
            self.is_connected = False
            self.device_label.config(text="ADB not found")
            self.update_status("ADB not installed", "error")
            self.send_button.config(state="disabled")
            self.preview_button.config(state="disabled")
            if not silent:
                messagebox.showerror(
                    "Error",
                    "ADB is not installed or not in system PATH"
                )

    def show_preview(self):
        text = self.text_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "Please enter some text to preview")
            return
            
        if self.preview_window:
            self.preview_window.destroy()
            
        self.preview_window = tk.Toplevel(self.root)
        self.preview_window.title("Text Preview")
        self.preview_window.geometry("400x300")
        
        # Create preview frame
        preview_frame = ttk.Frame(self.preview_window, padding="20")
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        # Preview label
        ttk.Label(
            preview_frame,
            text="Preview of text to be sent:",
            font=self.custom_font
        ).pack(pady=(0, 10))
        
        # Preview text
        preview_text = scrolledtext.ScrolledText(
            preview_frame,
            wrap=tk.WORD,
            font=self.custom_font
        )
        preview_text.pack(fill=tk.BOTH, expand=True)
        preview_text.insert("1.0", text)
        preview_text.config(state="disabled")
        
        # Close button
        ttk.Button(
            preview_frame,
            text="Close",
            command=self.preview_window.destroy
        ).pack(pady=(10, 0))

    def update_speed_labels(self, *args):
        """Update the speed labels when sliders are moved."""
        min_speed = int(self.min_typing_speed.get())
        max_speed = int(self.max_typing_speed.get())
        
        # Ensure min speed doesn't exceed max speed
        if min_speed > max_speed:
            self.min_typing_speed.set(max_speed)
            min_speed = max_speed
        
        self.min_speed_label.config(text=str(min_speed))
        self.max_speed_label.config(text=str(max_speed))
        self.speed_label.config(text=f"Current Speed Range: {min_speed}-{max_speed}ms per character")

    def update_status(self, message, status_type="info"):
        """Update status with different types of messages."""
        # Update status icon based on type
        icons = {
            "info": "🟢",    # Green circle
            "warning": "🟡",  # Yellow circle
            "error": "🔴",    # Red circle
            "typing": "⌨️",   # Keyboard
            "success": "✅",  # Check mark
            "stopped": "⏹️"   # Stop symbol
        }
        
        # Update status frame background based on type
        backgrounds = {
            "info": "#f8f9fa",     # Light gray
            "warning": "#fff3cd",   # Light yellow
            "error": "#f8d7da",     # Light red
            "typing": "#cce5ff",    # Light blue
            "success": "#d4edda",   # Light green
            "stopped": "#e2e3e5"    # Light gray
        }
        
        # Update status text color based on type
        colors = {
            "info": "#495057",      # Dark gray
            "warning": "#856404",   # Dark yellow
            "error": "#721c24",     # Dark red
            "typing": "#004085",    # Dark blue
            "success": "#155724",   # Dark green
            "stopped": "#383d41"    # Dark gray
        }
        
        # Update status frame background
        self.status_frame.configure(style="Status.TFrame")
        style = ttk.Style()
        style.configure(
            "Status.TFrame",
            background=backgrounds.get(status_type, "#f8f9fa")
        )
        
        # Update status icon and text
        self.status_icon.config(text=icons.get(status_type, "🟢"))
        self.status_label.config(
            text=message,
            foreground=colors.get(status_type, "#495057")
        )
        
        # Show success message without auto-hiding
        if status_type == "success":
            self.success_label.pack(side=tk.LEFT, padx=(0, 10))
        else:
            self.hide_success_message()

    def hide_success_message(self):
        """Hide the success message."""
        self.success_label.pack_forget()

    def stop_typing(self):
        """Stop the current typing operation."""
        self.is_typing = False
        self.stop_button.config(state="disabled")
        self.send_button.config(state="normal")
        self.preview_button.config(state="normal")
        self.update_status("Typing stopped", "stopped")
        self.progress_bar.pack_forget()  # Hide progress bar

    def show_success_notification(self):
        """Show a success notification window."""
        if self.show_notifications.get():
            SuccessNotification(self.root)

    def type_text(self, text):
        """Type text character by character with random delays within the specified range."""
        self.is_typing = True
        self.stop_button.config(state="normal")
        self.send_button.config(state="disabled")
        self.preview_button.config(state="disabled")
        
        # Show progress bar
        self.progress_bar.pack(side=tk.LEFT)
        self.progress_var.set(0)
        
        try:
            total_chars = len(text)
            for i, char in enumerate(text, 1):
                if not self.is_typing:
                    break
                    
                # Update progress
                progress = (i / total_chars) * 100
                self.progress_var.set(progress)
                self.update_status(f"Typing: {i}/{total_chars} characters", "typing")
                
                # Send single character
                command = self.text_encoder.encode_single_char(char)
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                
                if result.returncode != 0:
                    raise subprocess.CalledProcessError(result.returncode, command, result.stderr)
                
                # Generate random delay within the specified range
                min_delay = self.min_typing_speed.get()
                max_delay = self.max_typing_speed.get()
                delay = random.uniform(min_delay, max_delay)
                
                # Wait for the random delay
                time.sleep(delay / 1000.0)  # Convert ms to seconds
                
            if self.is_typing:  # Only update status if typing wasn't stopped
                self.update_status("Text sent successfully!", "success")
                self.last_sent_text = text
                
        except subprocess.CalledProcessError as e:
            self.update_status("Error sending text", "error")
            error_msg = str(e)
            if "ADBKeyboard" in error_msg:
                error_msg += "\n\nPlease ensure ADBKeyboard is installed and set as the default keyboard on your device."
            messagebox.showerror("Error", f"Failed to send text: {error_msg}")
        except Exception as e:
            self.update_status("Error sending text", "error")
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
        finally:
            self.is_typing = False
            self.stop_button.config(state="disabled")
            self.send_button.config(state="normal")
            self.preview_button.config(state="normal")
            self.progress_bar.pack_forget()  # Hide progress bar

    def send_text(self):
        if not self.is_connected:
            messagebox.showerror("Error", "No Android device connected")
            return
            
        text = self.text_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "Please enter some text")
            return
            
        # Start typing in a separate thread
        self.typing_thread = threading.Thread(target=self.type_text, args=(text,))
        self.typing_thread.daemon = True
        self.typing_thread.start()

def check_adb_installation():
    try:
        subprocess.run(["adb", "version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def main():
    if not check_adb_installation():
        messagebox.showerror(
            "Error",
            "ADB is not installed or not in system PATH.\n\n"
            "Please install Android Platform Tools and add it to your system PATH."
        )
        return
        
    root = tk.Tk()
    app = AutoInputApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
