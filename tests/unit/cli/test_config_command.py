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


def test_config_sets_languages(temp_speechdown_dir, capsys):
    """Test that the config command sets languages from a comma-separated list."""
    languages = "en,fr,de"
    
    result = config(temp_speechdown_dir, languages=languages)
    
    assert result == 0
    
    # Check output
    captured = capsys.readouterr()
    assert "Languages updated: en, fr, de" in captured.out
    
    # Check that the config file was updated
    config_file = temp_speechdown_dir / ".speechdown" / "config.json"
    with open(config_file, "r") as f:
        config_data = json.load(f)
    
    assert "languages" in config_data
    assert config_data["languages"] == ["en", "fr", "de"]


def test_config_adds_language(temp_speechdown_dir, capsys):
    """Test adding a single language to the configuration."""
    add_language = "fr"
    
    result = config(temp_speechdown_dir, add_language=add_language)
    
    assert result == 0
    
    # Check output
    captured = capsys.readouterr()
    assert f"Added language: {add_language}" in captured.out
    
    # Check that the config file was updated
    config_file = temp_speechdown_dir / ".speechdown" / "config.json"
    with open(config_file, "r") as f:
        config_data = json.load(f)
    
    assert "languages" in config_data
    assert "fr" in config_data["languages"]
    assert "en" in config_data["languages"]  # Original languages should still be there
    assert "uk" in config_data["languages"]
    assert "ru" in config_data["languages"]


def test_config_removes_language(temp_speechdown_dir, capsys):
    """Test removing a language from the configuration."""
    remove_language = "uk"
    
    result = config(temp_speechdown_dir, remove_language=remove_language)
    
    assert result == 0
    
    # Check output
    captured = capsys.readouterr()
    assert f"Removed language: {remove_language}" in captured.out
    
    # Check that the config file was updated
    config_file = temp_speechdown_dir / ".speechdown" / "config.json"
    with open(config_file, "r") as f:
        config_data = json.load(f)
    
    assert "languages" in config_data
    assert "uk" not in config_data["languages"]
    assert "en" in config_data["languages"]  # Other languages should still be there
    assert "ru" in config_data["languages"]


def test_config_handles_invalid_language(temp_speechdown_dir, capsys):
    """Test that the config command handles invalid language codes properly."""
    languages = "en,invalid,fr"
    
    result = config(temp_speechdown_dir, languages=languages)
    
    assert result == 0  # Should still succeed with a warning
    
    # Check output
    captured = capsys.readouterr()
    assert "Warning: 'invalid' is not a recognized language code" in captured.out
    assert "Languages updated: en, fr" in captured.out
    
    # Check that the config file was updated with only valid languages
    config_file = temp_speechdown_dir / ".speechdown" / "config.json"
    with open(config_file, "r") as f:
        config_data = json.load(f)
    
    assert "languages" in config_data
    assert "invalid" not in config_data["languages"]
    assert "en" in config_data["languages"]
    assert "fr" in config_data["languages"]


def test_config_with_existing_language(temp_speechdown_dir, capsys):
    """Test adding a language that is already in the configuration."""
    add_language = "en"  # Already exists in the fixture
    
    result = config(temp_speechdown_dir, add_language=add_language)
    
    assert result == 0
    
    # Check output
    captured = capsys.readouterr()
    assert f"Language '{add_language}' already in configuration" in captured.out
    
    # Config file should be unchanged
    config_file = temp_speechdown_dir / ".speechdown" / "config.json"
    with open(config_file, "r") as f:
        config_data = json.load(f)
    
    assert config_data["languages"] == ["en", "uk", "ru"]