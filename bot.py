import discord
from discord.ext import commands

from dotenv import load_dotenv
import os


load_dotenv()
dev_mode = True
if dev_mode:
    TOKEN = os.getenv('DEV_TOKEN')
else:
    TOKEN = os.getenv('BUILD_TOKEN')


intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents)

    async def setup_hook(self):

        await self._load_core_extensions()
        await self.load_custom_extensions()

        command_count = len(await self.tree.sync())
        suffix = 's' if command_count == 1 else ''
        print(f"{command_count} command{suffix} synced")

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")

    async def on_message(self, message):
        pass

    async def load_custom_extensions(self):
        for extension in os.listdir('./cogs'):
            if extension.endswith('.py') and not extension.startswith('_'):
                try:
                    await self.reload_extension(f'cogs.{extension[:-3]}')
                except commands.ExtensionNotLoaded:
                    await self.load_extension(f"cogs.{extension[:-3]}")

    async def _load_core_extensions(self):
        for extension in os.listdir('./core'):
            if extension.startswith('_'): continue
            await self.load_extension(f'core.{extension[:-3]}')

bot = Bot()
bot.run(TOKEN)
