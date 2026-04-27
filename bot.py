import discord
from discord.ext import commands

import os

from credentials import TOKEN


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

        await self.load_extensions()

        command_count = len(await self.tree.sync())
        suffix = 's' if command_count == 1 else ''
        print(f"{command_count} command{suffix} synced")

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")

    async def on_message(self, message):
        pass

    async def load_extensions(self):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py') and not filename.startswith('_'):
                await bot.load_extension(f"cogs.{filename[:-3]}")


bot = Bot()
bot.run(TOKEN)
