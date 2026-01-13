"""Module for general utility functions."""

import re
import json
from pathlib import Path


def export_dict_to_json(data: dict, path: Path, indent: int = 2) -> None:
    """
    Export a dictionary to a JSON file. The function serializes the provided
    dictionary and writes it to disk using UTF-8 encoding. Existing files will
    be overwritten.

    Notes:
        - Lists containing only simple values (numbers, strings) are kept on
          one line.
        - Lists containing nested lists or dictionaries are pretty-printed
          across multiple lines for readability.

    Args:
        data (dict): Dictionary to serialize and export.
        path (Path): Destination file path ending in '.json'.
        indent (int): Number of spaces to use for pretty-printing.
    """
    json_str = json.dumps(data, indent=indent, ensure_ascii=False)
    json_str = re.sub(
        r"\[\s*([^\[\]\{\}]+?)\s*\]",
        lambda m: "[" + ", ".join(s.strip() for s in m.group(1).split(",")) + "]",
        json_str,
    )

    with path.open("w", encoding="utf-8") as file:
        file.write(json_str)
