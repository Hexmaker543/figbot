from enum import verify
import discord
import json
import webcolors
import sys
from discord.ext import commands
from discord import app_commands


token = ''
token_filepath = 'token.txt'
def load_token():
    try:
        with open(token_filepath, 'r') as f:
            global token
            token = f.read()
            print('Token Loaded')
    except FileNotFoundError: 
        print(f"Token file '{token_filepath}' could not be loaded, ensure"+
              "file exists and try again. \n")
        sys.exit()

server_id = 0
server_id_filepath = 'server_id.txt'
def load_server_id():
    try:
        with open(server_id_filepath, 'r') as f:
            global server_id
            server_id = int(f.read())
            print('Server ID Loaded')
    except  ValueError:
        print(f"Server ID file '{server_id_filepath}' must contain int value")
        sys.exit()
    except FileNotFoundError: 
        print(f"Server ID file '{server_id_filepath}' could not be loaded, ensure"+
              "file exists and try again. \n")
        sys.exit()

config = {}
config_filepath = 'config.json'
def load_config():
    try: 
        with open(config_filepath, 'r') as f: 
            global config
            config = json.load(f)
            print('Config Loaded\n')
    except FileNotFoundError: 
        print(f"Config file '{config_filepath}' could not be loaded, ensure"+
              "file exists and try again. \n")
        sys.exit()

command_data = {}
commands_filepath = 'commands.json'
def load_commands():
    try: 
        with open(commands_filepath, 'r') as f: 
            global command_data
            command_data = json.load(f)
            print('Commands Loaded\n')
    except FileNotFoundError: 
        print(f"Config file '{config_filepath}' could not be loaded, ensure"+
              "file exists and try again. \n")
        sys.exit()

def save_config():
    with open(config_filepath, 'w') as f:
        json.dump(config, f, indent=4)

def save_commands():
    with open(commands_filepath, 'w') as f:
        json.dump(command_data, f, indent=4)


load_token()
load_server_id()
load_config()
load_commands()


# Client Class
class Client(commands.Bot):
    # Events
    async def on_ready(self):
        print(f'\nLogged on as {self.user}!\n')

        guild = self.get_guild(GUILD.id)
        await self.create_roles(guild=guild)
        await self.sync_commands()

        await send_embed()

    async def on_message(self, message):
        if message.author == self.user: return
        if message.guild is None: return
        if message.guild.id != GUILD.id: return 

        normalized_message = self.normalize_string(message.content)
        if any(word in normalized_message 
               for word in config['banned_words']):
            await message.delete()

    # Methods
    def normalize_string(self, string):
        substitutions = {
            "1": "i", "3": "e", "4": "a", "0": "o",
            "5": "s", "7": "t", "@": "a", "$": "s",
            "!": "i", "+": "t",}

        normalized_message = "".join(
            substitutions[char] if char in substitutions else char
            for char in string.lower())

        normalized_message = "".join(
            char.lower()
            for char in normalized_message
            if char.isascii() and char.isalpha())

        return normalized_message

    async def sync_commands(self):
        try:
            command_count = len(await self.tree.sync(guild=GUILD))
            print(f'Synced {command_count} commands to server: {server_id}\n')
        except Exception as e:
            print(f'Failed to sync commands: {e}')

    async def create_roles(self, guild):

        for role_category in config['roles']:
            for role_name in config['roles'][role_category].keys():
                if role_category == 'grouped permissions': continue
                existing_role = discord.utils.get(guild.roles, name=role_name)
                if existing_role: continue

                if role_category in config[
                    'roles'][
                    'grouped permissions'].keys():
                    perms = discord.Permissions(
                        **{
                            permission: True 
                            for permission in config[
                                'roles'][
                                'grouped permissions'][
                                role_category]})
                else:
                    perms = discord.Permissions(
                        **{
                            permission: True
                            for permission in config[
                                'roles'][
                                role_category][
                                role_name][
                                'permissions']})

                role_data = config['roles'][role_category][role_name]
                if role_data['color']: 
                    color=discord.Color.from_rgb(*role_data['color'])
                else: color = discord.Color.default()

                await guild.create_role(
                    name=role_name,
                    color = color,
                    hoist=role_data.get('hoist', False),
                    mentionable=role_data.get('mentionable', False),
                    permissions=perms)


