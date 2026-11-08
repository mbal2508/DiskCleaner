"""
C-cleaner | Smart File Organizer
Copyright (c) 2026 Jembar Muhammad Firdiana. All rights reserved.

This software is provided "as is", without warranty of any kind.
"""

import os
import sys
import shutil
import threading
from pathlib import Path
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox
from PIL import Image
import customtkinter as ctk

# CustomTkinter Theme Configuration
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class CCleanerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("C-cleaner | Smart File Organizer")
        self.geometry("650x750")
        self.minsize(600, 700)
        
        # Fullscreen bindings
        self.is_fullscreen = False
        self.bind("<F11>", self.toggle_fullscreen)
        self.bind("<Escape>", self.exit_fullscreen)

        # Handle window close event
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Color Scheme extracted from Logo
        self.COLOR_BLUE = "#287CB1"
        self.COLOR_GOLD = "#CBA373"
        self.COLOR_BLUE_HOVER = "#1E5C85"
        self.COLOR_GOLD_HOVER = "#A3835C"

        # Modern Font Configuration
        self.font_title = ctk.CTkFont(family="Segoe UI", size=24, weight="bold")
        self.font_label = ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
        self.font_text = ctk.CTkFont(family="Segoe UI", size=12)
        self.font_log = ctk.CTkFont(family="Consolas", size=11)

        self.is_cleaning = False
        self.custom_source_path = None

        self.setup_data()
        self.build_ui()

    def toggle_fullscreen(self, event=None):
        """Toggle full screen mode via F11."""
        self.is_fullscreen = not self.is_fullscreen
        self.attributes("-fullscreen", self.is_fullscreen)

    def exit_fullscreen(self, event=None):
        """Exit full screen mode via Escape."""
        self.is_fullscreen = False
        self.attributes("-fullscreen", False)

    def setup_data(self):
        self.home_path = Path.home()
        self.folder_map = {
            "Downloads": self.home_path / "Downloads",
            "Documents": self.home_path / "Documents",
            "Pictures": self.home_path / "Pictures",
            "Music": self.home_path / "Music",
            "Videos": self.home_path / "Videos",
            "Desktop": self.home_path / "Desktop"
        }

        self.sortir_map = {
            # === PHOTOS & VIDEOS ===
            ".png": "PHOTOS_AND_VIDEOS", ".jpg": "PHOTOS_AND_VIDEOS", ".jpeg": "PHOTOS_AND_VIDEOS",
            ".gif": "PHOTOS_AND_VIDEOS", ".webp": "PHOTOS_AND_VIDEOS", ".heic": "PHOTOS_AND_VIDEOS",
            ".mp4": "PHOTOS_AND_VIDEOS", ".mkv": "PHOTOS_AND_VIDEOS", ".mov": "PHOTOS_AND_VIDEOS",
            ".avi": "PHOTOS_AND_VIDEOS",

            # === DOCUMENTS & TEXT ===
            ".pdf": "DOCUMENTS", ".doc": "DOCUMENTS", ".docx": "DOCUMENTS",
            ".xls": "DOCUMENTS", ".xlsx": "DOCUMENTS", ".ppt": "DOCUMENTS",
            ".pptx": "DOCUMENTS", ".txt": "DOCUMENTS", ".csv": "DOCUMENTS",

            # === MUSIC & AUDIO ===
            ".mp3": "MUSIC", ".wav": "MUSIC", ".m4a": "MUSIC",

            # === ARCHIVES & PROGRAMS ===
            ".zip": "ARCHIVES", ".rar": "ARCHIVES", ".7z": "ARCHIVES",
            ".exe": "PROGRAMS", ".msi": "PROGRAMS", ".apk": "PROGRAMS", ".dmg": "PROGRAMS",

            # === DEVELOPMENT & CODING ===
            ".py": "DEVELOPMENT", ".html": "DEVELOPMENT", ".css": "DEVELOPMENT", 
            ".js": "DEVELOPMENT", ".json": "DEVELOPMENT", ".sql": "DEVELOPMENT"
        }

    def build_ui(self):
        # --- HEADER / LOGO ---
        try:
            img_path = resource_path("logo.png")
            img = Image.open(img_path)
            original_width, original_height = img.size
            
            target_width = 250
            ratio = original_height / original_width
            target_height = int(target_width * ratio)
            
            self.logo_img = ctk.CTkImage(
                light_image=img, 
                dark_image=img, 
                size=(target_width, target_height)
            )
            
            logo_label = ctk.CTkLabel(self, image=self.logo_img, text="")
            logo_label.pack(pady=(25, 10))
        except Exception:
            logo_label = ctk.CTkLabel(self, text="C-cleaner", font=self.font_title, text_color=self.COLOR_BLUE)
            logo_label.pack(pady=(35, 10))

        # --- MAIN CONTAINER ---
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=50, pady=10)

        # --- SOURCE FOLDER CONTROL ---
        ctk.CTkLabel(main_frame, text="1. Select the folder to clean:", font=self.font_label).pack(anchor="w")
        
        self.source_var = ctk.StringVar(value="Downloads")
        options = list(self.folder_map.keys()) + ["Select Another Folder..."]
        
        self.source_menu = ctk.CTkOptionMenu(
            main_frame, 
            values=options, 
            variable=self.source_var,
            command=self.on_source_select,
            fg_color=self.COLOR_BLUE, 
            button_color=self.COLOR_BLUE_HOVER,
            button_hover_color=self.COLOR_GOLD,
            font=self.font_text,
            height=35
        )
        self.source_menu.pack(fill="x", pady=(5, 20))

        # --- DESTINATION FOLDER CONTROL ---
        ctk.CTkLabel(main_frame, text="2. Destination folder:", font=self.font_label).pack(anchor="w")
        
        dest_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        dest_frame.pack(fill="x", pady=(5, 20))
        
        self.dest_var = ctk.StringVar(value=str(self.home_path / "C-Cleaner_Results"))
        
        dest_entry = ctk.CTkEntry(
            dest_frame, 
            textvariable=self.dest_var, 
            font=self.font_text, 
            height=35,
            border_color="#cccccc"
        )
        dest_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        browse_btn = ctk.CTkButton(
            dest_frame, 
            text="Browse...", 
            command=self.browse_dest, 
            fg_color=self.COLOR_GOLD, 
            hover_color=self.COLOR_GOLD_HOVER, 
            font=self.font_label, 
            width=80, 
            height=35
        )
        browse_btn.pack(side="right")

        # --- EXECUTE BUTTON ---
        self.start_btn = ctk.CTkButton(
            main_frame, 
            text="Start Cleaning", 
            command=self.start_cleaning_thread, 
            fg_color=self.COLOR_BLUE, 
            hover_color=self.COLOR_BLUE_HOVER, 
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"), 
            height=45,
            corner_radius=8
        )
        self.start_btn.pack(fill="x", pady=(10, 25))

        # --- TERMINAL LOG ---
        log_header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        log_header_frame.pack(fill="x")
        
        ctk.CTkLabel(log_header_frame, text="Process Log:", font=self.font_label).pack(side="left")
        ctk.CTkLabel(log_header_frame, text="(Press F11 for Fullscreen)", font=ctk.CTkFont(family="Segoe UI", size=10, slant="italic"), text_color="gray").pack(side="right")
        
        self.log_text = ctk.CTkTextbox(
            main_frame, 
            height=160, 
            font=self.font_log,
            state="disabled", 
            wrap="word",
            scrollbar_button_color=self.COLOR_GOLD,
            scrollbar_button_hover_color=self.COLOR_BLUE,
            border_width=2,
            border_color="#e5e5e5"
        )
        self.log_text.pack(fill="both", expand=True, pady=(5, 10))

        # --- COPYRIGHT FOOTER ---
        copyright_label = ctk.CTkLabel(
            self, 
            text="© 2026 Jembar Muhammad Firdiana. All rights reserved.", 
            font=ctk.CTkFont(family="Segoe UI", size=11), 
            text_color="gray"
        )
        copyright_label.pack(side="bottom", pady=(0, 15))

    def on_closing(self):
        """Prevent user from closing the app while cleaning is in progress."""
        if self.is_cleaning:
            messagebox.showwarning("Warning", "A cleaning process is currently running. Please wait until it finishes to prevent file corruption.")
        else:
            self.destroy()

    def on_source_select(self, choice):
        if choice == "Select Another Folder...":
            folder = filedialog.askdirectory(title="Select the folder to clean")
            if folder:
                self.custom_source_path = Path(folder)
                self.log_msg(f"Source folder set to: {self.custom_source_path}")
            else:
                self.source_var.set("Downloads")
                self.custom_source_path = None

    def browse_dest(self):
        folder = filedialog.askdirectory(title="Select destination folder")
        if folder:  
            self.dest_var.set(folder)

    def log_msg(self, message):
        """Thread-safe logging method."""
        self.after(0, self._append_log, message)

    def _append_log(self, message):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def start_cleaning_thread(self):
        if self.is_cleaning:
            return
            
        source_selection = self.source_var.get()
        if source_selection == "Select Another Folder...":
            path_asal = self.custom_source_path
        else:
            path_asal = self.folder_map[source_selection]

        path_tujuan = Path(self.dest_var.get())

        # Prevent sorting a folder into itself (Infinite loop)
        try:
            if path_asal.resolve() == path_tujuan.resolve() or path_tujuan.resolve().is_relative_to(path_asal.resolve()):
                messagebox.showerror("Error", "Destination folder cannot be the same as or inside the Source folder!")
                return
        except AttributeError:
            if str(path_asal.resolve()) in str(path_tujuan.resolve()):
                messagebox.showerror("Error", "Destination folder cannot be the same as or inside the Source folder!")
                return

        if not path_asal or not path_asal.exists():
            messagebox.showerror("Error", f"Source folder not found:\n{path_asal}")
            return

        self.is_cleaning = True
        self.start_btn.configure(text="Cleaning in Progress...", fg_color="gray", state="disabled")
        
        thread = threading.Thread(target=self.proses_pembersihan, args=(path_asal, path_tujuan))
        thread.daemon = True
        thread.start()

    def proses_pembersihan(self, path_asal, path_tujuan):
        self.log_msg("--- STARTING CLEANUP ---")
        self.log_msg(f"Source: {path_asal}")
        self.log_msg(f"Destination: {path_tujuan}\n")
        
        path_tujuan.mkdir(parents=True, exist_ok=True)
        
        file_dipindahkan = 0
        file_gagal = 0
        file_diproses = 0

        for file_path in path_asal.iterdir():
            if file_path.is_file() and not file_path.name.startswith(".") and not file_path.name.startswith("~") and file_path.name.lower() != "desktop.ini":
                
                file_diproses += 1
                ekstensi = file_path.suffix.lower()
                nama_polos = file_path.stem

                nama_subfolder = self.sortir_map.get(ekstensi, "OTHER_FILES")
                
                path_lengkap = path_tujuan / nama_subfolder
                path_lengkap.mkdir(parents=True, exist_ok=True)
                
                lokasi_baru = path_lengkap / file_path.name
                counter = 1

                while lokasi_baru.exists():
                    nama_baru = f"{nama_polos}_{counter}{ekstensi}"
                    lokasi_baru = path_lengkap / nama_baru
                    counter += 1

                try:
                    shutil.move(str(file_path), str(lokasi_baru))
                    if counter > 1:
                        self.log_msg(f"🔄 RENAMED: {file_path.name} -> {lokasi_baru.name}")
                    else:
                        self.log_msg(f"✅ MOVED: {file_path.name} -> [{nama_subfolder}]")
                    file_dipindahkan += 1
                except PermissionError:
                    self.log_msg(f"❌ DENIED: {file_path.name} (File is open or restricted)")
                    file_gagal += 1
                except Exception as e:
                    self.log_msg(f"❌ FAILED: {file_path.name} | Error: {e}")
                    file_gagal += 1
                    
        self.log_msg("\n🎉 CLEANUP FINISHED!")
        
        if file_diproses == 0:
            self.log_msg("No movable files found in the source folder.")
        else:
            self.log_msg(f"Total moved: {file_dipindahkan} file(s).")
            if file_gagal > 0:
                self.log_msg(f"Failed to move: {file_gagal} file(s).")
        self.log_msg("---------------------------\n")
        
        self.after(0, self.reset_ui)

    def reset_ui(self):
        self.is_cleaning = False
        self.start_btn.configure(text="Start Cleaning", fg_color=self.COLOR_BLUE, state="normal")
        messagebox.showinfo("Finished", "The cleaning process has been completed successfully!")

if __name__ == "__main__":
    app = CCleanerApp()
    app.mainloop()