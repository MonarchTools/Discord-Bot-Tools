"""کنسول خروجی با افکت ترمینال"""

import customtkinter as ctk
import datetime
from config import COLORS, FONT_MONO


class Console(ctk.CTkFrame):
    """کنسول لاگ با افکت هکری"""
    
    def __init__(self, parent, height: int = 200):
        super().__init__(parent, fg_color="#000000", corner_radius=0)
        
        # عنوان
        self.header = ctk.CTkLabel(
            self, text="▶ CONSOLE OUTPUT",
            text_color=COLORS["accent_green"],
            font=("Consolas", 11, "bold"),
            anchor="w"
        )
        self.header.pack(fill="x", padx=5, pady=(5, 0))
        
        # تکست باکس لاگ
        self.log_text = ctk.CTkTextbox(
            self,
            fg_color="#000000",
            text_color=COLORS["accent_green"],
            font=FONT_MONO,
            wrap="word",
            corner_radius=0,
            border_width=0
        )
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # دکمه پاک کردن
        self.clear_btn = ctk.CTkButton(
            self, text="CLEAR", width=80, height=25,
            fg_color="#1a0000",
            hover_color="#330000",
            text_color=COLORS["accent_red"],
            font=("Consolas", 10, "bold"),
            command=self.clear,
            corner_radius=3
        )
        self.clear_btn.pack(anchor="e", padx=5, pady=(0, 5))
        
        # تنظیم رنگ‌های tag
        self.log_text._textbox.tag_config("green", foreground="#00ff41")
        self.log_text._textbox.tag_config("red", foreground="#ff0033")
        self.log_text._textbox.tag_config("yellow", foreground="#ffcc00")
        self.log_text._textbox.tag_config("dim", foreground="#008f11")
    
    def log(self, message: str, color: str = "green"):
        """افزودن پیام به کنسول"""
        tag_map = {
            "#00ff41": "green",
            "#ff0033": "red",
            "#ffcc00": "yellow",
            "#008f11": "dim",
        }
        tag = tag_map.get(color, "green")
        self.log_text._textbox.configure(state="normal")
        self.log_text._textbox.insert("end", message + "\n", tag)
        self.log_text._textbox.see("end")
        self.log_text._textbox.configure(state="disabled")
    
    def clear(self):
        """پاک کردن کنسول"""
        self.log_text._textbox.configure(state="normal")
        self.log_text._textbox.delete("1.0", "end")
        self.log_text._textbox.configure(state="disabled")