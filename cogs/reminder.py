import discord
from discord import app_commands
from discord.ext import commands

from datetime import datetime

from utils.message import send_temporary_message


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
        button_pressed = {'name' : False, 'desc' : False}
        def add_text_displays():
            if button_pressed['name']:
                self.container.add_item(discord.ui.TextDisplay(
                    content=f'**Name:** {self.reminder_name}'))
            if button_pressed['desc']:
                self.container.add_item(discord.ui.TextDisplay(
                    content=f'**Description:** {self.reminder_desc}'))

        async def refresh_container():
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

        async def update_name_or_desc(text_input: discord.TextInput, type: str):
            if text_input.value:
                button_pressed[type] = True
                if type == 'name': self.reminder_name = text_input.value
                if type == 'desc': self.reminder_desc = text_input.value
            else:
                button_pressed[type] = False
                if type == 'name':
                    self.reminder_name = self.DEFAULT_REMINDER_NAME
                if type == 'desc':
                    self.reminder_desc = self.DEFAULT_REMINDER_DESC
            await refresh_container()


        async def on_set_name(interaction: discord.Interaction):
            text_prompt = discord.ui.Modal(title='Set Reminder Name')

            text_input = discord.ui.TextInput(
                label='3-16 Characters. This is optional.',
                placeholder='Reminder Name',
                required=False,
                min_length=3,
                max_length=16)
            text_prompt.add_item(text_input)

            async def on_submit(interaction: discord.Interaction):
                await update_name_or_desc(text_input, 'name')
                await send_temporary_message(interaction)
            text_prompt.on_submit = on_submit

            await interaction.response.send_modal(text_prompt)

        async def on_set_desc(interaction: discord.Interaction):
            text_prompt = discord.ui.Modal(title='Set Description')

            text_input = discord.ui.TextInput(
                label='200 Character Limit. This is optional.',
                placeholder='Short description',
                style=discord.TextStyle.long,
                required=False,
                max_length=200)
            text_prompt.add_item(text_input)

            async def on_submit(interaction: discord.Interaction):
                await update_name_or_desc(text_input, 'desc')
                await send_temporary_message(interaction)
            text_prompt.on_submit = on_submit

            await interaction.response.send_modal(text_prompt)

        name_button = discord.ui.Button(label='Set Name')
        desc_button = discord.ui.Button(label='Set Description')
        name_button.callback = on_set_name
        desc_button.callback = on_set_desc

        self.container.add_item(discord.ui.TextDisplay(
            "Set a name and description (Optional)."))
        self.container.add_item(discord.ui.ActionRow(name_button, desc_button))
        add_text_displays()

    def _add_time_select(self):
        pass

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
