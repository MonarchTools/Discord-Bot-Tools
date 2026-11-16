import discord
import asyncio
from discord.ext import commands
from modules.base_module import BaseModule
from core.token_manager import TokenManager


class RoleDeleterModule(BaseModule):
    NAME = "Role Deleter"
    ICON = "🗑️"
    REQUIRES_TOKEN = True
    REQUIRES_GUILD = True

    def _build_ui(self):
        self._create_label("Server ID:", 0)
        self._create_entry("guild_id", 0, "Enter server ID...")
        
        # گزینه سرعت
        self._create_label("Speed Mode:", 1)
        self._create_entry("speed", 1, "normal / fast / turbo")
        
        self._create_button("⚡ DELETE ALL ROLES", self._execute, 2, color="#660000")

    def _execute(self):
        guild_id = self._get_entry("guild_id")
        speed = self._get_entry("speed").lower() or "normal"
        
        if not guild_id.isdigit():
            self.logger.error("Invalid Server ID")
            return
        
        if speed not in ["normal", "fast", "turbo"]:
            self.logger.error("Speed must be: normal, fast, or turbo")
            return
        
        self.parent.winfo_toplevel().run_in_thread(self._run_delete, int(guild_id), speed)

    def _run_delete(self, guild_id: int, speed: str):
        token_mgr = TokenManager()
        token = token_mgr.token
        if token.lower().startswith("bot "):
            token = token[4:].strip()
        
        # تنظیمات بر اساس حالت سرعت
        # توجه: حذف رول حساس‌تر است، batch size کمتر
        speed_config = {
            "normal": {"batch_size": 3, "sleep": 0.5},
            "fast":   {"batch_size": 5, "sleep": 0.3},
            "turbo":  {"batch_size": 8, "sleep": 0.15},
        }
        
        config = speed_config[speed]
        batch_size = config["batch_size"]
        sleep_time = config["sleep"]
        
        self.logger.info(f"Speed mode: {speed.upper()} | Batch: {batch_size} | Sleep: {sleep_time}s")
        
        intents = discord.Intents.default()
        intents.guilds = True
        intents.members = True
        bot = commands.Bot(command_prefix="!", intents=intents)

        @bot.event
        async def on_ready():
            try:
                guild = bot.get_guild(guild_id)
                if not guild:
                    self.logger.error("Server not found!")
                    await bot.close()
                    return
                
                if not guild.me.guild_permissions.manage_roles:
                    self.logger.error("Bot does not have 'manage_roles' permission!")
                    await bot.close()
                    return
                
                # دریافت رول‌ها و مرتب‌سازی از پایین به بالا (برای حذف امن)
                # نکته مهم: باید از پایین شروع کنیم چون رول‌های بالا نمی‌توانند توسط رول‌های پایین حذف شوند
                roles = sorted(
                    [r for r in guild.roles if r.name != '@everyone' and not r.managed],
                    key=lambda r: r.position,
                    reverse=False  # از پایین به بالا
                )
                
                self.logger.info(f"Found {len(roles)} roles to delete.")
                
                if not roles:
                    self.logger.warning("No roles to delete.")
                    await bot.close()
                    return
                
                total_deleted = 0
                total_failed = 0
                
                # پردازش به صورت batch
                for batch_start in range(0, len(roles), batch_size):
                    batch_end = min(batch_start + batch_size, len(roles))
                    batch_roles = roles[batch_start:batch_end]
                    
                    # اجرای همزمان حذف در این batch
                    async def delete_role(role):
                        try:
                            await role.delete()
                            return ("success", role.name)
                        except Exception as e:
                            return ("failed", role.name, str(e))
                    
                    results = await asyncio.gather(*(delete_role(r) for r in batch_roles))
                    
                    for result in results:
                        if result[0] == "success":
                            total_deleted += 1
                            self.logger.success(f"Deleted: {result[1]}")
                        else:
                            total_failed += 1
                            self.logger.error(f"Failed {result[1]}: {result[2]}")
                    
                    # Sleep کوتاه بین batch‌ها
                    if batch_end < len(roles):
                        await asyncio.sleep(sleep_time)
                
                self.logger.success(f"✅ Done! Deleted: {total_deleted} | Failed: {total_failed}")
            finally:
                if not bot.is_closed():
                    await bot.close()

        try:
            asyncio.run(bot.start(token))
        except Exception as e:
            self.logger.error(f"Error: {e}")