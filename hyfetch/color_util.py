from __future__ import annotations

import colorsys
from dataclasses import dataclass, astuple
from .constants import GLOBAL_CFG
from .types import AnsiMode

MINECRAFT_COLORS = [

    # Minecraft formatting codes
    # ==========================
    "&0/\033[38;5;0m", "&1/\033[38;5;4m",  "&2/\033[38;5;2m",  "&3/\033[38;5;6m",
    "&4/\033[38;5;1m", "&5/\033[38;5;5m",  "&6/\033[38;5;3m",  "&7/\033[38;5;7m",
    "&8/\033[38;5;8m", "&9/\033[38;5;12m", "&a/\033[38;5;10m", "&b/\033[38;5;14m",
    "&c/\033[38;5;9m", "&d/\033[38;5;13m", "&e/\033[38;5;11m", "&f/\033[38;5;15m",
    "&l/\033[1m",   # Enable bold text
    "&o/\033[3m",   # Enable italic text
    "&n/\033[4m",   # Enable underlined text
    "&k/\033[8m",   # Enable hidden text
    "&m/\033[9m",   # Enable strikethrough text
    "&r/\033[0m",   # Reset everything

    # Extended codes (not officially in Minecraft)
    # ============================================
    "&-/\n",        # Line break
    "&~/\033[39m",  # Reset text color
    "&*/\033[49m",  # Reset background color
    "&L/\033[22m",  # Disable bold text
    "&O/\033[23m",  # Disable italic text
    "&N/\033[24m",  # Disable underlined text
    "&K/\033[28m",  # Disable hidden text
    "&M/\033[29m",  # Disable strikethrough text

]
MINECRAFT_COLORS = [(r[:2], r[3:]) for r in MINECRAFT_COLORS]


