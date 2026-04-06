import functools


def require_guild(func):
    @functools.wraps(func)
    async def wrapper(self, interaction, *args, **kwargs):
        if interaction.guild is None:
            return await interaction.response.send_message(
                "This command cannot be used in DMs.",
                ephemeral=True)
        return await func(self, interaction, *args, **kwargs)
    return wrapper
