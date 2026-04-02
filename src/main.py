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

def save_config():
    with open(config_filepath, 'w') as f:
        json.dump(config, f, indent=4)


load_token()
load_server_id()
load_config()


# Client Class
class Client(commands.Bot):
    # Events
    async def on_ready(self):
        print(f'\nLogged on as {self.user}!\n')

        guild = self.get_guild(GUILD.id)
        await self.create_roles(guild=guild)
        await self.sync_commands()

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
        if None in (interaction.guild, interaction.channel): return

        ticket_category = config['commands']['verify']['category']


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

    await interaction.followup.send(f'Deleted {deleted_count} messages',
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
verify_command_permissions = {"send_messages": True}

    # embed
@verify_group.command(
    name='embed',
    description='Send an embed with a verify button to the current channel')
@app_commands.checks.has_permissions(
        **verify_command_permissions,
        administrator=True)
async def set_embed(interaction:discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    if interaction.guild is None:
        await interaction.followup.send(
        "This command cannot be used in DMs")
        return

    if not config['commands']['verify']['category']:
        await interaction.followup.send(
        "No ticket category set. Set one with '/verify category'.")
        return

    config['commands']['verify']['channel'] = interaction.channel_id
    save_config()

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

    await interaction.followup.send(view=Verify_Button(), embed=embed)

    # category command
async def set_category(interaction:discord.Interaction, category_name:int):
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

    config['commands']['verify']['category'] = category.category_id


client.run(token)