def color(msg: str) -> str:
    """
    Replace extended minecraft color codes in string
    :param msg: Message with minecraft color codes
    :return: Message with escape codes
    """
    for code, esc in MINECRAFT_COLORS:
        msg = msg.replace(code, esc)

    while '&gf(' in msg or '&gb(' in msg:
        i = msg.index('&gf(') if '&gf(' in msg else msg.index('&gb(')
        end = msg.index(')', i)
        code = msg[i + 4:end]
        fore = msg[i + 2] == 'f'

        if code.startswith('#'):
            rgb = tuple(int(code.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        else:
            code = code.replace(',', ' ').replace(';', ' ').replace('  ', ' ')
            rgb = tuple(int(c) for c in code.split(' '))

        msg = msg[:i] + RGB(*rgb).to_ansi(foreground=fore) + msg[end + 1:]

    return msg


def printc(msg: str):
    """
    Print with color
    :param msg: Message with minecraft color codes
    """
    print(color(msg + '&r'))


def clear_screen(title: str = ''):
    """
    Clear screen using ANSI escape codes
    """
    if not GLOBAL_CFG.debug:
        print('\033[2J\033[H', end='')

    if title:
        print()
        printc(title)
        print()


def redistribute_rgb(rgb: list[int]) -> tuple[int, int, int]:
    """
    Redistribute RGB after lightening

    Credit: https://stackoverflow.com/a/141943/7346633
    """
    threshold = 256
    rgb_max = max(rgb)
    if rgb_max < threshold:
        return tuple(int(c) for c in rgb)
    total = sum(rgb)
    if total > 3 * threshold:
        return 255, 255, 255
    x = (3 * threshold - total) / (3 * rgb_max - total)
    grey = threshold - x * rgb_max
    return tuple(grey + x * c for c in rgb)


def rgb_to_hls(rgb) -> list:
    return [*colorsys.rgb_to_hls(*[v / 255.0 for v in rgb])]


def hls_to_rgb(hls: list):
    return RGB(*[round(v * 255.0) for v in colorsys.hls_to_rgb(*hls)])


@dataclass(unsafe_hash=True)
class RGB:
    r: int
    g: int
    b: int

    def __iter__(self):
        return iter(astuple(self))

    @classmethod
    def from_hex(cls, hex_val: str) -> "RGB":
        """
        Create color from hex code

        >>> RGB.from_hex('#FFAAB7')
        RGB(r=255, g=170, b=183)

        :param hex_val: Hex color code
        :return: RGB object
        """
        hex_val = hex_val.lstrip("#")
        r = int(hex_val[0:2], 16)
        g = int(hex_val[2:4], 16)
        b = int(hex_val[4:6], 16)
        return cls(r, g, b)

    def to_ansi_rgb(self, foreground: bool = True) -> str:
        """
        Convert RGB to ANSI TrueColor (RGB) Escape Code.

        This uses the 24-bit color encoding (an uint8 for each color value), and supports 16 million
        colors. However, not all terminal emulators support this escape code. (For example, IntelliJ
        debug console doesn't support it).

        Currently, we do not know how to detect whether a terminal environment supports ANSI RGB. If
        you have any thoughts, feel free to submit an issue on our Github page!

        :param foreground: Whether the color is for foreground text or background color
        :return: ANSI RGB escape code like \033[38;2;255;100;0m
        """
        c = '38' if foreground else '48'
        return f'\033[{c};2;{self.r};{self.g};{self.b}m'

    def to_ansi_8bit(self, foreground: bool = True) -> str:
        """
        Convert RGB to ANSI 8bit 256 Color Escape Code.

        This encoding supports 256 colors in total.

        :return: ANSI 256 escape code like \033[38;5;206m'
        """
        r, g, b = self.r, self.g, self.b
        sep = 42.5

        while True:
            if r < sep or g < sep or b < sep:
                gray = r < sep and g < sep and b < sep
                break
            sep += 42.5

        if gray:
            rgb_color = 232 + (r + g + b) / 33
        else:
            rgb_color = 16 + int(r / 256. * 6) * 36 + \
                int(g / 256. * 6) * 6 + int(b / 256. * 6)

        code = '38' if foreground else '48'
        return f'\033[{code};5;{int(rgb_color)}m'

    def to_ansi_16(self, foreground: bool = True) -> str:
        """
        Convert RGB to ANSI 16 Color Escape Code

        :return: ANSI 16 escape code
        """
        raise NotImplementedError()

    def to_ansi(self, mode: AnsiMode | None = None, foreground: bool = True):
        if mode is None:
            mode = GLOBAL_CFG.color_mode
        if mode == 'rgb':
            return self.to_ansi_rgb(foreground)
        if mode == '8bit':
            return self.to_ansi_8bit(foreground)
        if mode == 'ansi':
            return self.to_ansi_16(foreground)

    def lighten(self, multiplier: float) -> 'RGB':
        """
        Lighten the color by a multiplier

        :param multiplier: Multiplier
        :return: Lightened color (original isn't modified)
        """
        return RGB(*redistribute_rgb([v * multiplier for v in self]))

    def set_light(self, light: float, at_least: bool | None = None,
                  at_most: bool | None = None) -> 'RGB':
        """
        Set HLS lightness value

        :param light: Lightness value (0-1)
        :param at_least: Set the lightness to at least this value (no change if greater)
        :param at_most: Set the lightness to at most this value (no change if lesser)
        :return: New color (original isn't modified)
        """
        # Convert to HLS
        hls = rgb_to_hls(self)

        # Modify light value
        if at_least is None and at_most is None:
            hls[1] = light
        else:
            if at_most:
                hls[1] = min(hls[1], light)
            if at_least:
                hls[1] = max(hls[1], light)

        # Convert back to RGB
        rgb = hls_to_rgb(hls)
        return rgb

    def is_light(self):
        return rgb_to_hls(self)[1] > 0.5

    def overlay(self, rgb_color: 'RGB', alpha: float) -> 'RGB':
        """
        Overlay a color on top of this color

        :param rgb_color: Overlay color
        :param alpha: Overlay alpha
        :return: New color (original isn't modified)
        """
        return RGB(*[round((1 - alpha) * v1 + alpha * v2) for v1, v2 in zip(self, rgb_color)])
