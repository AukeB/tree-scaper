"""Module for testing tree_visualizer.py"""

import json

import pygame as pg
import pytest

from tree_scaper.constants import Position
from tree_scaper.tree_visualizer import TreeVisualizer


def _leaf(title):
    """Builds a leaf node of the tree data.

    Args:
        title (str): The title text of the node.
    """

    node = {"title": title, "subtitle": "sub", "branches": []}

    return node


def _node(title, branches):
    """Builds an inner node of the tree data.

    Args:
        title (str): The title text of the node.
        branches (list[dict]): The child nodes of the node.
    """

    node = {"title": title, "subtitle": "sub", "branches": branches}

    return node


def _pixels(surface):
    """Returns the raw RGB bytes of a surface, so two frames can be compared.

    Args:
        surface (pg.Surface): The surface to read.
    """

    raw = pg.image.tobytes(surface, "RGB")

    return raw


# Testing the "__init__" method from the "TreeVisualizer" class.


def test_init_reads_window_and_root_position(visualizer, config):
    """The window size and the root node position come from the config."""
    assert visualizer.window_width == 800
    assert visualizer.window_height == 600
    assert visualizer.root_node_position.x == config.root_node_position.x * 800
    assert visualizer.root_node_position.y == config.root_node_position.y * 600


def test_init_starts_at_config_zoom_without_scrolling(visualizer, config):
    """The zoom starts at the configured level and nothing is scrolled yet."""
    assert visualizer.zoom == config.zoom.start_level
    assert visualizer.scroll_x == 0
    assert visualizer.scroll_y == 0


def test_init_counts_the_depth_of_the_tree(visualizer):
    """The maximum depth is the number of levels below the root."""
    assert visualizer.max_depth == 2


def test_init_uses_dark_palette_in_dark_mode(visualizer, config):
    """In dark mode the dark palette is used for the tree levels."""
    assert visualizer.dark_mode is True
    assert visualizer.color_levels == config.color_palettes.dark.yellow


def test_init_uses_light_palette_in_light_mode(tree_data, config):
    """In light mode the light palette is used for the tree levels."""
    config.runtime.dark_mode = False

    visualizer = TreeVisualizer(tree_data, config)

    assert visualizer.color_levels == config.color_palettes.light.green
    assert visualizer.background_color == config.colors.white

    pg.quit()


# Testing the "_get_max_depth" method from the "TreeVisualizer" class.


def test_get_max_depth_of_leaf_is_zero(visualizer):
    """A node without branches has depth zero."""
    leaf = _leaf("A")

    assert visualizer._get_max_depth(leaf) == 0


def test_get_max_depth_follows_the_deepest_branch(visualizer):
    """The deepest branch decides the depth of the tree."""
    leaf_z = _leaf("Z")
    deepest = _node("Y", [leaf_z])
    middle = _node("X", [deepest])
    leaf = _leaf("Q")
    branches = [middle, leaf]
    tree = _node("Root", branches)

    assert visualizer._get_max_depth(tree) == 3


# Testing the "_set_colors" method from the "TreeVisualizer" class.


def test_set_colors_switches_between_light_and_dark(visualizer, config):
    """Changing the mode and recomputing the colors switches the palette."""
    visualizer.dark_mode = False

    visualizer._set_colors()

    assert visualizer.text_color == config.colors.black
    assert visualizer.color_levels == config.color_palettes.light.green


# Testing the "_zoomed" method from the "TreeVisualizer" class.


def test_zoomed_scales_a_pixel_value(visualizer):
    """A value is multiplied by the zoom level."""
    visualizer.zoom = 2.0

    assert visualizer._zoomed(5) == 10


def test_zoomed_never_goes_below_one_pixel(visualizer):
    """Very small values are rounded up to one pixel."""
    visualizer.zoom = 0.1

    assert visualizer._zoomed(5) == 1


# Testing the "_recompute_zoom_dependent_state" method from the "TreeVisualizer" class.


