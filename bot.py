import discord
from discord import app_commands
from discord.ext import commands


class Bot(commands.Bot):
    async def on_ready(self):
        pass

    async def on_message(self, message):
        pass
