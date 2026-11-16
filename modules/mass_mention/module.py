import discord
import asyncio
from discord.ext import commands
from modules.base_module import BaseModule
from core.token_manager import TokenManager

class MassMentionModule(BaseModule):
    NAME = "Mass Mention"
    ICON = "📢"
    REQUIRES_TOKEN = True
    REQUIRES_GUILD = True

    def _build_ui(self):
        self._create_label("Server ID:", 0)
        self._create_entry("guild_id", 0, "Enter server ID...")
        self._create_label("Channel ID:", 1)
        self._create_entry("channel_id", 1, "Enter channel ID...")
        self._create_label("Message:", 2)
        self._create_entry("message", 2, "Message before mentions...")
        self._create_button("⚡ SEND MASS MENTION", self._execute, 3, color="#ffcc00")

    def _execute(self):
        guild_id = self._get_entry("guild_id")
        channel_id = self._get_entry("channel_id")
        message = self._get_entry("message")
        if not guild_id.isdigit() or not channel_id.isdigit():
            self.logger.error("Invalid IDs")
            return
        self.parent.winfo_toplevel().run_in_thread(self._run_mention, int(guild_id), int(channel_id), message)

    def _run_mention(self, guild_id: int, channel_id: int, message: str):
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
                channel = bot.get_channel(channel_id)
                if not guild or not channel:
                    self.logger.error("Server or Channel not found!")
                    await bot.close()
                    return
                
                members = [m for m in guild.members if not m.bot]
                self.logger.info(f"Mentioning {len(members)} members...")
                
                mentions = " ".join(m.mention for m in members)
                # دیسکورد محدودیت 2000 کاراکتر دارد، اگر زیاد بود تقسیم می‌کنیم
                if len(mentions) > 1800:
                    chunks = [mentions[i:i+1800] for i in range(0, len(mentions), 1800)]
                    for chunk in chunks:
                        await channel.send(f"{message}\n{chunk}")
                        await asyncio.sleep(1)
                else:
                    await channel.send(f"{message}\n{mentions}")
                
                self.logger.success("Mass mention completed!")
            finally:
                if not bot.is_closed(): await bot.close()

        try:
            asyncio.run(bot.start(token))
        except Exception as e:
            self.logger.error(f"Error: {e}")