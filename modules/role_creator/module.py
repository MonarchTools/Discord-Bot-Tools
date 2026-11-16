import discord
import asyncio
from discord.ext import commands
from modules.base_module import BaseModule
from core.token_manager import TokenManager


class RoleCreatorModule(BaseModule):
    NAME = "Role Creator"
    ICON = "🎭"
    REQUIRES_TOKEN = True
    REQUIRES_GUILD = True

    def _build_ui(self):
        self._create_label("Server ID:", 0)
        self._create_entry("guild_id", 0, "Enter server ID...")
        
        self._create_label("Role Name:", 1)
        self._create_entry("role_name", 1, "e.g., Hacked")
        
        self._create_label("Count:", 2)
        self._create_entry("count", 2, "Number of roles")
        
        # گزینه سرعت
        self._create_label("Speed Mode:", 3)
        self._create_entry("speed", 3, "normal / fast / turbo")
        
        self._create_button("⚡ CREATE ROLES", self._execute, 4, color="#008f11")

    def _execute(self):
        guild_id = self._get_entry("guild_id")
        role_name = self._get_entry("role_name") or "Hacked"
        count = self._get_entry("count")
        speed = self._get_entry("speed").lower() or "normal"
        
        if not guild_id.isdigit() or not count.isdigit():
            self.logger.error("Invalid Server ID or Count")
            return
        
        if speed not in ["normal", "fast", "turbo"]:
            self.logger.error("Speed must be: normal, fast, or turbo")
            return
        
        self.parent.winfo_toplevel().run_in_thread(
            self._run_create, int(guild_id), role_name, int(count), speed
        )

    def _run_create(self, guild_id: int, role_name: str, count: int, speed: str):
        token_mgr = TokenManager()
        token = token_mgr.token
        if token.lower().startswith("bot "):
            token = token[4:].strip()
        
        # تنظیمات بر اساس حالت سرعت
        speed_config = {
            "normal": {"batch_size": 3, "sleep": 0.5},
            "fast":   {"batch_size": 8, "sleep": 0.3},
            "turbo":  {"batch_size": 15, "sleep": 0.1},
        }
        
        config = speed_config[speed]
        batch_size = config["batch_size"]
        sleep_time = config["sleep"]
        
        self.logger.info(f"Speed mode: {speed.upper()} | Batch: {batch_size} | Sleep: {sleep_time}s")
        
        intents = discord.Intents.default()
        intents.guilds = True
        bot = commands.Bot(command_prefix="!", intents=intents)

        @bot.event
        async def on_ready():
            try:
                guild = bot.get_guild(guild_id)
                if not guild:
                    self.logger.error("Server not found!")
                    await bot.close()
                    return
                
                self.logger.info(f"Connected to: {guild.name}")
                self.logger.info(f"Creating {count} roles named '{role_name}'...")
                
                total_created = 0
                total_failed = 0
                
                # پردازش به صورت batch
                for batch_start in range(0, count, batch_size):
                    batch_end = min(batch_start + batch_size, count)
                    batch_tasks = []
                    
                    for i in range(batch_start, batch_end):
                        batch_tasks.append(
                            guild.create_role(name=f"{role_name} {i+1}")
                        )
                    
                    # اجرای همزمان batch
                    results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                    
                    for i, result in enumerate(results):
                        role_num = batch_start + i + 1
                        if isinstance(result, Exception):
                            total_failed += 1
                            self.logger.error(f"Failed {role_name} {role_num}: {result}")
                        else:
                            total_created += 1
                            self.logger.success(f"Created: {role_name} {role_num}")
                    
                    # Sleep کوتاه بین batch‌ها (نه بین هر رول)
                    if batch_end < count:
                        await asyncio.sleep(sleep_time)
                
                self.logger.success(f"✅ Done! Created: {total_created} | Failed: {total_failed}")
            finally:
                if not bot.is_closed():
                    await bot.close()

        try:
            asyncio.run(bot.start(token))
        except Exception as e:
            self.logger.error(f"Error: {e}")