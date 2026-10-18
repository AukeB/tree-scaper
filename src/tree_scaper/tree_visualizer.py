"""Module for visualizing tree structures using PyGame."""

import pygame as pg

from tree_scaper.config_manager import ConfigModel
from tree_scaper.constants import DATA_PATH, Position
from tree_scaper.utils import export_dict_to_json


class TreeVisualizer:
    """Visualizes hierarchical tree structures using PyGame.

    Attributes:
        config (ConfigModel): The configuration the visualizer was created with.
        tree (dict): The hierarchical data to visualize, before measuring.
        measured_tree (dict): The tree with layout measurements and positions.
        max_depth (int): Depth of the deepest node. The root node is at depth zero.
        v_stack_level (int): How far vertical stacking of leaves applies.
        align_v_stack (bool): Whether the vertical leaf stacks get equal widths.
        dark_mode (bool): Whether the tree is drawn in dark mode.
        window_name (str): Window title.
        window_width (int): Window width in pixels.
        window_height (int): Window height in pixels.
        scroll_speed_horizontal (int): Pixels moved with a single horizontal scroll.
        scroll_speed_vertical (int): Pixels moved with a single vertical scroll.
        scroll_x (int): Current horizontal scroll offset in pixels.
        scroll_y (int): Current vertical scroll offset in pixels.
        font_size (int): Font size at zoom level one.
        min_font_size (int): Smallest font size, regardless of zoom.
        font_name (str): Name of the font family.
        zoom (float): Current zoom level.
        min_zoom (float): Smallest allowed zoom level.
        max_zoom (float): Largest allowed zoom level.
        zoom_factor (float): Size change of one scroll step, as a multiplier.
        base_font_size (int): Font size used as the starting point for zooming.
        border_thickness (int): Border width of a node in pixels, at the current zoom.
        node_margin_x (int): Horizontal padding of a node in pixels, at the current
            zoom.
        node_margin_y (int): Vertical padding of a node in pixels, at the current zoom.
        root_node_position (Position): Center of the root node, in pixels.
        horizontal_spacing (int): Pixels between sibling subtrees, at the current zoom.
        vertical_spacing (int): Pixels between a node and its branches, at the current
            zoom.
        text_color (list[int]): RGB color of the subtitle text.
        background_color (list[int]): RGB color of the window and node bodies.
        leaf_background_color (list[int]): RGB color of the leaf nodes.
        color_levels (list[list[int]]): RGB colors for each level of the tree.
        data_export_file_path (Path): File the measured tree is exported to.
        font_top (pg.font.Font): Font of the title text.
        font_bottom (pg.font.Font): Font of the subtitle text.
        screen (pg.Surface): The window surface that the tree is drawn on.

    Example:
        >>> visualizer = TreeVisualizer(tree_data, config)
        >>> visualizer.draw()
    """

    def __init__(self, tree_data: dict, config: ConfigModel) -> None:
        """Initializes the TreeVisualizer with data and configuration.

        Args:
            tree_data (dict): The hierarchical data to visualize.
            config (ConfigModel): Pydantic config containing display, node, layout, and
                color properties.
        """

        # Refactor.
        # Maybe extract the parameters that are used a lot throughout the code
        # and the variables that are only used once, do not create class variables
        # for those but when used used them from the self.config variable.

        # Config
        self.config = config

        # Data
        self.tree = tree_data
        self.measured_tree: dict
        self.max_depth: int = self._get_max_depth(self.tree)

        # Runtime / behavior
        self.v_stack_level = self.config.runtime.v_stack_level
        self.align_v_stack = self.config.runtime.align_v_stack
        self.dark_mode = self.config.runtime.dark_mode

        # Window
        self.window_name = self.config.window.name
        self.window_width = self.config.window.width
        self.window_height = self.config.window.height
        self.scroll_speed_horizontal = self.config.window.scroll_speed_horizontal
        self.scroll_speed_vertical = self.config.window.scroll_speed_vertical
        self.scroll_x, self.scroll_y = 0, 0

        # Font
        self.font_size = self.config.font.size
        self.min_font_size = self.config.font.min_size
        self.font_name = self.config.font.name

        # Zoom
        self.zoom = self.config.zoom.start_level

        self.min_zoom, self.max_zoom = (
            self.config.zoom.min_level,
            self.config.zoom.max_level,
        )

        self.zoom_factor = self.config.zoom.zoom_factor
        self.base_font_size = self.font_size

        # Node
        self.border_thickness = self.config.node_size.border_thickness
        self.node_margin_x = self.config.node_size.margin_x
        self.node_margin_y = self.config.node_size.margin_y

        # Root node position
        self.root_node_position = Position(
            x=self.config.root_node_position.x * self.window_width,
            y=self.config.root_node_position.y * self.window_height,
        )

        # Layout
        self.horizontal_spacing = self.config.layout.horizontal_spacing
        self.vertical_spacing = self.config.layout.vertical_spacing

        # Colors
        self.text_color: list[int]
        self.background_color: list[int]
        self.leaf_background_color: list[int]
        self.color_levels: list[list[int]]
        self._set_colors()

        # File export
        self.data_export_file_path = DATA_PATH.with_name(
            DATA_PATH.stem + "_export" + DATA_PATH.suffix
        )

        # Initialize PyGame
        pg.init()

        # Create and set fonts.
        self.font_top: pg.font.Font
        self.font_bottom: pg.font.Font
        self._recompute_zoom_dependent_state()

        # Initialize window
        self.screen = self._init_pg_window()

    def _get_max_depth(self, node: dict, level: int = 0) -> int:
        """Recursively compute the maximum depth of a tree.

        The root node is considered level 0. Each recursive descent into a child branch
        increases the level by 1.

        Args:
            node (dict): Current node in the tree.
            level (int): Current depth level.

        Returns:
            max_depth (int): Maximum depth found in this subtree.
        """

        branches = node.get("branches", [])

        if not branches:
            return level

        child_depths = [self._get_max_depth(child, level + 1) for child in branches]
        max_depth = max(child_depths)

        return max_depth

    def _set_colors(self) -> None:
        """Chooses the text, background, and level colors for the current mode."""

        if not self.dark_mode:
            self.text_color = self.config.colors.black
            self.background_color = self.config.colors.white
            self.leaf_background_color = self.config.colors.gray
            self.color_levels = self.config.color_palettes.light.green
        else:
            self.text_color = self.config.colors.white
            self.background_color = self.config.colors.black
            self.leaf_background_color = self.config.colors.gray
            self.color_levels = self.config.color_palettes.dark.yellow

    def _zoomed(self, value: int) -> int:
        """Scales a pixel value by the current zoom level.

        Args:
            value (int): Pixel value at zoom level one.

        Returns:
            zoomed_value (int): The scaled value, never smaller than one pixel.
        """

        scaled_value = int(value * self.zoom)
        zoomed_value = max(1, scaled_value)

        return zoomed_value

    def _recompute_zoom_dependent_state(self) -> None:
        """Update zoom-dependent parameters like fonts and node metrics."""

        scaled_font_size = int(self.base_font_size * self.zoom)
        scaled_size = max(self.min_font_size, scaled_font_size)
        self.font_top = pg.font.SysFont(self.font_name, scaled_size)
        self.font_bottom = pg.font.SysFont(self.font_name, scaled_size)

        self.node_margin_x = self._zoomed(self.config.node_size.margin_x)
        self.node_margin_y = self._zoomed(self.config.node_size.margin_y)
        self.horizontal_spacing = self._zoomed(self.config.layout.horizontal_spacing)
        self.vertical_spacing = self._zoomed(self.config.layout.vertical_spacing)
        self.border_thickness = self._zoomed(self.config.node_size.border_thickness)

    def _init_pg_window(self) -> pg.Surface:
        """Initializes the PyGame display window.

        Returns:
            screen (pg.Surface): The pygame screen surface.
        """

        pg.display.set_caption(self.window_name)
        screen = pg.display.set_mode((self.window_width, self.window_height))

        return screen

    def _measure_node(self, node_data: dict) -> tuple[int, int, int, int]:
        """Compute the pixel size required to render a single node.

        This method measures how much space a node needs based on its textual content
        and layout configuration. The process is as follows:

        1. Split the node's title and subtitle into separate text lines.
        2. Render each line using the configured pygame fonts.
        3. Measure the width of every rendered text surface.
        4. Determine the node width as the maximum text width plus horizontal padding,
           while enforcing a minimum node width.
        5. Compute the height of the title and subtitle sections separately by summing
           their text heights and adding vertical padding.
        6. Combine the title and subtitle heights into the final node height.

        Args:
            node_data (dict): A node dictionary containing 'title' and 'subtitle' text
                fields.

        Returns:
            measurements (tuple[int, int, int, int]): The node width, node height, title
                section height, and subtitle section height, in pixels.
        """

        title_lines = node_data["title"].split("\n")
        subtitle_lines = node_data["subtitle"].split("\n")
        dummy_color_value = (0, 0, 0)

        top_surfs = [
            self.font_top.render(line, True, dummy_color_value) for line in title_lines
        ]

        bottom_surfs = [
            self.font_bottom.render(line, True, dummy_color_value)
            for line in subtitle_lines
        ]

        text_widths = [surf.get_width() for surf in top_surfs + bottom_surfs]
        width = max(text_widths) + self.node_margin_x * 2

        top_text_heights = [surf.get_height() for surf in top_surfs]
        top_height = sum(top_text_heights) + self.node_margin_y * 2

        bottom_text_heights = [surf.get_height() for surf in bottom_surfs]
        bottom_height = sum(bottom_text_heights) + self.node_margin_y * 2

        height = top_height + bottom_height

        measurements = (width, height, top_height, bottom_height)

        return measurements

    def _measure_tree(self, node_data: dict) -> dict:
        """Recursively measure a tree and compute layout metadata.

        This method traverses the tree structure depth-first and constructs a new tree
        containing layout measurements for every node. The process is as follows:

        1. Measure the visual size of the current node using measure_node.
        2. Recursively call _measure_tree on each branch (child node).
        3. If the node has branches: - Sum the subtree widths of all branches. - Add
           horizontal spacing between sibling subtrees. - Compute the subtree height as
           the node height plus vertical spacing and the maximum child subtree height.
        4. If the node has no branches, its subtree size equals its own size.
        5. Create a new node dictionary that: - Copies the original node data. -
           Replaces 'branches' with the measured branch nodes. - Attaches a '_measured'
           dictionary containing size and layout metadata used for positioning and
           rendering.

        Args:
            node_data (dict): A node dictionary that may contain a 'branches' list of
                child nodes.

        Returns:
            measured_node (dict): A new tree structure augmented with '_measured' layout
                data for each node.
        """

        node_width, node_height, top_height, bottom_height = self._measure_node(
            node_data
        )

        branches = node_data.get("branches", [])

        measured_branches = [
            self._measure_tree(branch_node) for branch_node in branches
        ]

        # Determine whether this node has only leaf children
        if measured_branches:
            child_branch_lists = [child.get("branches") for child in measured_branches]
            leaves_only = not any(child_branch_lists)
        else:
            leaves_only = False

        child_leaves_flags = [
            child["_measured"].get("leaves_only", False) for child in measured_branches
        ]

        children_are_leaf_parents = bool(measured_branches) and all(child_leaves_flags)

        v_stack_applied = 0

        if self.v_stack_level >= 2 and children_are_leaf_parents:
            v_stack_applied = 2
        elif self.v_stack_level >= 1 and leaves_only:
            v_stack_applied = 1

        if measured_branches and v_stack_applied == 0:
            subtree_widths = [
                branch_node["_measured"]["subtree_width"]
                for branch_node in measured_branches
            ]

            total_width = sum(subtree_widths)

            total_width += self.horizontal_spacing * (len(measured_branches) - 1)
            total_width = max(total_width, node_width)

            subtree_heights = [
                branch_node["_measured"]["subtree_height"]
                for branch_node in measured_branches
            ]

            tallest_subtree = max(subtree_heights)
            total_height = node_height + self.vertical_spacing + tallest_subtree

        elif measured_branches and v_stack_applied == 1:
            child_widths = [child["_measured"]["width"] for child in measured_branches]
            max_child_width = max(child_widths)
            total_width = max(node_width, max_child_width)

            child_heights = [
                child["_measured"]["height"] for child in measured_branches
            ]

            children_height = sum(child_heights) + self.vertical_spacing * (
                len(measured_branches) - 1
            )

            total_height = node_height + self.vertical_spacing + children_height

        elif measured_branches and v_stack_applied == 2:
            child_subtree_widths = [
                branch["_measured"]["subtree_width"] for branch in measured_branches
            ]

            widest_subtree = max(child_subtree_widths)
            total_width = max(node_width, widest_subtree)

            child_subtree_heights = [
                branch["_measured"]["subtree_height"] for branch in measured_branches
            ]

            children_total_height = sum(
                child_subtree_heights
            ) + self.vertical_spacing * (len(measured_branches) - 1)

            total_height = node_height + self.vertical_spacing + children_total_height

        else:
            total_width = node_width
            total_height = node_height

        measured_node = {
            "title": node_data["title"],
            "subtitle": node_data["subtitle"],
            "_measured": {
                "width": node_width,
                "height": node_height,
                "top_height": top_height,
                "bottom_height": bottom_height,
                "subtree_width": total_width,
                "subtree_height": total_height,
                "position": None,
                "leaves_only": leaves_only,
                "v_stack_applied": v_stack_applied,
                "suppress_connectors": (v_stack_applied in (1, 2)),
            },
            "branches": measured_branches,
        }

        return measured_node

    def _apply_vstack_alignment(self, measured_tree: dict) -> None:
        """Post-process measured tree to align widths for vertical leaf stacks.

        This walks the measured tree bottom-up. For nodes marked as
        '_measured.leaves_only', it makes the parent and all direct leaf children share
        the same width (the maximum of their current widths). It also recomputes
        subtree_width and subtree_height for each node so ancestor measurements remain
        correct.

        This method mutates the measured_tree in-place.

        Args:
            measured_tree (dict): A tree produced by _measure_tree, which is updated in
                place.
        """

        for child in measured_tree.get("branches", []):
            self._apply_vstack_alignment(child)

        branches = measured_tree.get("branches", [])

        if not branches:
            measured_tree["_measured"]["subtree_width"] = measured_tree["_measured"][
                "width"
            ]

            measured_tree["_measured"]["subtree_height"] = measured_tree["_measured"][
                "height"
            ]

            return

        if measured_tree["_measured"]["leaves_only"] and self.align_v_stack:
            child_widths = [child["_measured"]["width"] for child in branches]
            max_child_width = max(child_widths)
            target_width = max(measured_tree["_measured"]["width"], max_child_width)

            measured_tree["_measured"]["width"] = target_width

            for child in branches:
                child["_measured"]["width"] = target_width
                child["_measured"]["subtree_width"] = target_width
                child["_measured"]["subtree_height"] = child["_measured"]["height"]

            child_heights = [child["_measured"]["height"] for child in branches]

            children_height = sum(child_heights) + self.vertical_spacing * (
                len(branches) - 1
            )

            measured_tree["_measured"]["subtree_width"] = target_width

            measured_tree["_measured"]["subtree_height"] = (
                measured_tree["_measured"]["height"]
                + self.vertical_spacing
                + children_height
            )

        else:
            child_subtree_widths = [
                child["_measured"]["subtree_width"] for child in branches
            ]
            total_width = sum(child_subtree_widths) + self.horizontal_spacing * (
                len(branches) - 1
            )
            measured_tree["_measured"]["subtree_width"] = max(
                measured_tree["_measured"]["width"], total_width
            )

            child_subtree_heights = [
                child["_measured"]["subtree_height"] for child in branches
            ]
            tallest_subtree = max(child_subtree_heights)
            measured_tree["_measured"]["subtree_height"] = (
                measured_tree["_measured"]["height"]
                + self.vertical_spacing
                + tallest_subtree
            )

    def _assign_positions(self, measured_tree: dict, position: Position) -> None:
        """Assign screen positions to all nodes in a measured tree.

        This method performs a second recursive traversal over the tree after all size
        measurements have been completed. It relies on the fact that every node already
        contains accurate width and height information in its '_measured' metadata.

        The separation of measurement and positioning is essential, because node
        positions depend on the total subtree sizes of sibling nodes, which can only be
        known after measuring the entire tree.

        The positioning process works as follows:

        1. Assign the given (x, y) position to the current node.
        2. Compute the total horizontal width occupied by all branch subtrees, including
           horizontal spacing between siblings.
        3. Determine the starting x-coordinate so the branches are centered below the
           parent node.
        4. For each branch: - Compute the branch node's x-position using its subtree
           width. - Compute the branch node's y-position using the parent's height,
           vertical spacing, and the branch node's own height. - Recursively assign
           positions to the branch subtree.
        5. Continue recursively until all leaf nodes have positions.

        Args:
            measured_tree (dict): A tree produced by _measure_tree containing
                '_measured' layout data for every node.
            position (Position): The (x, y) position of the current node's center in
                screen coordinates.
        """

        measured_tree["_measured"]["position"] = (position.x, position.y)
        branches = measured_tree.get("branches", [])
        vstack_mode = measured_tree["_measured"].get("v_stack_applied", 0)

        if not branches:
            return

        if vstack_mode == 0:
            subtree_widths = [
                branch_node["_measured"]["subtree_width"] for branch_node in branches
            ]

            total_width = sum(subtree_widths) + self.horizontal_spacing * (
                len(branches) - 1
            )

            x_start = position.x - total_width // 2
            current_x = x_start

            for branch_node in branches:
                branch_node_w = branch_node["_measured"]["subtree_width"]
                branch_node_x = current_x + branch_node_w // 2

                branch_node_y = (
                    position.y
                    + measured_tree["_measured"]["height"] // 2
                    + self.vertical_spacing
                    + branch_node["_measured"]["height"] // 2
                )

                branch_position = Position(branch_node_x, branch_node_y)
                self._assign_positions(branch_node, branch_position)
                current_x += branch_node_w + self.horizontal_spacing

        elif vstack_mode == 1:
            x_parent, y_parent = measured_tree["_measured"]["position"]
            parent_height = measured_tree["_measured"]["height"]
            parent_bottom = y_parent + parent_height // 2

            y_cursor = parent_bottom + self.vertical_spacing

            for child in branches:
                child_height = child["_measured"]["height"]
                child_center_y = y_cursor + child_height // 2
                child_center_x = x_parent

                child_position = Position(child_center_x, child_center_y)
                self._assign_positions(child, child_position)

                y_cursor = child_center_y + child_height // 2 + self.vertical_spacing

        else:
            x_parent, y_parent = measured_tree["_measured"]["position"]
            parent_height = measured_tree["_measured"]["height"]
            parent_bottom = y_parent + parent_height // 2

            y_cursor = parent_bottom + self.vertical_spacing

            for child in branches:
                child_subtree_h = child["_measured"]["subtree_height"]
                child_center_y = y_cursor + child_subtree_h // 2
                child_center_x = x_parent

                child_position = Position(child_center_x, child_center_y)
                self._assign_positions(child, child_position)
                y_cursor += child_subtree_h + self.vertical_spacing

    def _update_tree_layout(self) -> None:
        """Measure, align, and assign positions for the current tree."""

        self.measured_tree = self._measure_tree(self.tree)

        if self.v_stack_level > 0 and self.align_v_stack:
            self._apply_vstack_alignment(self.measured_tree)

        self._assign_positions(self.measured_tree, self.root_node_position)

    def _set_zoom(self, new_zoom: float) -> None:
        """Clamp zoom, update fonts, and update tree layout.

        Args:
            new_zoom (float): The requested zoom level, before it is clamped to the
                allowed range.
        """

        upper_bounded_zoom = min(self.max_zoom, new_zoom)
        clamped_zoom = max(self.min_zoom, upper_bounded_zoom)

        if abs(clamped_zoom - self.zoom) < 1e-3:
            return

        self.zoom = clamped_zoom
        self._recompute_zoom_dependent_state()
        self._update_tree_layout()

    def _handle_events(self) -> None:
        """Handles pygame events, including quitting the application."""

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                raise SystemExit
            elif event.type == pg.MOUSEWHEEL:
                mods = pg.key.get_mods()

                # Zooming in and out.
                if mods & pg.KMOD_CTRL:
                    factor = self.zoom_factor**event.y
                    self._set_zoom(self.zoom * factor)

                # Horizontal scrolling.
                elif mods & pg.KMOD_SHIFT:
                    self.scroll_x += event.y * self.scroll_speed_horizontal

                # Vertical scrolling.
                else:
                    self.scroll_y += event.y * self.scroll_speed_vertical

    def _draw_node(self, node_data: dict, node_color: list[int]) -> None:
        """Render a single node using its precomputed layout data.

        This method draws a node rectangle split into a top and bottom section, along
        with a border and text content. All positional and dimensional information is
        read from the node's '_measured' data, which must already be populated by the
        measurement and positioning phases.

        The drawing process follows these steps:

        1. Read the node's center position, width, and height.
        2. Construct a main rectangle centered at the given position.
        3. Split the rectangle vertically into top and bottom sections.
        4. Fill each section with its respective background color.
        5. Draw a border around the full node rectangle.
        6. Render and blit the title text into the top section.
        7. Render and blit the subtitle text into the bottom section.

        This method does not perform any layout calculations and assumes that all
        geometry has been finalized beforehand.

        Args:
            node_data (dict): A measured node containing '_measured' layout data and
                text fields to render.
            node_color (list[int]): RGB color of the node's top section and border.
        """

        x, y = node_data["_measured"]["position"]
        x += self.scroll_x
        y += self.scroll_y

        width = node_data["_measured"]["width"]
        height = node_data["_measured"]["height"]

        rect = pg.Rect(x - width // 2, y - height // 2, width, height)
        top_height = node_data["_measured"]["top_height"]
        bottom_height = node_data["_measured"]["bottom_height"]
        top_rect = pg.Rect(rect.left, rect.top, width, top_height)
        bottom_rect = pg.Rect(rect.left, rect.top + top_height, width, bottom_height)

        pg.draw.rect(self.screen, node_color, top_rect)
        pg.draw.rect(self.screen, self.background_color, bottom_rect)
        pg.draw.rect(self.screen, node_color, rect, self.border_thickness)

        title_lines = node_data["title"].split("\n")
        subtitle_lines = node_data["subtitle"].split("\n")

        top_surfs = [
            self.font_top.render(line, True, self.background_color)
            for line in title_lines
        ]

        bottom_surfs = [
            self.font_bottom.render(line, True, self.text_color)
            for line in subtitle_lines
        ]

        current_y = top_rect.top + self.node_margin_y

        for surf in top_surfs:
            surf_height = surf.get_height()
            text_rect = surf.get_rect(center=(x, current_y + surf_height // 2))
            self.screen.blit(surf, text_rect)
            current_y += surf_height

        current_y = bottom_rect.top + self.node_margin_y

        for surf in bottom_surfs:
            surf_height = surf.get_height()
            text_rect = surf.get_rect(center=(x, current_y + surf_height // 2))
            self.screen.blit(surf, text_rect)
            current_y += surf_height

    def _draw_connectors(self, measured_tree: dict, node_color: list[int]) -> None:
        """Draw orthogonal connector lines between a node and its branches.

        This method renders tree connectors using only horizontal and vertical line
        segments. For a node with one or more branches, the connectors are drawn in
        three steps:

        1. A vertical line extending downward from the bottom center of the parent node.
        2. A horizontal junction line spanning across all branch x-positions.
        3. Individual vertical lines connecting the junction to each branch node's top
           center.

        This layout ensures visually clean 90-degree connections and clearly
        communicates hierarchical relationships without diagonal lines.

        The method assumes that all branch nodes have already been measured and assigned
        absolute positions. It performs no layout calculations and relies entirely on
        '_measured' metadata.

        Args:
            measured_tree (dict): A measured tree node containing position and dimension
                data for the parent and all direct branches.
            node_color (list[int]): RGB color of the connector lines.
        """

        branches = measured_tree.get("branches", [])

        if not branches:
            return

        if measured_tree["_measured"].get("suppress_connectors"):
            return

        height = measured_tree["_measured"]["height"]
        x, y = measured_tree["_measured"]["position"]
        x += self.scroll_x
        y += self.scroll_y

        parent_x = x
        parent_y = y + height // 2

        child_points = []

        for branch in branches:
            bx, by = branch["_measured"]["position"]
            bh = branch["_measured"]["height"]
            child_points.append((bx + self.scroll_x, by + self.scroll_y - bh // 2))

        junction_y = parent_y + self.vertical_spacing // 2

        pg.draw.line(
            self.screen,
            node_color,
            (parent_x, parent_y),
            (parent_x, junction_y),
            self.border_thickness,
        )

        min_x = min(x for x, _ in child_points)
        max_x = max(x for x, _ in child_points)

        pg.draw.line(
            self.screen,
            node_color,
            (min_x, junction_y),
            (max_x, junction_y),
            self.border_thickness,
        )

        for cx, cy in child_points:
            pg.draw.line(
                self.screen,
                node_color,
                (cx, junction_y),
                (cx, cy),
                self.border_thickness,
            )

    def _draw_tree(self, measured_tree: dict, level: int = 0) -> None:
        """Recursively draw all nodes and connectors in a measured tree.

        This method performs a depth-first traversal of a fully measured and positioned
        tree structure. For each node, it renders both the visual node representation
        and the orthogonal connector lines to its branches.

        The drawing order is:

        1. Draw the current node rectangle and text.
        2. Draw connector lines from the node to its direct branches.
        3. Recursively draw each branch subtree.

        This method assumes that all nodes already have their final width, height,
        subtree dimensions, and absolute screen positions assigned. It contains no
        layout or measurement logic and relies entirely on the '_measured' metadata.

        Args:
            measured_tree (dict): A measured tree structure containing layout and
                position metadata for every node.
            level (int): Depth level in the tree (0=root).
        """

        if level == self.max_depth:
            node_color = self.leaf_background_color
        else:
            last_color_index = len(self.color_levels) - 1
            color_idx = min(level, last_color_index)
            node_color = self.color_levels[color_idx]

        self._draw_node(measured_tree, node_color)
        self._draw_connectors(measured_tree, node_color)

        branches = measured_tree.get("branches", [])

        for branch_node in branches:
            self._draw_tree(branch_node, level=level + 1)

    def draw(self) -> None:
        """Run the complete visualization pipeline and render loop.

        This method orchestrates the full rendering process from raw input data to on-
        screen visualization. It performs the following steps:

        1. Measure the entire tree to determine node and subtree sizes.
        2. Assign screen positions to all nodes based on measured sizes.
        3. Enter the main render loop: - Handle window and quit events. - Clear the
           screen using the background color. - Draw the entire tree using precomputed
           layout data. - Update the display.

        The measurement and positioning phases are executed once, while drawing is
        repeated every frame.
        """

        self._update_tree_layout()
        export_dict_to_json(data=self.measured_tree, path=self.data_export_file_path)

        while True:
            self._handle_events()
            self.screen.fill(self.background_color)
            self._draw_tree(self.measured_tree)
            pg.display.flip()
