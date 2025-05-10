import json
import pytest

from speechdown.presentation.cli.commands.handlers import config


@pytest.fixture
def temp_speechdown_dir(tmp_path):
    """Create a temporary speechdown directory structure."""
    sd_dir = tmp_path / ".speechdown"
    sd_dir.mkdir()
    
    config_file = sd_dir / "config.json"
    config_data = {"languages": ["en", "uk", "ru"]}
    
    with open(config_file, "w") as f:
        json.dump(config_data, f)
    
    return tmp_path


def test_config_displays_current_configuration(temp_speechdown_dir, capsys):
    """Test that the config command displays the current configuration."""
    result = config(temp_speechdown_dir)
    
    assert result == 0
    
    captured = capsys.readouterr()
    assert "Current configuration:" in captured.out
    assert "Languages: en, uk, ru" in captured.out
    assert "Output directory: " in captured.out


def test_config_sets_output_directory(temp_speechdown_dir, capsys):
    """Test that the config command sets the output directory."""
    output_dir = "custom_transcripts"
    
    result = config(temp_speechdown_dir, output_dir)
    
    assert result == 0
    
    # Check output
    captured = capsys.readouterr()
    assert f"Output directory set to: {output_dir}" in captured.out
    
    # Check that the config file was updated
    config_file = temp_speechdown_dir / ".speechdown" / "config.json"
    with open(config_file, "r") as f:
        config_data = json.load(f)
    
    assert "output_dir" in config_data
    assert config_data["output_dir"] == output_dir


def test_config_handles_error(tmp_path, capsys):
    """Test that the config command handles errors gracefully."""
    non_existent_dir = tmp_path / "non_existent"
    
    # The directory doesn't exist, so this should fail
    result = config(non_existent_dir)
    
    assert result == 1