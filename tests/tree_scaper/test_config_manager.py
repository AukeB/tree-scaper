"""Module for testing config_manager.py"""

import pytest
import yaml
from pydantic import ValidationError

from tree_scaper.config_manager import ConfigManager, ConfigModel
from tree_scaper.constants import CONFIG_PATH


# Testing the "__init__" method from the "ConfigManager" class.


def test_init_defaults_to_packaged_config():
    """Without an argument, the packaged config file is used."""
    config_manager = ConfigManager()

    assert config_manager.config_path == CONFIG_PATH
    assert CONFIG_PATH.exists()


# Testing the "load_config_file" method from the "ConfigManager" class.


def test_load_config_file_returns_validated_model():
    """The packaged config is parsed into a ConfigModel."""
    config = ConfigManager().load_config_file()

    assert isinstance(config, ConfigModel)
    assert config.runtime.v_stack_level in (0, 1)


def test_load_config_file_rejects_unknown_keys(tmp_path):
    """A key that is not part of the model fails validation."""
    config_text = CONFIG_PATH.read_text(encoding="utf-8")
    config_data = yaml.safe_load(config_text)
    config_data["unexpected"] = True
    dumped_text = yaml.safe_dump(config_data)
    path = tmp_path / "config.yaml"
    path.write_text(dumped_text, encoding="utf-8")

    with pytest.raises(ValidationError):
        ConfigManager(path).load_config_file()