def test_recompute_scales_node_metrics_with_zoom(visualizer, config):
    """Margins, spacing, and border width follow the zoom level."""
    visualizer.zoom = 2.0

    visualizer._recompute_zoom_dependent_state()

    assert visualizer.node_margin_x == config.node_size.margin_x * 2
    assert visualizer.node_margin_y == config.node_size.margin_y * 2
    assert visualizer.horizontal_spacing == config.layout.horizontal_spacing * 2
    assert visualizer.vertical_spacing == config.layout.vertical_spacing * 2
    assert visualizer.border_thickness == config.node_size.border_thickness * 2


# Testing the "_init_pg_window" method from the "TreeVisualizer" class.


def test_init_pg_window_opens_window_of_configured_size(visualizer):
    """The window surface has the configured size."""
    screen = visualizer._init_pg_window()

    assert screen.get_size() == (800, 600)


# Testing the "_measure_node" method from the "TreeVisualizer" class.


def test_measure_node_adds_padding_to_text(visualizer):
    """The node height is the title and subtitle heights, each with vertical padding."""
    leaf = _leaf("Title")
    width, height, top_height, bottom_height = visualizer._measure_node(leaf)

    assert height == top_height + bottom_height
    assert top_height >= visualizer.node_margin_y * 2
    assert width >= visualizer.node_margin_x * 2


def test_measure_node_grows_with_more_title_lines(visualizer):
    """A title with more lines makes the node taller."""
    one_line_leaf = _leaf("Title")
    three_lines_leaf = _leaf("Title\nLine two\nLine three")
    one_line = visualizer._measure_node(one_line_leaf)
    three_lines = visualizer._measure_node(three_lines_leaf)

    assert three_lines[2] > one_line[2]


# Testing the "_measure_tree" method from the "TreeVisualizer" class.


def test_measure_tree_keeps_structure_and_adds_measurements(visualizer, tree_data):
    """Every node keeps its text and branches, and gets layout measurements."""
    measured = visualizer._measure_tree(tree_data)

    assert measured["title"] == "Root"
    assert len(measured["branches"]) == 2
    assert measured["branches"][0]["title"] == "Inner"

    assert {"width", "height", "subtree_width", "subtree_height"} <= set(
        measured["_measured"]
    )


def test_measure_tree_parent_is_at_least_as_wide_as_its_branches(visualizer, tree_data):
    """A subtree is wide enough to hold its whole branch subtree."""
    measured = visualizer._measure_tree(tree_data)

    branch_widths = [
        branch["_measured"]["subtree_width"] for branch in measured["branches"]
    ]

    assert measured["_measured"]["subtree_width"] >= max(branch_widths)


def test_measure_tree_stacks_leaves_when_level_one(visualizer, tree_data):
    """With level one, a node whose branches are all leaves stacks them vertically."""
    visualizer.v_stack_level = 1

    measured = visualizer._measure_tree(tree_data)

    inner = measured["branches"][0]["_measured"]
    assert inner["v_stack_applied"] == 1
    assert inner["suppress_connectors"] is True


def test_measure_tree_stacks_leaf_parents_when_level_two(visualizer):
    """With level two, a node whose branches are all leaf parents stacks them vertically."""
    visualizer.v_stack_level = 2
    leaf_a = _leaf("A")
    leaf_b = _leaf("B")
    parent_one = _node("P1", [leaf_a])
    parent_two = _node("P2", [leaf_b])
    tree = _node("Root", [parent_one, parent_two])

    measured = visualizer._measure_tree(tree)

    assert measured["_measured"]["v_stack_applied"] == 2
    assert measured["_measured"]["suppress_connectors"] is True


def test_measure_tree_does_not_stack_when_level_is_zero(visualizer, tree_data):
    """Without vertical stacking, no node is marked as stacked."""
    visualizer.v_stack_level = 0

    measured = visualizer._measure_tree(tree_data)

    assert measured["branches"][0]["_measured"]["v_stack_applied"] == 0


