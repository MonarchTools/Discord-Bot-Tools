"""منوی کناری با لیست ابزارها"""

import customtkinter as ctk
from config import COLORS, WINDOW_WIDTH
from ui.theme import style_sidebar


class Sidebar(ctk.CTkFrame):
    """منوی کناری"""
    
    def __init__(self, parent, on_module_select):
        super().__init__(parent, width=220)
        style_sidebar(self)
        self.pack_propagate(False)
        
        self.on_module_select = on_module_select
        self.buttons = []
        self.active_button = None
        
        # لوگو / عنوان
        self.logo_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.logo_frame.pack(fill="x", padx=10, pady=(15, 10))
        
        self.title_label = ctk.CTkLabel(
            self.logo_frame,
            text="╔══════════╗\n║  H4CK3R  ║\n║  P4N3L   ║\n╚══════════╝",
            text_color=COLORS["accent_green"],
            font=("Consolas", 11, "bold"),
            justify="center"
        )
        self.title_label.pack()
        
        # خط جداکننده
        sep = ctk.CTkFrame(self, height=2, fg_color=COLORS["accent_dark_green"])
        sep.pack(fill="x", padx=10, pady=10)
        
        # بخش اتصال
        self.status_frame = ctk.CTkFrame(self, fg_color="#000000")
        self.status_frame.pack(fill="x", padx=10, pady=5)
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="● DISCONNECTED",
            text_color=COLORS["accent_red"],
            font=("Consolas", 10, "bold"),
            anchor="w"
        )
        self.status_label.pack(fill="x", padx=8, pady=6)
        
        self.user_label = ctk.CTkLabel(
            self.status_frame,
            text="No token loaded",
            text_color=COLORS["text_dim"],
            font=("Consolas", 9),
            anchor="w"
        )
        self.user_label.pack(fill="x", padx=8, pady=(0, 6))
        
        # خط جداکننده
        sep2 = ctk.CTkFrame(self, height=2, fg_color=COLORS["accent_dark_green"])
        sep2.pack(fill="x", padx=10, pady=10)
        
        # عنوان ابزارها
        tools_label = ctk.CTkLabel(
            self, text="[ TOOLS ]",
            text_color=COLORS["accent_green"],
            font=("Consolas", 11, "bold")
        )
        tools_label.pack(pady=(5, 10))
        
        # اسکرول برای دکمه‌ها
        self.scroll_frame = ctk.CTkScrollableFrame(
            self, fg_color="transparent",
            scrollbar_button_color=COLORS["accent_dark_green"],
            scrollbar_button_hover_color=COLORS["accent_green"]
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)
    
    def add_module_button(self, module_class):
        """افزودن دکمه برای یک ماژول"""
        btn = ctk.CTkButton(
            self.scroll_frame,
            text=f" {module_class.ICON}  {module_class.NAME}",
            command=lambda: self._on_click(btn, module_class),
            fg_color="transparent",
            hover_color="#002200",
            text_color=COLORS["accent_green"],
            font=("Consolas", 11),
            anchor="w",
            height=35,
            corner_radius=4,
            border_width=0
        )
        btn.pack(fill="x", padx=5, pady=2)
        self.buttons.append((btn, module_class))
    
    def _on_click(self, btn, module_class):
        """کلیک روی دکمه ماژول"""
        if self.active_button:
            self.active_button.configure(
                fg_color="transparent",
                text_color=COLORS["accent_green"]
            )
        btn.configure(
            fg_color="#003300",
            text_color="#00ff41"
        )
        self.active_button = btn
        self.on_module_select(module_class)
    
    def update_status(self, connected: bool, username: str = "", is_bot: bool = False):
        """بروزرسانی وضعیت اتصال"""
        if connected:
            prefix = "🤖" if is_bot else "👤"
            self.status_label.configure(
                text="● CONNECTED",
                text_color=COLORS["accent_green"]
            )
            self.user_label.configure(
                text=f"{prefix} {username}",
                text_color=COLORS["text_secondary"]
            )
        else:
            self.status_label.configure(
                text="● DISCONNECTED",
                text_color=COLORS["accent_red"]
            )
            self.user_label.configure(
                text="No token loaded",
                text_color=COLORS["text_dim"]
            )