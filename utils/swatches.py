import discord

from dataclasses import dataclass

from config import SWATCH_SETTINGS


@dataclass(frozen=True)
class SwatchesConfig:
    font_path: str
    font_size: int = 16
    canvas_width: int = 400
    line_spacing: float = 1.2
    word_spacing: int = 1


class Swatches:
    def __init__(self, color_dict:dict[str, tuple[int, int, int]]):
        self.config = SwatchesConfig(**SWATCH_SETTINGS)
