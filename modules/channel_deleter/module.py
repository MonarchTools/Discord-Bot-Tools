import discord
import asyncio
from discord.ext import commands
from modules.base_module import BaseModule
from core.token_manager import TokenManager

class ChannelDeleterModule(BaseModule):
    NAME = "Channel Deleter"
    ICON = "🗑️"
    REQUIRES_TOKEN = True
    REQUIRES_GUILD = True

    def _build_ui(self):
        self._create_label("Server ID:", 0)
        self._create_entry("guild_id", 0, "Enter server ID...")
        self._create_button("⚡ DELETE ALL CHANNELS", self._execute, 1, color="#660000")

    def _execute(self):
        guild_id = self._get_entry("guild_id")
        if not guild_id.isdigit():
            self.logger.error("Invalid Server ID")
            return
        self.parent.winfo_toplevel().run_in_thread(self._run_delete, int(guild_id))

    def _run_delete(self, guild_id: int):
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
                
                channels = list(guild.channels)
                self.logger.info(f"Deleting {len(channels)} channels...")
                
                async def delete_one(channel):
                    try:
                        await channel.delete()
                        self.logger.success(f"Deleted: {channel.name}")
                        await asyncio.sleep(0.5)
                    except Exception as e:
                        self.logger.error(f"Failed {channel.name}: {e}")
                
                await asyncio.gather(*(delete_one(c) for c in channels))
                self.logger.success("Channel deletion completed.")
            finally:
                if not bot.is_closed(): await bot.close()

        try:
            asyncio.run(bot.start(token))
        except Exception as e:
            self.logger.error(f"Error: {e}")