# Testing the "_apply_vstack_alignment" method from the "TreeVisualizer" class.


def test_apply_vstack_alignment_gives_stacked_nodes_equal_width(visualizer, tree_data):
    """A stacked parent and its leaves share the widest width."""
    visualizer.v_stack_level = 1
    visualizer.align_v_stack = True
    measured = visualizer._measure_tree(tree_data)

    visualizer._apply_vstack_alignment(measured)

    inner = measured["branches"][0]
    widths = {inner["_measured"]["width"]}
    widths.update(leaf["_measured"]["width"] for leaf in inner["branches"])
    assert len(widths) == 1


def test_apply_vstack_alignment_without_alignment_keeps_leaf_widths(
    visualizer, tree_data
):
    """With alignment turned off, the stacked leaves keep their own widths."""
    visualizer.v_stack_level = 1
    visualizer.align_v_stack = False
    measured = visualizer._measure_tree(tree_data)

    visualizer._apply_vstack_alignment(measured)

    inner = measured["branches"][0]
    assert inner["_measured"]["subtree_width"] >= inner["_measured"]["width"]


def test_apply_vstack_alignment_recomputes_unstacked_subtrees(visualizer, tree_data):
    """Subtree sizes of nodes that are not stacked cover their branches."""
    visualizer.v_stack_level = 0
    measured = visualizer._measure_tree(tree_data)

    visualizer._apply_vstack_alignment(measured)

    root = measured["_measured"]
    assert root["subtree_height"] >= root["height"] + visualizer.vertical_spacing
    assert root["subtree_width"] >= root["width"]


# Testing the "_assign_positions" method from the "TreeVisualizer" class.


def test_assign_positions_sets_the_root_position(visualizer, tree_data):
    """The root node gets exactly the position it is given."""
    measured = visualizer._measure_tree(tree_data)

    origin = Position(400, 300)

    visualizer._assign_positions(measured, origin)

    assert measured["_measured"]["position"] == (400, 300)


def test_assign_positions_places_branches_below_their_parent(visualizer, tree_data):
    """Without stacking, every branch sits lower on the screen than its parent."""
    visualizer.v_stack_level = 0
    measured = visualizer._measure_tree(tree_data)

    origin = Position(400, 300)

    visualizer._assign_positions(measured, origin)

    for branch in measured["branches"]:
        assert branch["_measured"]["position"][1] > 300


def test_assign_positions_stacks_leaves_under_parent(visualizer, tree_data):
    """With level one, stacked leaves share the parent's x position and go downwards."""
    visualizer.v_stack_level = 1
    measured = visualizer._measure_tree(tree_data)

    origin = Position(400, 300)

    visualizer._assign_positions(measured, origin)

    inner = measured["branches"][0]
    leaf_positions = [leaf["_measured"]["position"] for leaf in inner["branches"]]
    assert {x for x, _ in leaf_positions} == {inner["_measured"]["position"][0]}
    assert leaf_positions[0][1] < leaf_positions[1][1]


def test_assign_positions_stacks_leaf_parents_under_parent(visualizer):
    """With level two, stacked leaf parents share the root's x position and go downwards."""
    visualizer.v_stack_level = 2
    leaf_a = _leaf("A")
    leaf_b = _leaf("B")
    parent_one = _node("P1", [leaf_a])
    parent_two = _node("P2", [leaf_b])
    tree = _node("Root", [parent_one, parent_two])
    measured = visualizer._measure_tree(tree)

    origin = Position(400, 300)

    visualizer._assign_positions(measured, origin)

    parent_positions = [
        branch["_measured"]["position"] for branch in measured["branches"]
    ]

    assert {x for x, _ in parent_positions} == {400}
    assert parent_positions[0][1] < parent_positions[1][1]


# Testing the "_update_tree_layout" method from the "TreeVisualizer" class.


