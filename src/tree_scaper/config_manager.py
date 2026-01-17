"""Module for loading the configuration files."""

import yaml

from pathlib import Path
from pydantic import BaseModel, confloat, ConfigDict

from src.tree_scaper.constants import CONFIG_PATH


class ConfiguredBaseModel(BaseModel):
    """Base model with strict configuration validation enabled."""

    model_config = ConfigDict(extra="forbid")


class ConfigModel(ConfiguredBaseModel):
    """Root configuration model for the TreeVisualizer."""

    class Runtime(ConfiguredBaseModel):
        """Runtime behavior flags controlling visualization logic."""

        v_stack_leafs: bool
        """Stack leaf-only child nodes vertically instead of horizontally."""

        align_v_stack: bool
        """
        If ``v_stack_leafs`` is enabled, enforce equal widths for the entire
        vertical leaf stack (including the parent node).
        """

        dark_mode: bool
        """Whether to display the tree visualization in dark mode."""

    class Window(ConfiguredBaseModel):
        """Window configuration for the visualization canvas."""

        name: str
        width: int
        height: int
        scroll_speed_horizontal: int
        scroll_speed_vertical: int

    class Font(ConfiguredBaseModel):
        """Font configuration for node text."""

        size: int
        min_size: int
        name: str

    class Zoom(ConfiguredBaseModel):
        """Parameters related to zooming."""

        start_level: float
        min_level: float
        max_level: float
        zoom_factor: float

    class NodeSize(ConfiguredBaseModel):
        """Sizing and spacing configuration for tree nodes."""

        border_thickness: int
        margin_x: int
        margin_y: int

    class RootNodePosition(ConfiguredBaseModel):
        """Defining root node position."""

        x: confloat(ge=0, le=1)  # type: ignore
        y: confloat(ge=0, le=1)  # type: ignore

    class Layout(ConfiguredBaseModel):
        """Layout configuration for tree spacing."""

        horizontal_spacing: int
        vertical_spacing: int

    class Colors(ConfiguredBaseModel):
        """Basic color definitions used throughout the visualization."""

        white: list[int]
        gray: list[int]
        black: list[int]

    class ColorPalettes(ConfiguredBaseModel):
        """ """

        class LightPalettes(ConfiguredBaseModel):
            """ """

            green: list[list[int]]
            red: list[list[int]]
            blue: list[list[int]]
            purple: list[list[int]]
            teal: list[list[int]]
            orange: list[list[int]]
            brown: list[list[int]]
            slate: list[list[int]]

        class DarkPalettes(ConfiguredBaseModel):
            """ """

            yellow: list[list[int]]
            amber: list[list[int]]
            olive: list[list[int]]

        light: LightPalettes
        dark: DarkPalettes

    runtime: Runtime
    window: Window
    font: Font
    zoom: Zoom
    node_size: NodeSize
    root_node_position: RootNodePosition
    layout: Layout
    colors: Colors
    color_palettes: ColorPalettes


class ConfigManager:
    """
    Load and parse application configuration files.

    This class is responsible for reading a configuration file from disk
    and converting it into a strongly typed ConfigModel instance that can
    be used throughout the application.
    """

    def __init__(self, config_path: Path = CONFIG_PATH):
        """
        Initialize the ConfigManager with a configuration file path.

        Args:
            config_path (Path): Path to the configuration YAML file.
        """
        self.config_path = config_path

    def load_config_file(self) -> ConfigModel:
        """
        Load and validate the configuration file.

        This method reads the YAML configuration file from disk, parses its
        contents into a dictionary, and instantiates a ConfigModel from it.
        Validation is handled implicitly by the ConfigModel constructor.

        Returns:
            ConfigModel: Parsed and validated configuration object.
        """
        with open(self.config_path) as file:
            config = yaml.safe_load(file)

        return ConfigModel(**config)
