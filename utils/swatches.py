import discord

from dataclasses import dataclass

from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

from config import SWATCH_SETTINGS

@dataclass(frozen=True)
class SwatchesConfig:
    font_path: str = ''
    font_size: int = 16
    canvas_width: int = 400
    canvas_height: int = 300
    padding: tuple[int] = (1, 1, 1, 1)
    line_spacing: float = 1.2
    word_spacing: int = 1


class Swatches:
    def __init__(self, color_dict:dict[str, tuple[int, int, int]]):
        self.config = SwatchesConfig(**SWATCH_SETTINGS)
        self.color_dict = color_dict
        self._set_font()
        self._set_line_height()
        self._set_total_lines()
        self._set_line_metrics()
        self._draw_swatches()

    async def send(self, interaction: discord.Interaction):
        files = [discord.File(buffer, filename=f'swaches_{index+1}.png')
                 for index, buffer in enumerate(self.buffers)]
        for file in files:
            await interaction.channel.send(file=file)

    def _set_font(self):
        font_path = self.config.font_path or None
        self.font = ImageFont.truetype(font_path, self.config.font_size)

    def _set_total_lines(self):
        color_names = list(self.color_dict.keys())
        line_width_count = 0
        line_count = 1

        for color_name in color_names:
            name_width = self.font.getlength(
                f"{color_name}{' ' * self.config.word_spacing}")
            line_width_count += name_width

            line_too_wide = (
                line_width_count 
                + self.config.padding[0]
                + self.config.padding[2]
                >= self.config.canvas_width)

            if line_too_wide:
                line_width_count = name_width
                line_count += 1

        self.total_lines = line_count

    def _set_line_height(self) -> int:
        ascent, descent = self.font.getmetrics()
        max_char_height = ascent + descent
        self.line_height = int(max_char_height)

    def _set_line_metrics(self):
        self.line_step = self.line_height * self.config.line_spacing
        usable_height = (self.config.canvas_height
                         - (self.config.padding[1] + self.config.padding[3]))
        self.lines_per_swatch = int(usable_height // self.line_step)

    def _create_canvas(self) -> Image.Image:
        img = Image.new(
                mode='RGBA',
                color=(0, 0, 0, 0),
                size=(self.config.canvas_width, self.config.canvas_height))
        draw = ImageDraw.Draw(img)
        return img, draw

    def _draw_swatches(self):
        img, draw = self._create_canvas()

        color_names = list(self.color_dict.keys())
        line_count = 1
        swatch_count = 1
        x = self.config.padding[0]
        y = self.config.padding[1]
        self.buffers = []
        for color_name in color_names:
            color_entry = f"{color_name},{' ' * self.config.word_spacing}"

            color_entry_width = self.font.getlength(color_entry)

            need_to_wrap = (
                    x + color_entry_width
                    >= (self.config.canvas_width + self.config.padding[2]))

            if need_to_wrap:
                line_count += 1
                y += self.line_step
                x = self.config.padding[0]

            reached_height_limit = line_count > self.lines_per_swatch

            if reached_height_limit:
                buffer = BytesIO()
                img.save(buffer, format='PNG')
                buffer.seek(0)
                self.buffers.append(buffer)
                img, draw = self._create_canvas()
                swatch_count += 1
                line_count = 1
                y = self.config.padding[1]

            draw.text(
                (x, y),
                text=color_entry,
                font=self.font,
                fill=self.color_dict[color_name])

            if color_name == color_names[-1]:
                buffer = BytesIO()
                img.save(buffer, format='PNG')
                buffer.seek(0)
                self.buffers.append(buffer)
                return

            x += color_entry_width
