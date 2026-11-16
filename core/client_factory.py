"""کارخانه ساخت کلاینت دیسکورد - نسخه نهایی و پایدار"""
import discord
from core.token_manager import TokenManager

class ClientFactory:
    @staticmethod
    def create_client():
        token_mgr = TokenManager()
        if not token_mgr.is_connected:
            raise RuntimeError("ابتدا باید توکن را وارد کنید")
        
        # فعال کردن تمام Intentها برای جلوگیری از خطاهای دسترسی
        intents = discord.Intents.all()
        return discord.Client(intents=intents)
    
    @staticmethod
    def get_token() -> str:
        return TokenManager().token