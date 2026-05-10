import discord
from discord import app_commands
from discord.ext import commands



class Purge(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    # Purge command
    @app_commands.command(
        name='purge',
        description='Command to purge messages from a channel')
    @app_commands.default_permissions(administrator=True)
    @app_commands.guild_only
    async def purge(self, interaction: discord.Interaction, amount: int = 0):
        await interaction.response.defer(ephemeral=True)
        amount = amount or None
        messages = await interaction.channel.purge(limit=amount)
        msg = await interaction.followup.send(
            f"Amount of messages deleted: {len(messages)}")
        if isinstance(msg, discord.Message): await msg.delete(delay=3)

async def setup(bot: commands.Bot):
    await bot.add_cog(Purge(bot))
