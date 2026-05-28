import discord
from discord.ext import commands

import os

from credentials import TOKEN


intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

CORE_EXTENSIONS = ["cogs._update"]

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
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py') and not filename.startswith('_'):
                try:
                    await self.reload_extension(f'cogs.{filename[:-3]}')
                except commands.ExtensionNotLoaded:
                    await self.load_extension(f"cogs.{filename[:-3]}")

    async def _load_core_extensions(self):
        for extension in CORE_EXTENSIONS:
            await self.load_extension(extension)


bot = Bot()
bot.run(TOKEN)
