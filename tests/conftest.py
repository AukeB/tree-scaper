"""Module conftest.py, reusable code for pytest."""

import os

import pygame as pg
import pytest
import yaml

from tree_scaper.config_manager import ConfigModel
from tree_scaper.constants import CONFIG_PATH
from tree_scaper.tree_visualizer import TreeVisualizer

# Run pygame without a real display so the tests work headless.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")


def _leaf(title):
    """Builds a leaf node of the tree data.

    Args:
        title (str): The title text of the node.
    """

    node = {"title": title, "subtitle": "sub", "branches": []}

    return node


@pytest.fixture(scope="function", name="config")
def fixture_config():
    """Loads the packaged config, with a smaller window so the tests stay fast."""
    config_text = CONFIG_PATH.read_text(encoding="utf-8")
    config_data = yaml.safe_load(config_text)
    config_data["window"]["width"] = 800
    config_data["window"]["height"] = 600

    config = ConfigModel.model_validate(config_data)

    return config


@pytest.fixture(scope="function", name="tree_data")
def fixture_tree_data():
    """Defines a tree with two levels of branches: a root, one inner node, and leaves."""
    inner = {"title": "Inner", "subtitle": "sub", "branches": [_leaf("A"), _leaf("B")]}
    tree = {"title": "Root", "subtitle": "sub", "branches": [inner, _leaf("C")]}

    return tree


@pytest.fixture(scope="function", name="visualizer")
def fixture_visualizer(config, tree_data, tmp_path):
    """Creates a TreeVisualizer that exports into a temporary folder, and closes pygame afterwards."""
    visualizer = TreeVisualizer(tree_data, config)
    visualizer.data_export_file_path = tmp_path / "export.json"

    yield visualizer

    pg.quit()
