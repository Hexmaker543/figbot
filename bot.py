import discord
from discord.ext import commands
from os import getenv
from sys import exit
from dotenv import load_dotenv


load_dotenv()
try:
    TOKEN = getenv("TOKEN")
    SERVER_ID = int(getenv("SERVER_ID"))
except Exception as e:
    print(e)
    exit()


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

        await self.load_extension("cogs.role")

        command_count = len(
            await self.tree.sync(guild=discord.Object(id=SERVER_ID)))
        print(
            f"{command_count} command{
            's' if command_count == 1 else ''} synced")

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        pass

    async def on_message(self, message):
        pass


bot = Bot()
bot.run(TOKEN)
