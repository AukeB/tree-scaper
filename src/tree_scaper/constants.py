"""Module for storing project constants."""

from pathlib import Path
from collections import namedtuple

Position = namedtuple("Position", "x y")

CONFIG_PATH = Path("src/tree_scaper/configs/config.yaml")
AUGMENTED_CONFIG_EXPORT_PATH = Path("src/tree_scaper/data/augmented_exported_data.json")
DATA_PATH = Path("src/tree_scaper/data/example_data.json")
