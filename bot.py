import discord
from discord.ext import commands

from credentials import TOKEN, SERVER_ID


intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents)

        self.guild = discord.Object(id=SERVER_ID)

    async def setup_hook(self):

        await self.load_extension("cogs.role")

        command_count = len(
            await self.tree.sync(guild=self.guild))
        print(
            f"{command_count} command{
            's' if command_count == 1 else ''} synced")

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")

        await self.tree.sync()

    async def on_message(self, message):
        pass


bot = Bot()
bot.run(TOKEN)
