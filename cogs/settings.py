import discord
from discord import app_commands
from discord.ext import commands


class Settings(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        self._create_settings_command()

    def _create_settings_command(self):
        @self.bot.tree.command(
            name='settings',
            description='Set your user settings for the server'
        )
        @app_commands.default_permissions(send_messages=True)
        @app_commands.guild_only()
        async def settings(interaction: discord.Interaction):
            interaction.response.send_message(
                view=SettingsView(interaction),
                ephemeral=True
            )


class SettingsView(discord.ui.LayoutView):
    def __init__(self, interaction: discord.Interaction):
        super().__init__()
        self.user = interaction.user
        self.original_message = interaction.message
        self.original_channel = interaction.channel

        self.timezone = None
        self._build_ui()

    async def _build_ui(self):
        self.container = discord.ui.Container()
        self.add_item(
            discord.ui.TextDisplay(
                f"# {self.user.display_name.capitalize()}'s Settings"
            )
        )
        self.add_item(discord.ui.Separator())
        self.add_item(self.container)


async def setup(bot: commands.Bot):
    await bot.add_cog(Settings(bot))
