import discord
import asyncio
from discord.ext import commands
from modules.base_module import BaseModule
from core.token_manager import TokenManager

class SpamChannelsModule(BaseModule):
    NAME = "Spam All Channels"
    ICON = "💬"
    REQUIRES_TOKEN = True
    REQUIRES_GUILD = True

    def _build_ui(self):
        self._create_label("Server ID:", 0)
        self._create_entry("guild_id", 0, "Enter server ID...")
        self._create_label("Message:", 1)
        self._create_entry("message", 1, "Message to spam...")
        self._create_label("Messages per Channel:", 2)
        self._create_entry("count", 2, "e.g., 100")
        self._create_button("⚡ START SPAM", self._execute, 3, color="#660000")

    def _execute(self):
        guild_id = self._get_entry("guild_id")
        message = self._get_entry("message")
        count = self._get_entry("count")
        if not guild_id.isdigit() or not count.isdigit() or not message:
            self.logger.error("Invalid inputs")
            return
        self.parent.winfo_toplevel().run_in_thread(self._run_spam, int(guild_id), message, int(count))

    def _run_spam(self, guild_id: int, message: str, count: int):
        token_mgr = TokenManager()
        token = token_mgr.token
        if token.lower().startswith("bot "): token = token[4:].strip()
        
        intents = discord.Intents.default()
        intents.guilds = True
        intents.message_content = True
        bot = commands.Bot(command_prefix="!", intents=intents)

        @bot.event
        async def on_ready():
            try:
                guild = bot.get_guild(guild_id)
                if not guild:
                    self.logger.error("Server not found!")
                    await bot.close()
                    return
                
                channels = guild.text_channels
                self.logger.info(f"Found {len(channels)} text channels. Spamming {count} messages each...")
                
                async def spam_channel(channel):
                    try:
                        for i in range(count):
                            await channel.send(message)
                            await asyncio.sleep(0.3)
                        self.logger.success(f"[{channel.name}] Done")
                    except Exception as e:
                        self.logger.error(f"Error in {channel.name}: {e}")
                
                await asyncio.gather(*(spam_channel(c) for c in channels))
                self.logger.success("Spam completed!")
            finally:
                if not bot.is_closed(): await bot.close()

        try:
            asyncio.run(bot.start(token))
        except Exception as e:
            self.logger.error(f"Error: {e}")