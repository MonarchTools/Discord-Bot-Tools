"""تم هکری پنل"""

import customtkinter as ctk
from config import COLORS


def apply_hacker_theme():
    """اعمال تم هکری به کل برنامه"""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")  # پایه، سپس override می‌کنیم


def style_window(window):
    """استایل‌دهی به پنجره اصلی"""
    window.configure(fg_color=COLORS["bg_dark"])


def style_frame(frame):
    """استایل‌دهی به فریم‌ها"""
    frame.configure(
        fg_color=COLORS["bg_panel"],
        border_color=COLORS["accent_dark_green"],
        border_width=1,
        corner_radius=6
    )


def style_sidebar(frame):
    """استایل‌دهی به sidebar"""
    frame.configure(
        fg_color=COLORS["bg_sidebar"],
        border_color=COLORS["accent_dark_green"],
        border_width=1,
        corner_radius=0
    )