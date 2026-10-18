"""Module for general utility functions."""

import json
import re
from pathlib import Path


def _inline_list(match: re.Match[str]) -> str:
    """Joins the items of a matched JSON array onto one line.

    Args:
        match (re.Match[str]): Regex match of a JSON array that contains no nested
            brackets or braces.

    Returns:
        inline_list (str): The array written on one line, with its items separated by
            commas and a space.
    """

    items = match.group(1).split(",")
    stripped_items = [item.strip() for item in items]
    inline_list = "[" + ", ".join(stripped_items) + "]"

    return inline_list


def export_dict_to_json(data: dict, path: Path, indent: int = 2) -> None:
    """Export a dictionary to a JSON file. The function serializes the provided
    dictionary and writes it to disk using UTF-8 encoding. Existing files will be
    overwritten.

    Notes:
        - Lists containing only simple values (numbers, strings) are kept on one line.
        - Lists containing nested lists or dictionaries are pretty-printed across
          multiple lines for readability.

    Args:
        data (dict): Dictionary to serialize and export.
        path (Path): Destination file path ending in '.json'.
        indent (int): Number of spaces to use for pretty-printing.
    """

    json_str = json.dumps(data, indent=indent, ensure_ascii=False)
    json_str = re.sub(r"\[\s*([^\[\]\{\}]+?)\s*\]", _inline_list, json_str)

    with path.open("w", encoding="utf-8") as file:
        file.write(json_str)