# verify button
class Verify_Button(discord.ui.View):
    @discord.ui.button(
        label="Create Verification Ticket", 
        style=discord.ButtonStyle.green)
    async def verification_button_callback(
        self,
        interaction:discord.Interaction,
        button:discord.ui.Button):
        if interaction.guild is None: return

        ticket_category = interaction.guild.get_channel(
            command_data['verify']['category'])

        if not isinstance(ticket_category, discord.CategoryChannel):
            await interaction.response.send_message(
                "'Ticket category' is not a category. Notify admin",
                ephemeral=True)
            return

        channel_name=(
                f"verification-ticket-{command_data['verify']['count']}")
        verified_role = discord.utils.get(
            interaction.guild.roles, name='Verified')

        if verified_role is None:
            await interaction.response.send_message(
                "No verified role detected. Alert admin.",
                ephemeral=True)
            return

        channel_overwrites= {
            verified_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(
                view_channel = True,
                read_messages = True,
                send_messages = True
            )
        }

        await ticket_category.create_text_channel(
            name=channel_name,
            overwrites=channel_overwrites)
        command_data['verify']['count'] += 1
        save_commands()

        ticket_channel = discord.utils.get(
            interaction.guild.channels, name=channel_name)
        if not isinstance(ticket_channel, discord.TextChannel):
            await interaction.response.send_message(
                    "Ticket channel could not be created, alert admin.",
                ephemeral=True)
            return

        await ticket_channel.send(
            f"<@{interaction.user.id}>\n"+
            "# You will need to send:\n"+
            "\n"
            "**An image of you and your photo ID.** "+
                "The only information you must leave "+
                "visible is your face and birthday.\n"+
            "\n"+
            "**A paper with the name of the server on it and "+
                "the current date.**\n"+
            "\n"+
            "**An image of you with the paper.**\n"+
            "\n"+
            "# Once you've sent them:\n"+
            "\n"+
            "@ the admins, one of them will come and verify you \n"+
            "and your pictures will be deleted.")

        await interaction.response.send_message(
            f"Ticket opened in <#{ticket_channel.id}>",
            ephemeral=True)


intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = Client(command_prefix="!", intents=intents)

# GUILD Definition
GUILD = discord.Object(id=server_id)

# purge command
@client.tree.command(
    name='purge', 
    description='Purge messages. Leave blank to purge all.', 
    guild=GUILD)
@app_commands.checks.has_permissions(
    manage_messages=True, read_message_history=True)
@app_commands.describe(
    message_count="Number of messages to delete. Leave blank ")
async def purge(
    interaction:discord.Interaction,
    message_count:int|None=None):
    if not isinstance(interaction.channel, discord.TextChannel): return

    await interaction.response.defer(ephemeral=True)
    deleted_count = len(await interaction.channel.purge(limit=message_count))

    await interaction.followup.send(
        f'Deleted {deleted_count} messages',
        ephemeral=True)