def test_update_tree_layout_aligns_when_enabled(visualizer, tree_data):
    """With stacking and alignment on, the stacked leaves get equal widths."""
    visualizer.v_stack_level = 1
    visualizer.align_v_stack = True

    visualizer._update_tree_layout()

    inner = visualizer.measured_tree["branches"][0]

    assert {leaf["_measured"]["width"] for leaf in inner["branches"]} == {
        inner["_measured"]["width"]
    }


def test_update_tree_layout_skips_alignment_when_disabled(visualizer, tree_data):
    """With alignment off, the layout is still computed but the widths are not forced equal."""
    visualizer.v_stack_level = 1
    visualizer.align_v_stack = False

    visualizer._update_tree_layout()

    assert visualizer.measured_tree["branches"][0]["_measured"]["position"] is not None


# Testing the "_set_zoom" method from the "TreeVisualizer" class.


def test_set_zoom_clamps_to_the_maximum(visualizer, config):
    """A zoom above the maximum is limited to the maximum."""
    visualizer._set_zoom(100.0)

    assert visualizer.zoom == config.zoom.max_level


def test_set_zoom_clamps_to_the_minimum(visualizer, config):
    """A zoom below the minimum is limited to the minimum."""
    visualizer._set_zoom(0.0)

    assert visualizer.zoom == config.zoom.min_level


def test_set_zoom_ignores_tiny_changes(visualizer):
    """A change smaller than the threshold keeps the fonts and layout as they are."""
    old_font = visualizer.font_top

    visualizer._set_zoom(visualizer.zoom + 1e-4)

    assert visualizer.font_top is old_font


def test_set_zoom_updates_fonts_and_layout(visualizer, config):
    """A real zoom change rescales the node metrics and recomputes the layout."""
    visualizer._set_zoom(2.0)

    assert visualizer.zoom == 2.0
    assert visualizer.node_margin_x == config.node_size.margin_x * 2
    assert visualizer.measured_tree["_measured"]["position"] is not None


# Testing the "_handle_events" method from the "TreeVisualizer" class.


def test_handle_events_quits_on_window_close(visualizer):
    """Closing the window exits the application."""
    event = pg.event.Event(pg.QUIT)
    pg.event.post(event)

    with pytest.raises(SystemExit):
        visualizer._handle_events()


def test_handle_events_zooms_with_control_and_wheel(visualizer, monkeypatch):
    """Scrolling the wheel while holding Control zooms by the zoom factor."""
    monkeypatch.setattr(pg.key, "get_mods", lambda: pg.KMOD_CTRL)
    before = visualizer.zoom
    event = pg.event.Event(pg.MOUSEWHEEL, x=0, y=1)
    pg.event.post(event)

    visualizer._handle_events()

    assert visualizer.zoom == pytest.approx(before * visualizer.zoom_factor)


def test_handle_events_scrolls_horizontally_with_shift_and_wheel(
    visualizer, monkeypatch
):
    """Scrolling the wheel while holding Shift scrolls horizontally."""
    monkeypatch.setattr(pg.key, "get_mods", lambda: pg.KMOD_SHIFT)
    event = pg.event.Event(pg.MOUSEWHEEL, x=0, y=2)
    pg.event.post(event)

    visualizer._handle_events()

    assert visualizer.scroll_x == 2 * visualizer.scroll_speed_horizontal
    assert visualizer.scroll_y == 0


def test_handle_events_scrolls_vertically_with_wheel(visualizer, monkeypatch):
    """Scrolling the wheel without a modifier scrolls vertically."""
    monkeypatch.setattr(pg.key, "get_mods", lambda: 0)
    event = pg.event.Event(pg.MOUSEWHEEL, x=0, y=-1)
    pg.event.post(event)

    visualizer._handle_events()

    assert visualizer.scroll_y == -visualizer.scroll_speed_vertical
    assert visualizer.scroll_x == 0


# Testing the "_draw_node" method from the "TreeVisualizer" class.


