import discord
from discord import app_commands
from discord.ext import commands

from typing import Literal, Optional
import sys, os, asyncio



class Update(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Update command
    @app_commands.command(
        name='update',
        description="Commands for updating and rebooting the bot")
    @app_commands.default_permissions(administrator=True)
    @app_commands.guild_only
    async def update(
        self,
        interaction: discord.Interaction,
        mode: Optional[Literal["reboot"]] = None):
        await interaction.response.defer(ephemeral=True)

        try: await self._pull_github_repo()
        except Exception as e: 
            print(e)
            msg = await interaction.followup.send(
                "Error. Check logs for details.")
            if isinstance(msg, discord.Message): await msg.delete(delay=5)
            return

        if mode is None: await self._reload_custom_extensions(interaction)
        if mode == 'reboot': await self._reboot_bot(interaction)

    async def _pull_github_repo(self):
        pull_process = await asyncio.create_subprocess_exec(
            "git", "pull",
            stderr=asyncio.subprocess.PIPE)
        _, stderr = await pull_process.communicate()
        if pull_process.returncode != 0:
            raise Exception(stderr.decode())

    async def _reload_custom_extensions(self, interaction:discord.Interaction):
        await self.bot.load_custom_extensions()
        msg = await interaction.followup.send("Extensions reloaded")
        if isinstance(msg, discord.Message): await msg.delete(delay=3)
        return

    async def _reboot_bot(self, interaction:discord.Interaction):
        msg = await interaction.followup.send(f"Figbot rebooting.")
        if isinstance(msg, discord.Message): await msg.delete(delay=3)
        await asyncio.sleep(4)
        os.execv(sys.executable, [sys.executable] + sys.argv)


async def setup(bot: commands.Bot):
    await bot.add_cog(Update(bot))
