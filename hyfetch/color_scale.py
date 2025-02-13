"""
This version of color_scale is a special version made without numpy dependency. The numpy version
would be faster, but numpy is 11 MB. In comparison, hyfetch 1.0.7 is only 105 kB, so it's not
a good idea to depend on numpy.
"""

from __future__ import annotations

from .color_util import RGB


def create_gradient_hex(colors: list[str], resolution: int = 300) -> list[RGB]:
    """
    Create gradient array from hex
    """
    colors = [RGB.from_hex(s) for s in colors]
    return create_gradient(colors, resolution)


def create_gradient(colors: list[RGB], resolution: int) -> list[RGB]:
    """
    Create gradient array

    Usage: arr[ratio / len(arr)] = Scaled gradient color at that point
    """
    result = []

    # Create gradient mapping
    for i in range(len(colors) - 1):
        color_1 = colors[i]
        color_2 = colors[i + 1]

        for point in range(resolution):
            ratio = point / resolution
            r = int(color_2.r * ratio + color_1.r * (1 - ratio))
            g = int(color_2.g * ratio + color_1.g * (1 - ratio))
            b = int(color_2.b * ratio + color_1.b * (1 - ratio))
            result.append(RGB(r, g, b))

    return result


def get_raw(gradient: list[RGB], ratio: float) -> RGB:
    """
    :param gradient: Gradient array (2d)
    :param ratio: Between 0-1
    :return: RGB subarray (1d, has 3 values)
    """
    if ratio == 1:
        return gradient[-1]

    i = int(ratio * len(gradient))
    return gradient[i]


class Scale:
    """
    A simple color scale using linear interpolation
    """
    colors: list[RGB]
    rgb: list[RGB]

    def __init__(self, scale: list[str], resolution: int = 300):
        self.resolution = resolution
        self.colors = [RGB.from_hex(s) for s in scale]
        self.rgb = create_gradient(self.colors, self.resolution)

    def __call__(self, ratio: float) -> RGB:
        """
        :param ratio: Between 0-1
        """
        return get_raw(self.rgb, ratio)

    def __len__(self):
        return self.resolution


def test_color_scale():
    """
    Display a gradient

    Returns
    -------
    None.

    """
    scale = Scale(['#232323', '#4F1879', '#B43A78', '#F98766', '#FCFAC0'])

    colors = 100
    for i in range(colors + 1):
        print(scale(i / colors).to_ansi_rgb(False), end=' ')
