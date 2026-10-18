"""Module for testing utils.py"""

import json

from tree_scaper.utils import export_dict_to_json


# Testing the "export_dict_to_json" function.


def test_export_keeps_simple_lists_on_one_line(tmp_path):
    """Lists of simple values are written on a single line."""
    path = tmp_path / "simple.json"

    export_dict_to_json({"values": [1, 2, 3]}, path)

    assert '"values": [1, 2, 3]' in path.read_text(encoding="utf-8")


def test_export_pretty_prints_nested_lists_and_round_trips(tmp_path):
    """Lists of dictionaries are pretty-printed, and the file loads back to the same data."""
    path = tmp_path / "nested.json"
    data = {"branches": [{"title": "A", "values": [1, 2]}]}

    export_dict_to_json(data, path)

    text = path.read_text(encoding="utf-8")
    assert "\n" in text.strip()
    assert json.loads(text) == data


def test_export_overwrites_existing_file(tmp_path):
    """An existing file is replaced by the new export."""
    path = tmp_path / "existing.json"
    path.write_text("old content", encoding="utf-8")

    export_dict_to_json({"title": "new"}, path)

    text = path.read_text(encoding="utf-8")

    assert json.loads(text) == {"title": "new"}
