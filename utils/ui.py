import discord
import asyncio
from utils.message import send_temporary_message


async def get_text_from_modal(
    interaction: discord.Interaction,
    title: str,
    label: str,
    placeholder: str,
    required: bool = False,
    min_length: int | None = None,
    max_length: int | None = None,
    timeout: float = 300,
    style: discord.TextStyle = discord.TextStyle.short) -> str | None:
    modal = discord.ui.Modal(title=title)

    text_input = discord.ui.TextInput(
        label=label,
        placeholder=placeholder,
        style=style,
        required=required,
        min_length=min_length,
        max_length=max_length)
    modal.add_item(text_input)

    submitted = asyncio.Event()
    user_input = None

    async def on_submit(modal_interaction: discord.Interaction):
        nonlocal user_input
        user_input = text_input.value
        await send_temporary_message(modal_interaction)
        submitted.set()

    modal.on_submit = on_submit
    await interaction.response.send_modal(modal)

    try:
        await asyncio.wait_for(submitted.wait(), timeout=timeout)
    except asyncio.TimeoutError:
        return None

    return user_input
