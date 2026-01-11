"""Module for loading the configuration files."""

import yaml

from pathlib import Path
from pydantic import BaseModel, ConfigDict

from src.tree_scaper.constants import CONFIG_PATH


class ConfiguredBaseModel(BaseModel):
    """Base model with strict configuration validation enabled."""

    model_config = ConfigDict(extra="forbid")


class ConfigModel(ConfiguredBaseModel):
    """Root configuration model for the TreeVisualizer."""

    class Window(ConfiguredBaseModel):
        """Window configuration for the visualization canvas."""

        name: str
        width: int
        height: int
        background_color: list[int]  # [R, G, B]

    class Node(ConfiguredBaseModel):
        """Visual configuration for tree nodes."""

        class NodeSize(ConfiguredBaseModel):
            """Sizing and spacing configuration for a node."""

            width: int
            height: int
            border_thickness: int
            min_width: int
            padding_x: int
            padding_y: int

        class NodeColors(ConfiguredBaseModel):
            """Color configuration for node rendering."""

            levels: list[list[int]]
            background_color: list[int]

        class NodeFont(ConfiguredBaseModel):
            """Font configuration for node text."""

            name: str
            size: int

        size: NodeSize
        colors: NodeColors
        font: NodeFont

    class Layout(ConfiguredBaseModel):
        """Layout configuration for tree spacing."""

        horizontal_spacing: int
        vertical_spacing: int

    window: Window
    node: Node
    layout: Layout


class ConfigManager:
    """Load and parse application configuration files.

    This class is responsible for reading a configuration file from disk
    and converting it into a strongly typed ConfigModel instance that can
    be used throughout the application.
    """

    def __init__(self, config_path: Path = CONFIG_PATH):
        """Initialize the ConfigManager with a configuration file path.

        Args:
            config_path (Path): Path to the configuration YAML file.
        """
        self.config_path = config_path

    def load_config_file(self) -> ConfigModel:
        """Load and validate the configuration file.

        This method reads the YAML configuration file from disk, parses its
        contents into a dictionary, and instantiates a ConfigModel from it.
        Validation is handled implicitly by the ConfigModel constructor.

        Returns:
            ConfigModel: Parsed and validated configuration object.
        """
        with open(self.config_path) as file:
            config = yaml.safe_load(file)
        return ConfigModel(**config)
