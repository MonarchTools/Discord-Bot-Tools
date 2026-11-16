import discord
import asyncio
from discord.ext import commands
from modules.base_module import BaseModule
from core.token_manager import TokenManager

class ChannelCreatorModule(BaseModule):
    NAME = "Channel Creator"
    ICON = "📢"
    REQUIRES_TOKEN = True
    REQUIRES_GUILD = True

    def _build_ui(self):
        self._create_label("Server ID:", 0)
        self._create_entry("guild_id", 0, "Enter server ID...")
        self._create_label("Channel Names (comma separated):", 1)
        self._create_entry("channel_names", 1, "e.g., hacked, owned")
        self._create_label("Count:", 2)
        self._create_entry("count", 2, "Number of channels")
        self._create_button("⚡ CREATE CHANNELS", self._execute, 3, color="#008f11")

    def _execute(self):
        guild_id = self._get_entry("guild_id")
        names_str = self._get_entry("channel_names") or "hacked"
        count = self._get_entry("count")
        if not guild_id.isdigit() or not count.isdigit():
            self.logger.error("Invalid Server ID or Count")
            return
        
        names = [n.strip() for n in names_str.split(",") if n.strip()]
        self.parent.winfo_toplevel().run_in_thread(self._run_create, int(guild_id), names, int(count))

    def _run_create(self, guild_id: int, names: list, count: int):
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
                
                self.logger.info(f"Creating {count} channels...")
                async def create_one(i):
                    try:
                        name = names[i % len(names)]
                        await guild.create_text_channel(f"{name}-{i+1}")
                        self.logger.success(f"Created: {name}-{i+1}")
                        await asyncio.sleep(0.5)
                    except Exception as e:
                        self.logger.error(f"Failed: {e}")
                
                await asyncio.gather(*(create_one(i) for i in range(count)))
                self.logger.success("Channel creation completed.")
            finally:
                if not bot.is_closed(): await bot.close()

        try:
            asyncio.run(bot.start(token))
        except Exception as e:
            self.logger.error(f"Error: {e}")