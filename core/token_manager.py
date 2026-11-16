"""مدیریت یکپارچه توکن دیسکورد - نسخه بهبودیافته"""

import re
import requests
from typing import Optional, Dict, Any
from config import DISCORD_API_URL


class TokenManager:
    """مدیریت توکن به صورت singleton"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._token = None
            cls._instance._token_info = None
            cls._instance._is_bot = None
            cls._instance._token_type = None  # "bot" یا "user"
        return cls._instance
    
    @property
    def token(self) -> Optional[str]:
        return self._token
    
    @property
    def is_bot(self) -> Optional[bool]:
        return self._is_bot
    
    @property
    def info(self) -> Optional[Dict[str, Any]]:
        return self._token_info
    
    @property
    def is_connected(self) -> bool:
        return self._token is not None and self._token_info is not None
    
    def _test_token(self, token: str, as_bot: bool) -> Optional[Dict[str, Any]]:
        """تست توکن با نوع مشخص"""
        if as_bot:
            auth_header = f"Bot {token}"
        else:
            auth_header = token
        
        headers = {
            "Authorization": auth_header,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        try:
            response = requests.get(DISCORD_API_URL, headers=headers, timeout=10)
            if response.status_code == 200:
                user_data = response.json()
                return {
                    "id": user_data.get("id"),
                    "username": user_data.get("username"),
                    "discriminator": user_data.get("discriminator", "0"),
                    "email": user_data.get("email"),
                    "phone": user_data.get("phone"),
                    "mfa_enabled": user_data.get("mfa_enabled", False),
                    "premium_type": user_data.get("premium_type", 0),
                    "is_bot": user_data.get("bot", False),
                }
            return None
        except Exception:
            return None
    
    def set_token(self, token: str) -> Dict[str, Any]:
        """تنظیم توکن - تشخیص خودکار نوع آن"""
        token = token.strip()
        if not token:
            raise ValueError("توکن نمی‌تواند خالی باشد")
        
        # حذف پیشوندهای احتمالی
        if token.lower().startswith("bot "):
            token = token[4:].strip()
        
        # بررسی فرمت کلی
        if not re.match(r'^[A-Za-z0-9._\-]+$', token):
            raise ValueError("فرمت توکن نامعتبر است")
        
        # ابتدا به عنوان Bot Token تست می‌کنیم
        info = self._test_token(token, as_bot=True)
        if info:
            self._token = token
            self._is_bot = True
            self._token_type = "bot"
            self._token_info = info
            return info
        
        # اگر نشد، به عنوان User Token تست می‌کنیم
        info = self._test_token(token, as_bot=False)
        if info:
            self._token = token
            self._is_bot = False
            self._token_type = "user"
            self._token_info = info
            return info
        
        # اگر هیچکدام کار نکرد
        raise ValueError(
            "توکن نامعتبر است!\n\n"
            "• اگر Bot Token است: مطمئن شوید از Developer Portal کپی شده\n"
            "• اگر User Token است: ممکن است توسط Discord محدود شده باشد\n"
            "• توکن را Reset کنید و دوباره تلاش کنید"
        )
    
    def get_auth_header(self) -> str:
        """دریافت هدر Authorization مناسب"""
        if self._token_type == "bot":
            return f"Bot {self._token}"
        return self._token
    
    def clear(self):
        """پاک کردن توکن"""
        self._token = None
        self._token_info = None
        self._is_bot = None
        self._token_type = None