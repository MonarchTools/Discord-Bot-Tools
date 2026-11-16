import discord
import asyncio
from discord.ext import commands
from modules.base_module import BaseModule
from core.token_manager import TokenManager

class InviteSpamerModule(BaseModule):
    NAME = "DM Spam (Invite)"
    ICON = "📨"
    REQUIRES_TOKEN = True
    REQUIRES_GUILD = True

    def _build_ui(self):
        self._create_label("Server ID:", 0)
        self._create_entry("guild_id", 0, "Enter server ID...")
        self._create_label("Message:", 1)
        self._create_entry("message", 1, "Message to send in DM...")
        self._create_button("⚡ SEND TO ALL MEMBERS", self._execute, 2, color="#008f11")

    def _execute(self):
        guild_id = self._get_entry("guild_id")
        message = self._get_entry("message")
        if not guild_id.isdigit() or not message:
            self.logger.error("Invalid inputs")
            return
        self.parent.winfo_toplevel().run_in_thread(self._run_spam, int(guild_id), message)

    def _run_spam(self, guild_id: int, message: str):
        token_mgr = TokenManager()
        token = token_mgr.token
        if token.lower().startswith("bot "): token = token[4:].strip()
        
        intents = discord.Intents.default()
        intents.members = True
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
                
                members = [m for m in guild.members if not m.bot]
                self.logger.info(f"Found {len(members)} members. Starting DM spam...")
                
                success, failed = 0, 0
                for member in members:
                    try:
                        await member.send(message)
                        self.logger.success(f"Sent to: {member.name}")
                        success += 1
                        await asyncio.sleep(1.5)
                    except discord.Forbidden:
                        failed += 1
                    except Exception as e:
                        self.logger.error(f"Failed {member.name}: {e}")
                        failed += 1
                
                self.logger.success(f"DM spam done! Success: {success}, Failed: {failed}")
            finally:
                if not bot.is_closed(): await bot.close()

        try:
            asyncio.run(bot.start(token))
        except Exception as e:
            self.logger.error(f"Error: {e}")