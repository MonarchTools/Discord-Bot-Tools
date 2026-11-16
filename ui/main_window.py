"""پنجره اصلی پنل"""

import customtkinter as ctk
from tkinter import messagebox
import threading
from config import COLORS, WINDOW_WIDTH, WINDOW_HEIGHT, APP_NAME, APP_VERSION, FONT_TITLE
from ui.theme import apply_hacker_theme, style_window, style_frame
from ui.sidebar import Sidebar
from ui.console import Console
from core.token_manager import TokenManager
from core.logger import Logger


class MainWindow(ctk.CTk):
    """پنجره اصلی برنامه"""
    
    def __init__(self):
        super().__init__()
        
        apply_hacker_theme()
        style_window(self)
        
        self.title(f"{APP_NAME} v{APP_VERSION}")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(900, 600)
        
        # تنظیمات
        self.token_manager = TokenManager()
        self.logger = Logger()
        self.current_module_instance = None
        self.modules = []
        
        # اتصال لاگر به کنسول
        self._setup_layout()
        Logger.set_callback(self.console.log)
        
        # ثبت ماژول‌ها
        self._register_modules()
        
        # پروتکل بستن
        self.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _setup_layout(self):
        """چیدمان اصلی"""
        # گرید اصلی
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # هدر بالا
        self.header = ctk.CTkFrame(self, height=60, fg_color="#000000", corner_radius=0)
        self.header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=0, pady=0)
        self.header.grid_propagate(False)
        
        self.title_lbl = ctk.CTkLabel(
            self.header,
            text=f"█ {APP_NAME.upper()} █",
            text_color=COLORS["accent_green"],
            font=FONT_TITLE
        )
        self.title_lbl.pack(side="left", padx=20, pady=15)
        
        # دکمه‌های هدر
        self.btn_frame = ctk.CTkFrame(self.header, fg_color="transparent")
        self.btn_frame.pack(side="right", padx=20)
        
        self.disconnect_btn = ctk.CTkButton(
            self.btn_frame, text="⏻ DISCONNECT", width=130,
            fg_color="#330000", hover_color="#660000",
            text_color=COLORS["accent_red"],
            font=("Consolas", 10, "bold"),
            command=self._disconnect,
            corner_radius=3
        )
        self.disconnect_btn.pack(side="left", padx=5)
        
        self.connect_btn = ctk.CTkButton(
            self.btn_frame, text="⚡ CONNECT TOKEN", width=150,
            fg_color=COLORS["accent_dark_green"],
            hover_color=COLORS["accent_green"],
            text_color="#000000",
            font=("Consolas", 10, "bold"),
            command=self._connect_token,
            corner_radius=3
        )
        self.connect_btn.pack(side="left", padx=5)
        
        # Sidebar
        self.sidebar = Sidebar(self, self._on_module_select)
        self.sidebar.grid(row=1, column=0, sticky="nsw", padx=0, pady=0)
        
        # محتوای اصلی
        self.main_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_panel"])
        self.main_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        
        # عنوان ماژول فعلی
        self.module_title = ctk.CTkLabel(
            self.main_frame,
            text="[ SELECT A TOOL FROM SIDEBAR ]",
            text_color=COLORS["accent_green"],
            font=FONT_TITLE
        )
        self.module_title.grid(row=0, column=0, sticky="ew", padx=20, pady=15)
        
        # فرم ماژول
        self.module_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.module_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        self.module_frame.grid_columnconfigure(1, weight=1)
        
        # کنسول پایین
        self.console = Console(self.main_frame, height=180)
        self.console.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        self.main_frame.grid_rowconfigure(1, weight=1)
        
        # پیام خوش‌آمد
        self.logger.info(f"╔══════════════════════════════════════╗")
        self.logger.info(f"║  Welcome to {APP_NAME} v{APP_VERSION}")
        self.logger.info(f"╚══════════════════════════════════════╝")
        self.logger.warning("Please connect your token first...")
    
    def _register_modules(self):
        """ثبت همه ماژول‌ها"""
        # ایمپورت ماژول‌ها (lazy import)
        from modules.token_checker.module import TokenCheckerModule
        from modules.ban.module import BanModule
        from modules.kick.module import KickModule
        from modules.channel_creator.module import ChannelCreatorModule
        from modules.channel_deleter.module import ChannelDeleterModule
        from modules.role_creator.module import RoleCreatorModule
        from modules.role_deleter.module import RoleDeleterModule
        from modules.unban_all.module import UnbanAllModule
        from modules.mass_mention.module import MassMentionModule
        from modules.spam_channels.module import SpamChannelsModule
        from modules.invite_spamer.module import InviteSpamerModule
        from modules.webhook_spamer.module import WebhookSpamerModule
        
        self.modules = [
            TokenCheckerModule,
            BanModule,
            KickModule,
            ChannelCreatorModule,
            ChannelDeleterModule,
            RoleCreatorModule,
            RoleDeleterModule,
            UnbanAllModule,
            MassMentionModule,
            SpamChannelsModule,
            InviteSpamerModule,
            WebhookSpamerModule,
        ]
        
        for mod in self.modules:
            self.sidebar.add_module_button(mod)
    
    def _connect_token(self):
        """پنجره ورود توکن"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Connect Token")
        dialog.geometry("500x250")
        dialog.configure(fg_color=COLORS["bg_dark"])
        dialog.transient(self)
        dialog.grab_set()
        
        ctk.CTkLabel(
            dialog, text="⚡ ENTER DISCORD TOKEN",
            text_color=COLORS["accent_green"],
            font=("Consolas", 14, "bold")
        ).pack(pady=(20, 10))
        
        token_entry = ctk.CTkEntry(
            dialog, placeholder_text="Token here...",
            show="•", width=400,
            fg_color="#050805",
            border_color=COLORS["accent_dark_green"],
            text_color=COLORS["accent_green"],
            font=("Consolas", 12)
        )
        token_entry.pack(pady=10, padx=20)
        token_entry.focus()
        
        def do_connect():
            token = token_entry.get().strip()
            if not token:
                messagebox.showwarning("Error", "Token cannot be empty!")
                return
            try:
                info = self.token_manager.set_token(token)
                username = f"{info['username']}#{info['discriminator']}"
                self.sidebar.update_status(True, username, info['is_bot'])
                self.logger.success(f"Connected as: {username}")
                self.logger.info(f"Token type: {'BOT' if info['is_bot'] else 'USER'}")
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        ctk.CTkButton(
            dialog, text="CONNECT", command=do_connect,
            fg_color=COLORS["accent_dark_green"],
            hover_color=COLORS["accent_green"],
            text_color="#000000",
            font=("Consolas", 12, "bold"),
            width=150, height=35
        ).pack(pady=15)
    
    def _disconnect(self):
        """قطع اتصال"""
        if not self.token_manager.is_connected:
            return
        self.token_manager.clear()
        self.sidebar.update_status(False)
        self.logger.warning("Token disconnected")
    
    def _on_module_select(self, module_class):
        """انتخاب یک ماژول"""
        # بررسی نیاز به توکن
        if module_class.REQUIRES_TOKEN and not self.token_manager.is_connected:
            messagebox.showwarning(
                "Token Required",
                "Please connect your token first!"
            )
            return
        
        # پاک کردن فرم قبلی
        for widget in self.module_frame.winfo_children():
            widget.destroy()
        
        self.module_title.configure(text=f"[ {module_class.ICON}  {module_class.NAME} ]")
        
        # ساخت ماژول جدید
        try:
            self.current_module_instance = module_class(self.module_frame)
            self.logger.debug(f"Loaded module: {module_class.NAME}")
        except Exception as e:
            self.logger.error(f"Failed to load module: {e}")
    
    def run_in_thread(self, func, *args, **kwargs):
        """اجرای تابع در thread جداگانه (برای جلوگیری از فریز UI)"""
        def wrapper():
            try:
                func(*args, **kwargs)
            except Exception as e:
                self.logger.error(f"Error: {e}")
        t = threading.Thread(target=wrapper, daemon=True)
        t.start()
    
    def _on_close(self):
        """بستن برنامه"""
        self.token_manager.clear()
        self.destroy()