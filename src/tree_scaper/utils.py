"""Module for general utility functions."""

import json
from pathlib import Path


def export_dict_to_json(data: dict, path: Path, indent: int = 2) -> None:
    """
    Export a dictionary to a JSON file.

    The function serializes the provided dictionary and writes it to disk
    using UTF-8 encoding. Existing files will be overwritten.

    Args:
        data (dict): Dictionary to serialize and export.
        path (Path): Destination file path ending in '.json'.
        indent (int): Number of spaces to use for pretty-printing.
    """
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=indent, ensure_ascii=False)
