"""سیستم لاگ مشترک برای همه ماژول‌ها"""

import datetime
from typing import Callable, Optional


class Logger:
    """لاگر مرکزی که خروجی را به کنسول UI می‌فرستد"""
    _instance = None
    _callback: Optional[Callable] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def set_callback(cls, callback: Callable):
        """تنظیم تابع callback برای نمایش لاگ در UI"""
        cls._callback = callback
    
    def _emit(self, level: str, message: str, color: str = "green"):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        formatted = f"[{timestamp}] [{level}] {message}"
        if self._callback:
            self._callback(formatted, color)
        print(formatted)
    
    def info(self, msg: str):
        self._emit("INFO", msg, "#00ff41")
    
    def success(self, msg: str):
        self._emit("OK", msg, "#00ff41")
    
    def warning(self, msg: str):
        self._emit("WARN", msg, "#ffcc00")
    
    def error(self, msg: str):
        self._emit("ERR", msg, "#ff0033")
    
    def debug(self, msg: str):
        self._emit("DBG", msg, "#008f11")