@purge.error
async def purge_error(
    interaction: discord.Interaction, 
    error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(
            "You don't have permission to do that.", ephemeral=True)
    else: raise error

# color command
color_group = app_commands.Group(
    name='color', 
    description='Commands for assigning color roles' )
client.tree.add_command(color_group, guild=GUILD) 
color_command_permissions = {
    "send_messages" : True}

    # set command
@color_group.command(
    name='set',
    description='Set your color role',)
@app_commands.checks.has_permissions(**color_command_permissions)
@app_commands.describe(
    color_name = "The name of the color you'd like to assign to yourself. "+
                 "Leave blank to reset your color to default")
async def set(
    interaction:discord.Interaction,
    color_name:str|None=None):
    await interaction.response.defer(ephemeral=True)

    if color_name:
        color_name = ''.join([
            word.strip().lower() 
            for word in color_name.strip().split(' ')])

    available_colors = webcolors.names(spec='css3')
    if color_name and color_name not in available_colors:
        await interaction.followup.send(
            "Color not available, please use the '/color list' command to "+
            "view all available colors.")
        return

    if interaction.guild is None:
        await interaction.followup.send(
            "This command does not work in DMs")
        return

    member = interaction.guild.get_member(interaction.user.id)
    if member is None:
        await interaction.followup.send(
            "Error. Please alert the admins. Code: CEC-M")
        return

    existing_color_roles = [
        role
        for role in interaction.guild.roles
        if role.name in available_colors]

    await member.remove_roles(*existing_color_roles)

    for role in existing_color_roles: 
        if not role.members: await role.delete()

    existing_color_roles = [
        role
        for role in interaction.guild.roles
        if role.name in available_colors]

    if color_name is None:
        await member.remove_roles(*existing_color_roles)
        await interaction.followup.send(
        "You are now colorless!")
        return

    if existing_color_roles and color_name in [
        role.name for role in existing_color_roles]:

        color_role = next((
            role 
            for role in existing_color_roles
            if role.name == color_name), None)

        if color_role is None:
            await interaction.followup.send(
                "Error. Please alert the admins. Code: CEC-R")
            return

        await member.add_roles(color_role)

    else:
        color = int(webcolors.name_to_hex(color_name, spec='css3')[1:], 16)
        color_role = await interaction.guild.create_role(
            name= color_name,
            color = color,
            hoist= False,
            mentionable= False)

        await member.add_roles(color_role)

    await interaction.followup.send(
        f"You are now {color_name}!")

    # list command
@color_group.command(
    name='list',
    description='Display a list of all available colors')
@app_commands.checks.has_permissions(administrator=True)
async def list_colors(interaction:discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    if interaction.guild is None:
        await interaction.followup.send(
                "This command does not work in DMs")
        return

    swatch_imgs = []
    for index in range(15):
        swatch_imgs.append(discord.File(fp=f"../assets/swatch{index+1}.png"))

    if not isinstance(interaction.channel, discord.TextChannel):
        await interaction.followup.send(
        "This command cannot be used in this type of channel.")
        return

    await interaction.channel.send("# Available Colors")
    for img in swatch_imgs:
        await interaction.channel.send(file=img)

    await interaction.channel.send("*Use '/color set' to set your color!*")

    await interaction.followup.send("Color list is now being shown")


if __name__ != "__main__":
    print("This script cannot be run as a module.")
    sys.exit()

# verify command
verify_group = app_commands.Group(
    name='verify',
    description="Commands to setup and complete the verification process.")
client.tree.add_command(verify_group, guild=GUILD)
verify_command_permissions = {"administrator": True}

    # embed
async def send_embed():
    embed = discord.Embed(
    title='Verification',
    description="You must verify your age to join the server",
    color=config['dionysus theme']['red'])

    embed.add_field(
        name="What you'll need: ", 
        value=
            "Photo ID with your birthday on it,\n"+
            "Something to write with,\n"+
            "Something to write on,\n"+
            "A functional camera.\n",
        inline=False)

    embed.add_field(
        name="When you're ready, press the button below to verify",
        value='',
        inline=False)

    embed_channel = client.get_channel(
        command_data['verify']['channel'])
    if not isinstance(embed_channel, discord.TextChannel): return

    await embed_channel.purge()
    await embed_channel.send(view=Verify_Button(), embed=embed)

@verify_group.command(
    name='embed',
    description='Send an embed with a verify button to the current channel')
@app_commands.checks.has_permissions(**verify_command_permissions)
async def set_embed(interaction:discord.Interaction):

    if interaction.guild is None:
        await interaction.response.send_message(
        "This command cannot be used in DMs",
        ephemeral=True)
        return

    if not command_data['verify']['category']:
        await interaction.response.send_message(
            "No ticket category set. Set one with '/verify category'.",
            ephemeral=True)
        return

    if not isinstance(interaction.channel, discord.TextChannel):
        await interaction.response.send_message(
            "This command can only be used in a text channel.")
        return

    if not command_data['verify']['channel']:
        command_data['verify']['channel'] = interaction.channel.id
        save_commands()

    if not isinstance(interaction.channel, discord.TextChannel):
        await interaction.response.send_message(
            "This command must be used in a text channel.",
            ephemeral=True)
        return

    await interaction.response.send_message("Embed sent.", ephemeral=True)
    await send_embed()

    # category command
@verify_group.command(
    name='category',
    description='Set a category to create verification tickets in')
@app_commands.checks.has_permissions(**verify_command_permissions)
@app_commands.describe(
    category_name = 'Name of the category where tickets will be created')
async def set_category(interaction:discord.Interaction, category_name:str):
    await interaction.response.defer(ephemeral=True)

    if interaction.guild is None:
        await interaction.followup.send("This command cannot be used in DMs")
        return

    category = discord.utils.get(
        interaction.guild.channels, 
        name=category_name)

    if category is None:
        await interaction.followup.send(
            f"'{category_name}' is not a valid category, ensure proper "+
            "spelling and try again")
        return

    command_data['verify']['category'] = category.id
    save_commands()

    await interaction.followup.send("Category set.")

    # accept command
@verify_group.command(
    name='accept',
    description='Accept this ticket.')
@app_commands.checks.has_permissions(**verify_command_permissions)
async def accept_ticket(interaction:discord.Interaction):

    await interaction.response.defer(ephemeral=True)

    if interaction.guild is None:
        await interaction.followup.send("This command cannot be used in DMs")
        return

    if not isinstance(interaction.channel, discord.TextChannel):
        await interaction.followup.send(
            "This command must be used in a text channel")
        return

    if client.user is None:
        await interaction.followup.send("Error, no client user.")
        return

    verified_role = discord.utils.get(
        interaction.guild.roles, name="Verified")

    if verified_role is None:
        await interaction.followup.send("No verified role.")
        return

    for member in interaction.channel.members:
        if client.user.id == member.id: continue
        if member.guild_permissions.administrator: continue
        await member.add_roles(verified_role)

    await interaction.followup.send(
        "Added 'Verified' role to user.")

    await close_ticket(interaction.channel)

    # deny command


async def close_ticket(channel:discord.TextChannel):
    pass


client.run(token)
