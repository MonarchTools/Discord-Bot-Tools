import discord
import asyncio
from discord.ext import commands
from modules.base_module import BaseModule
from core.token_manager import TokenManager

class BanModule(BaseModule):
    NAME = "Mass Ban"
    ICON = "🔨"
    REQUIRES_TOKEN = True
    REQUIRES_GUILD = True

    def _build_ui(self):
        self._create_label("Server ID:", 0)
        self._create_entry("guild_id", 0, "Enter server ID...")
        self._create_label("Ban Count (or 'all'):", 1)
        self._create_entry("ban_count", 1, "Number or 'all'")
        self._create_label("Ban Message (DM):", 2)
        self._create_entry("ban_message", 2, "Message to send before ban...")
        self._create_button("⚡ EXECUTE BAN", self._execute, 3, color="#660000")

    def _execute(self):
        guild_id = self._get_entry("guild_id")
        ban_count = self._get_entry("ban_count")
        ban_message = self._get_entry("ban_message")
        if not guild_id.isdigit() or not ban_count:
            self.logger.error("Invalid Server ID or Count")
            return
        self.parent.winfo_toplevel().run_in_thread(self._run_ban, int(guild_id), ban_count, ban_message)

    def _run_ban(self, guild_id: int, ban_count: str, ban_message: str):
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
                limit = len(members) if ban_count.lower() == "all" else min(int(ban_count), len(members))
                self.logger.info(f"Starting to ban {limit} members...")

                async def ban_one(member):
                    try:
                        if ban_message:
                            try:
                                if member.dm_channel is None: await member.create_dm()
                                await member.dm_channel.send(f"**{ban_message}**")
                            except: pass
                        await guild.ban(member, reason="Mass ban by panel")
                        self.logger.success(f"Banned: {member.name}")
                    except Exception as e:
                        self.logger.error(f"Failed {member.name}: {e}")

                await asyncio.gather(*(ban_one(m) for m in members[:limit]))
                self.logger.success(f"Done! {limit} members banned.")
            finally:
                if not bot.is_closed(): await bot.close()

        try:
            asyncio.run(bot.start(token))
        except Exception as e:
            self.logger.error(f"Error: {e}")