def test_draw_node_paints_the_node_color(visualizer, tree_data):
    """The node's top section and border use the given color."""
    measured = visualizer._measure_tree(tree_data)
    origin = Position(400, 300)
    visualizer._assign_positions(measured, origin)
    node = measured["branches"][1]
    node_color = [255, 0, 0]

    visualizer._draw_node(node, node_color)

    x, y = node["_measured"]["position"]
    left = x - node["_measured"]["width"] // 2
    top = y - node["_measured"]["height"] // 2
    inset = visualizer.border_thickness + 3

    pixel = visualizer.screen.get_at((left + inset, top + inset))

    assert tuple(pixel)[:3] == (255, 0, 0)


# Testing the "_draw_connectors" method from the "TreeVisualizer" class.


def test_draw_connectors_draws_lines_to_branches(visualizer, tree_data):
    """A node with branches gets connector lines drawn on the screen."""
    visualizer.v_stack_level = 0
    measured = visualizer._measure_tree(tree_data)
    origin = Position(400, 300)
    visualizer._assign_positions(measured, origin)
    before = _pixels(visualizer.screen)

    visualizer._draw_connectors(measured, [255, 0, 0])

    assert _pixels(visualizer.screen) != before


def test_draw_connectors_skips_leaves(visualizer, tree_data):
    """A leaf has no branches, so nothing is drawn."""
    measured = visualizer._measure_tree(tree_data)
    origin = Position(400, 300)
    visualizer._assign_positions(measured, origin)
    leaf = measured["branches"][1]
    before = _pixels(visualizer.screen)

    visualizer._draw_connectors(leaf, [255, 0, 0])

    assert _pixels(visualizer.screen) == before


def test_draw_connectors_skips_stacked_parents(visualizer, tree_data):
    """A stacked parent draws no connectors, because its leaves are stacked under it."""
    visualizer.v_stack_level = 1
    measured = visualizer._measure_tree(tree_data)
    origin = Position(400, 300)
    visualizer._assign_positions(measured, origin)
    inner = measured["branches"][0]
    before = _pixels(visualizer.screen)

    visualizer._draw_connectors(inner, [255, 0, 0])

    assert _pixels(visualizer.screen) == before


# Testing the "_draw_tree" method from the "TreeVisualizer" class.


def test_draw_tree_draws_every_node(visualizer, tree_data):
    """Drawing a measured tree changes the screen."""
    measured = visualizer._measure_tree(tree_data)
    origin = Position(400, 300)
    visualizer._assign_positions(measured, origin)
    before = _pixels(visualizer.screen)

    visualizer._draw_tree(measured)

    assert _pixels(visualizer.screen) != before


def test_draw_tree_reuses_last_palette_color_for_deep_levels(visualizer):
    """Levels deeper than the palette reuse its last color instead of failing."""
    depth = len(visualizer.color_levels) + 2
    tree = _leaf("Bottom")

    for index in range(depth):
        tree = _node(f"Level {index}", [tree])

    measured = visualizer._measure_tree(tree)
    origin = Position(400, 300)
    visualizer._assign_positions(measured, origin)
    before = _pixels(visualizer.screen)

    visualizer._draw_tree(measured)

    assert _pixels(visualizer.screen) != before


# Testing the "draw" method from the "TreeVisualizer" class.


def test_draw_exports_the_measured_tree_and_runs_until_quit(visualizer, monkeypatch):
    """Drawing exports the measured tree, renders a frame, then loops until quit."""
    frames = []

    def fake_handle_events():
        frames.append("frame")

        if len(frames) > 1:
            raise SystemExit

    monkeypatch.setattr(visualizer, "_handle_events", fake_handle_events)

    with pytest.raises(SystemExit):
        visualizer.draw()

    export_text = visualizer.data_export_file_path.read_text(encoding="utf-8")
    exported = json.loads(export_text)
    assert exported["title"] == "Root"
    assert len(frames) == 2
