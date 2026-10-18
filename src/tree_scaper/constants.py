"""Module for storing project constants."""

from pathlib import Path
from typing import NamedTuple

_PACKAGE_DIRECTORY = Path(__file__).parent

CONFIG_PATH = _PACKAGE_DIRECTORY / "configs" / "config.yaml"
DATA_PATH = _PACKAGE_DIRECTORY / "data" / "real_data.json"


class Position(NamedTuple):
    """Location on the screen, in pixels.

    Attributes:
        x (float): Horizontal coordinate, measured from the left edge.
        y (float): Vertical coordinate, measured from the top edge.
    """

    x: float
    y: float
