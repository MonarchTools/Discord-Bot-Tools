"""کلاس پایه برای همه ماژول‌ها - interface یکسان"""

import customtkinter as ctk
from typing import Optional
from core.logger import Logger


class BaseModule:
    """کلاس پایه که همه ابزارها از آن ارث می‌برند"""
    
    # هر ماژول باید این مقادیر را override کند
    NAME: str = "Base Module"
    DESCRIPTION: str = ""
    ICON: str = "⚙"
    REQUIRES_TOKEN: bool = True
    REQUIRES_GUILD: bool = False
    
    def __init__(self, parent_frame: ctk.CTkFrame):
        self.parent = parent_frame
        self.logger = Logger()
        self.widgets = {}
        self._build_ui()
    
    def _build_ui(self):
        """ساخت UI - باید در کلاس‌های فرزند پیاده‌سازی شود"""
        raise NotImplementedError
    
    def run(self):
        """اجرای ابزار - باید در کلاس‌های فرزند پیاده‌سازی شود"""
        raise NotImplementedError
    
    def _get_entry(self, key: str) -> str:
        """دریافت مقدار یک ورودی"""
        if key in self.widgets:
            return self.widgets[key].get().strip()
        return ""
    
    def _set_entry(self, key: str, value: str):
        """تنظیم مقدار یک ورودی"""
        if key in self.widgets:
            self.widgets[key].delete(0, "end")
            self.widgets[key].insert(0, value)
    
    def _create_label(self, text: str, row: int, column: int = 0):
        label = ctk.CTkLabel(
            self.parent, text=text,
            text_color="#00ff41",
            font=("Consolas", 12)
        )
        label.grid(row=row, column=column, padx=10, pady=5, sticky="w")
        return label
    
    def _create_entry(self, key: str, row: int, placeholder: str = "", 
                      column: int = 1, show: str = ""):
        entry = ctk.CTkEntry(
            self.parent,
            placeholder_text=placeholder,
            fg_color="#050805",
            border_color="#008f11",
            text_color="#00ff41",
            font=("Consolas", 12),
            show=show
        )
        entry.grid(row=row, column=column, padx=10, pady=5, sticky="ew")
        self.widgets[key] = entry
        return entry
    
    def _create_button(self, text: str, command, row: int, column: int = 0,
                       columnspan: int = 2, color: str = "#008f11"):
        btn = ctk.CTkButton(
            self.parent, text=text, command=command,
            fg_color=color,
            hover_color="#00ff41",
            text_color="#000000",
            font=("Consolas", 12, "bold"),
            border_color="#00ff41",
            border_width=1
        )
        btn.grid(row=row, column=column, columnspan=columnspan, 
                 padx=10, pady=15, sticky="ew")
        return btn
    
    def _create_checkbox(self, key: str, text: str, row: int, column: int = 0):
        var = ctk.BooleanVar(value=False)
        cb = ctk.CTkCheckBox(
            self.parent, text=text, variable=var,
            text_color="#00ff41",
            fg_color="#008f11",
            font=("Consolas", 12)
        )
        cb.grid(row=row, column=column, padx=10, pady=5, sticky="w")
        self.widgets[key] = var
        return var