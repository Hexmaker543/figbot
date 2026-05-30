import discord
from discord import app_commands
from discord.ext import commands

from datetime import datetime

from utils.ui import get_text_from_modal


class Reminder(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.init_commands()

    def init_commands(self):
        self.init_root_command()
        self.init_set_command()
        self.init_delete_command()
        self.init_list_command()

    def init_root_command(self):
        self.reminder = app_commands.Group(
            name='reminder',
            description="Commands to manage reminders",
            default_permissions=discord.Permissions(
            read_message_history=True))
        self.bot.tree.add_command(self.reminder)

    def init_set_command(self):
        @self.reminder.command(
                name='set',
                description="Set a reminder")
        @app_commands.guild_only
        async def reminder_set(interaction: discord.Interaction):
            await interaction.response.send_message(
                view=SetView(interaction),
                ephemeral=True)

    def init_delete_command(self):
        @self.reminder.command(
            name='delete',
            description="Delete one or more reminders")
        @app_commands.guild_only
        async def reminder_delete(interaction: discord.Interaction):
            await interaction.response.send_message(
                view=DeleteView(interaction),
                ephemeral=True)

    def init_list_command(self):
        @self.reminder.command(
            name='list',
            description="List your reminders")
        @app_commands.guild_only
        async def reminder_list(interaction: discord.Interaction):
            await interaction.response.send_message(
                view=ListView(interaction),
                ephemeral=True)

class SetView(discord.ui.LayoutView):
    def __init__(self, interaction: discord.Interaction):
        super().__init__()

        self.original_interaction = interaction

        current_time = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        self.DEFAULT_REMINDER_NAME = f'reminder_{current_time}'
        self.DEFAULT_REMINDER_DESC = 'No description'

        self.reminder_name = self.DEFAULT_REMINDER_NAME
        self.reminder_desc = self.DEFAULT_REMINDER_DESC

        self.time_type = None
        self.reminder_datetime = None
        self.reminder_repeats = None

        self.container = discord.ui.Container()
        self._build_ui()

    def _build_ui(self):
        self.container.add_item(discord.ui.TextDisplay(
            "# __Set a Reminder__"))
        self._add_name_and_desc()
        self._add_time_select()
        self._add_absolute_input()
        self._add_relative_input()
        self._add_submit_button()
        self.add_item(self.container)

    def _add_name_and_desc(self):
        self.container.add_item(discord.ui.TextDisplay(
            "Set a name and description (Optional)."))

        has_custom = {'name' : False, 'desc' : False}
        def add_text_displays():
            if has_custom['name']:
                self.container.add_item(discord.ui.TextDisplay(
                    content=f'**Name:** {self.reminder_name}'))
            if has_custom['desc']:
                self.container.add_item(discord.ui.TextDisplay(
                    content=f'**Description:** {self.reminder_desc}'))

        async def refresh_display():
            items_to_keep = [item
                for item in self.container.children[5:]]
            items_to_remove = [item
                for item in self.container.children[3:]]

            for item in items_to_remove:
                self.container.remove_item(item=item)
            add_text_displays()
            for item in items_to_keep:
                self.container.add_item(item=item)

            await self.original_interaction.edit_original_response(view=self)

        def update_name_or_desc(input: str, type: str):
            if input:
                has_custom[type] = True
                if type == 'name': self.reminder_name = input
                if type == 'desc': self.reminder_desc = input
            else:
                has_custom[type] = False
                if type == 'name':
                    self.reminder_name = self.DEFAULT_REMINDER_NAME
                if type == 'desc':
                    self.reminder_desc = self.DEFAULT_REMINDER_DESC

        async def on_name_button(interaction: discord.Interaction):
            name = await get_text_from_modal(
                interaction,
                title='Set Reminder Name',
                label='Give your reminder a name (Optional).',
                placeholder='(16 Character Limit)',
                max_length=16)
            update_name_or_desc(name, 'name')
            await refresh_display()

        async def on_desc_button(interaction: discord.Interaction):
            desc = await get_text_from_modal(
                interaction,
                title='Set Description',
                label='Enter a short description (Optional).',
                placeholder='(200 Character Limit)',
                max_length=200,
                style=discord.TextStyle.long)
            update_name_or_desc(desc, 'desc')
            await refresh_display()

        name_button = discord.ui.Button(label='Set Name')
        desc_button = discord.ui.Button(label='Set Description')
        name_button.callback = on_name_button
        desc_button.callback = on_desc_button

        self.container.add_item(discord.ui.ActionRow(name_button, desc_button))
        add_text_displays()

    def _add_time_select(self):
        self.container.add_item(discord.ui.TextDisplay(
            "What type of reminder would you like to set?\n\n" +
            "__Absolute:__ January 1st, 2003 at 08:00 AM\n\n" +
            "__Relative:__ In 2 days, 3 hours, and 5 minutes."))

        absolute_button = discord.ui.Button(label='absolute')
        relative_button = discord.ui.Button(label='relative')

        absolute_button.callback = lambda self: self.time_type = 'absolute'
        relative_button.callback = lambda self: self.time_type = 'relative'

    def _add_absolute_input(self):
        pass

    def _add_relative_input(self):
        pass

    def _add_submit_button(self):
        pass

class DeleteView(discord.ui.View):
    def __init__(self, interaction: discord.Interaction):
        super().__init__()

        self.original_interaction = interaction

class ListView(discord.ui.View):
    def __init__(self, interaction: discord.Interaction):
        super().__init__()

        self.original_interaction = interaction

async def setup(bot: commands.Bot):
    await bot.add_cog(Reminder(bot))
