import json
import pytest
from pathlib import Path
from unittest.mock import patch
import sys

# Add path to allow importing from the src directory
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "src"))

from speechdown.presentation.cli.commands import cli


@pytest.fixture
def temp_project_dir(tmp_path):
    """Create a temporary project directory for integration tests."""
    # Call the init command to set up a project
    with patch('sys.argv', ['sd', 'init', '-d', str(tmp_path)]):
        cli()
    
    return tmp_path


@pytest.mark.integration
def test_language_config_integration(temp_project_dir):
    """Test the full workflow of setting and using language configurations."""
    # Set specific languages
    with patch('sys.argv', ['sd', 'config', '-d', str(temp_project_dir), '--languages', 'en,fr']):
        result = cli()
    
    assert result == 0
    
    # Verify languages were set in config file
    config_path = temp_project_dir / ".speechdown" / "config.json"
    with open(config_path) as f:
        config_data = json.load(f)
    
    assert "languages" in config_data
    assert config_data["languages"] == ["en", "fr"]
    
    # Add a language
    with patch('sys.argv', ['sd', 'config', '-d', str(temp_project_dir), '--add-language', 'de']):
        result = cli()
    
    assert result == 0
    
    # Verify language was added
    with open(config_path) as f:
        config_data = json.load(f)
    
    assert "languages" in config_data
    assert set(config_data["languages"]) == set(["en", "fr", "de"])
    
    # Remove a language
    with patch('sys.argv', ['sd', 'config', '-d', str(temp_project_dir), '--remove-language', 'fr']):
        result = cli()
    
    assert result == 0
    
    # Verify language was removed
    with open(config_path) as f:
        config_data = json.load(f)
    
    assert "languages" in config_data
    assert set(config_data["languages"]) == set(["en", "de"])


@pytest.mark.integration
def test_invalid_language_handling_integration(temp_project_dir, capsys):
    """Test how the CLI handles invalid language codes."""
    # Try to set an invalid language
    with patch('sys.argv', ['sd', 'config', '-d', str(temp_project_dir), '--languages', 'en,invalid,fr']):
        result = cli()
    
    assert result == 0  # Should still succeed but with warning
    
    # Check warning was shown
    captured = capsys.readouterr()
    assert "Warning: 'invalid' is not a recognized language code" in captured.out
    
    # Verify only valid languages were set
    config_path = temp_project_dir / ".speechdown" / "config.json"
    with open(config_path) as f:
        config_data = json.load(f)
    
    assert "languages" in config_data
    assert set(config_data["languages"]) == set(["en", "fr"])
