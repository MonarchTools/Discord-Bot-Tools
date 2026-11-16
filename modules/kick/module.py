import discord
import asyncio
from discord.ext import commands
from modules.base_module import BaseModule
from core.token_manager import TokenManager

class KickModule(BaseModule):
    NAME = "Mass Kick"
    ICON = "🥾"
    REQUIRES_TOKEN = True
    REQUIRES_GUILD = True

    def _build_ui(self):
        self._create_label("Server ID:", 0)
        self._create_entry("guild_id", 0, "Enter server ID...")
        self._create_label("Kick Count (or 'all'):", 1)
        self._create_entry("kick_count", 1, "Number or 'all'")
        self._create_button("⚡ EXECUTE KICK", self._execute, 2, color="#660000")

    def _execute(self):
        guild_id = self._get_entry("guild_id")
        kick_count = self._get_entry("kick_count")
        if not guild_id.isdigit() or not kick_count:
            self.logger.error("Invalid Server ID or Count")
            return
        self.parent.winfo_toplevel().run_in_thread(self._run_kick, int(guild_id), kick_count)

    def _run_kick(self, guild_id: int, kick_count: str):
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
                limit = len(members) if kick_count.lower() == "all" else min(int(kick_count), len(members))
                self.logger.info(f"Starting to kick {limit} members...")

                async def kick_one(member):
                    try:
                        await member.kick(reason="Mass kick by panel")
                        self.logger.success(f"Kicked: {member.name}")
                    except Exception as e:
                        self.logger.error(f"Failed {member.name}: {e}")

                await asyncio.gather(*(kick_one(m) for m in members[:limit]))
                self.logger.success(f"Done! {limit} members kicked.")
            finally:
                if not bot.is_closed(): await bot.close()

        try:
            asyncio.run(bot.start(token))
        except Exception as e:
            self.logger.error(f"Error: {e}")