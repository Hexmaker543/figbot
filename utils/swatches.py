import discord

from dataclasses import dataclass

from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

from config import SWATCH_SETTINGS

@dataclass(frozen=True)
class SwatchesConfig:
    font_path: str = ''
    font_size: int = 16
    max_canvas_height = 300
    canvas_width: int = 400
    padding: tuple[int] = (1, 1, 1, 1)
    line_spacing: float = 1.2
    word_spacing: int = 1


class Swatches:
    def __init__(self, color_dict:dict[str, tuple[int, int, int]]):
        self.config = SwatchesConfig(**SWATCH_SETTINGS)
        self.color_dict = color_dict
        self._set_font()
        self._set_line_height()
        self._set_canvas_height()
        self._create_canvas()
        self._draw_swatches()

    def send(self, interaction: discord.Interaction):
        pass

    def _set_font(self):
        if self.config.font_path == '': self.config.font_path = None
        self.font = ImageFont.truetype(self.config.font_path, self.config.font_size)

    def _set_canvas_height(self):
        color_names = self.color_dict.keys()
        line_width_count = 0
        line_count = 1

        for color_name in color_names:
            name_width = self.font.getlength(f"{color_name}{' ' * self.config.word_spacing}")
            line_width_count += name_width
            if (line_width_count + self.config.padding[0] + self.config.padding[2]
                >= self.config.canvas_width):
                line_width_count = name_width
                line_count += 1

        self.canvas_height = (
                (line_count * self.line_height)
                + (self.config.padding[1] + self.config.padding[3]))

    def _set_line_height(self) -> int:
        ascent, descent = self.font.getmetrics()
        max_char_height = ascent + descent
        self.line_height = int(max_char_height)

    def _create_canvas(self):
        self.img = Image.new(
                mode='RGBA',
                color=(0, 0, 0, 0),
                size=(self.config.canvas_width, self.canvas_height))

    def _draw_swatches(self):
        draw = ImageDraw.Draw(self.img)

        color_names = self.color_dict.keys()
        line_string = ''
        line_count = 0
        line_step = self.line_height * self.config.line_spacing
        y = self.config.padding[1]
        buffers = []
        for color_name in color_names:
            new_line_string = (
            f"{line_string}{color_name}{' ' * self.config.word_spacing}")

            new_line_string_width = self.font.getlength(new_line_string)

            new_line_string_too_long = (
                new_line_string_width
                    >= (self.config.canvas_width
                        - (self.config.padding[0]
                           + self.config.padding[2])))

            height_padding = self.config.padding[1] + self.config.padding[3]
            reached_height_limit = (
                y + self.line_step 
                >= self.config.max_canvas_height
                   - self.config.padding[3]
            )

            if reached_height_limit:
                pass

            if new_line_string_too_long:
                draw.text(
                    (self.config.padding[0], y),
                    line_string,
                    font=self.font)
                new_line_string = f"{color_name}{' ' * self.config.word_spacing}"
                line_count += 1
                y += line_step

            line_string = new_line_string
