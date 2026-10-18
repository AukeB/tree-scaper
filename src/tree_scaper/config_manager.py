"""Module for loading the configuration files."""

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, confloat

from tree_scaper.constants import CONFIG_PATH


class ConfiguredBaseModel(BaseModel):
    """Base model with strict configuration validation enabled."""

    model_config = ConfigDict(extra="forbid")


class ConfigModel(ConfiguredBaseModel):
    """Root configuration model for the TreeVisualizer.

    Attributes:
        runtime (Runtime): Runtime behavior flags.
        window (Window): Window configuration.
        font (Font): Font configuration for node text.
        zoom (Zoom): Parameters related to zooming.
        node_size (NodeSize): Sizing and spacing configuration for tree nodes.
        root_node_position (RootNodePosition): Position of the root node.
        layout (Layout): Layout configuration for tree spacing.
        colors (Colors): Basic color definitions.
        color_palettes (ColorPalettes): Color palettes for the tree levels.
    """

    class Runtime(ConfiguredBaseModel):
        """Runtime behavior flags controlling visualization logic.

        Attributes:
            v_stack_level (Literal[0, 1]): How far vertical stacking of leaves applies.
            align_v_stack (bool): If ``v_stack_leafs`` is enabled, enforce equal widths
                for the entire vertical leaf stack (including the parent node).
            dark_mode (bool): Whether to display the tree visualization in dark mode.
        """

        v_stack_level: Literal[0, 1]
        align_v_stack: bool
        dark_mode: bool

    class Window(ConfiguredBaseModel):
        """Window configuration for the visualization canvas.

        Attributes:
            name (str): Window title.
            width (int): Window width in pixels.
            height (int): Window height in pixels.
            scroll_speed_horizontal (int): Pixels moved with a single horizontal scroll.
            scroll_speed_vertical (int): Pixels moved with a single vertical scroll.
        """

        name: str
        width: int
        height: int
        scroll_speed_horizontal: int
        scroll_speed_vertical: int

    class Font(ConfiguredBaseModel):
        """Font configuration for node text.

        Attributes:
            size (int): Font size at zoom level one.
            min_size (int): Smallest font size, regardless of zoom.
            name (str): Name of the font family.
        """

        size: int
        min_size: int
        name: str

    class Zoom(ConfiguredBaseModel):
        """Parameters related to zooming.

        Attributes:
            start_level (float): Zoom level when the window opens.
            min_level (float): Smallest allowed zoom level.
            max_level (float): Largest allowed zoom level.
            zoom_factor (float): Size change of one scroll step, as a multiplier.
        """

        start_level: float
        min_level: float
        max_level: float
        zoom_factor: float

    class NodeSize(ConfiguredBaseModel):
        """Sizing and spacing configuration for tree nodes.

        Attributes:
            border_thickness (int): Border width in pixels at zoom level one.
            margin_x (int): Horizontal padding in pixels at zoom level one.
            margin_y (int): Vertical padding in pixels at zoom level one.
        """

        border_thickness: int
        margin_x: int
        margin_y: int

    class RootNodePosition(ConfiguredBaseModel):
        """Defining root node position.

        Attributes:
            x (float): Horizontal position as a ratio of the window width.
            y (float): Vertical position as a ratio of the window height.
        """

        x: confloat(ge=0, le=1)  # type: ignore
        y: confloat(ge=0, le=1)  # type: ignore

    class Layout(ConfiguredBaseModel):
        """Layout configuration for tree spacing.

        Attributes:
            horizontal_spacing (int): Pixels between sibling subtrees at zoom level one.
            vertical_spacing (int): Pixels between a node and its branches at zoom level
                one.
        """

        horizontal_spacing: int
        vertical_spacing: int

    class Colors(ConfiguredBaseModel):
        """Basic color definitions used throughout the visualization.

        Attributes:
            white (list[int]): RGB color for white.
            gray (list[int]): RGB color for gray.
            black (list[int]): RGB color for black.
        """

        white: list[int]
        gray: list[int]
        black: list[int]

    class ColorPalettes(ConfiguredBaseModel):
        """Color palettes for the levels of the tree, per display mode.

        Attributes:
            light (LightPalettes): Palettes used in light mode.
            dark (DarkPalettes): Palettes used in dark mode.
        """

        class LightPalettes(ConfiguredBaseModel):
            """Palettes used in light mode.

            Each palette is a list of RGB colors, one for each level of the tree.

            Attributes:
                green (list[list[int]]): Green palette.
                red (list[list[int]]): Red palette.
                blue (list[list[int]]): Blue palette.
                purple (list[list[int]]): Purple palette.
                teal (list[list[int]]): Teal palette.
                orange (list[list[int]]): Orange palette.
                brown (list[list[int]]): Brown palette.
                slate (list[list[int]]): Slate palette.
            """

            green: list[list[int]]
            red: list[list[int]]
            blue: list[list[int]]
            purple: list[list[int]]
            teal: list[list[int]]
            orange: list[list[int]]
            brown: list[list[int]]
            slate: list[list[int]]

        class DarkPalettes(ConfiguredBaseModel):
            """Palettes used in dark mode.

            Each palette is a list of RGB colors, one for each level of the tree.

            Attributes:
                yellow (list[list[int]]): Yellow palette.
                amber (list[list[int]]): Amber palette.
                olive (list[list[int]]): Olive palette.
            """

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
    """Load and parse application configuration files.

    This class is responsible for reading a configuration file from disk and converting
    it into a strongly typed ConfigModel instance that can be used throughout the
    application.

    Attributes:
        config_path (Path): Path to the configuration YAML file.

    Example:
        >>> config_manager = ConfigManager()
        >>> config = config_manager.load_config_file()
    """

    def __init__(self, config_path: Path = CONFIG_PATH) -> None:
        """Initialize the ConfigManager with a configuration file path.

        Args:
            config_path (Path): Path to the configuration YAML file.
        """

        self.config_path = config_path

    def load_config_file(self) -> ConfigModel:
        """Load and validate the configuration file.

        This method reads the YAML configuration file from disk, parses its contents
        into a dictionary, and instantiates a ConfigModel from it. Validation is handled
        implicitly by the ConfigModel constructor.

        Returns:
            config_model (ConfigModel): Parsed and validated configuration object.
        """

        with open(self.config_path) as file:
            config = yaml.safe_load(file)

        config_model = ConfigModel(**config)

        return config_model
