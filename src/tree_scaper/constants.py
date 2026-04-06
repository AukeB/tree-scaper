"""Module for storing project constants."""

from collections import namedtuple
from pathlib import Path

Position = namedtuple("Position", "x y")

CONFIG_PATH = Path("src/tree_scaper/configs/config.yaml")
DATA_PATH = Path("src/tree_scaper/data/real_data.json")
