import discord
import asyncio
from discord.ext import commands
from modules.base_module import BaseModule
from core.token_manager import TokenManager

class UnbanAllModule(BaseModule):
    NAME = "Unban All"
    ICON = "🔓"
    REQUIRES_TOKEN = True
    REQUIRES_GUILD = True

    def _build_ui(self):
        self._create_label("Server ID:", 0)
        self._create_entry("guild_id", 0, "Enter server ID...")
        self._create_button("⚡ UNBAN ALL USERS", self._execute, 1, color="#008f11")

    def _execute(self):
        guild_id = self._get_entry("guild_id")
        if not guild_id.isdigit():
            self.logger.error("Invalid Server ID")
            return
        self.parent.winfo_toplevel().run_in_thread(self._run_unban, int(guild_id))

    def _run_unban(self, guild_id: int):
        token_mgr = TokenManager()
        token = token_mgr.token
        if token.lower().startswith("bot "): token = token[4:].strip()
        
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
                
                bans = [ban async for ban in guild.bans()]
                self.logger.info(f"Total banned users: {len(bans)}")
                
                for ban_entry in bans:
                    try:
                        await guild.unban(ban_entry.user)
                        self.logger.success(f"Unbanned: {ban_entry.user.name}")
                        await asyncio.sleep(1)
                    except Exception as e:
                        self.logger.error(f"Failed: {e}")
                
                self.logger.success("All users unbanned!")
            finally:
                if not bot.is_closed(): await bot.close()

        try:
            asyncio.run(bot.start(token))
        except Exception as e:
            self.logger.error(f"Error: {e}")