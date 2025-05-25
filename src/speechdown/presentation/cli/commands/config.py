"""Configuration command handler for speechdown CLI."""
from pathlib import Path
import logging

from speechdown.domain.value_objects import Language, LANGUAGES
from speechdown.infrastructure.adapters.config_adapter import ConfigAdapter
from speechdown.presentation.cli.commands.common import SpeechDownPaths

__all__ = ["config"]


def config(
        *,
        directory: Path, 
        add_language: str | None = None,
        languages: str | None = None, 
        model_name: str | None = None,
        output_dir: str | None = None, 
        remove_language: str | None = None, 
) -> int:
    """
    Configure the speechdown project settings.

    Args:
        directory: The directory containing the speechdown project
        add_language: Language code to add to the configuration
        languages: Comma-separated list of language codes to set (replaces existing languages)
        model_name: The name of the Whisper model to use for transcription
        output_dir: The directory to store transcription output files
        remove_language: Language code to remove from the configuration

    Returns:
        Exit code (0 for success)
    """
    try:
        speechdown_paths = SpeechDownPaths.from_working_directory(directory)
        config_adapter = ConfigAdapter.load_config_from_path(speechdown_paths.config)
        
        # Handle output directory configuration
        if output_dir is not None:
            config_adapter.set_output_dir(output_dir)
            print(f"Output directory set to: {output_dir}")

        # Handle model name configuration
        if model_name is not None:
            config_adapter.set_model_name(model_name)
            print(f"Model name set to: {model_name}")
        
        # Handle language configuration
        if languages is not None:
            # Set the complete list of languages
            try:
                language_codes = [code.strip() for code in languages.split(",")]
                new_languages = []
                for code in language_codes:
                    if code not in LANGUAGES:
                        print(f"Warning: '{code}' is not a recognized language code. Skipping.")
                    else:
                        new_languages.append(Language(code))
                
                if new_languages:
                    config_adapter.set_languages(new_languages)
                    print(f"Languages updated: {', '.join([lang.code for lang in new_languages])}")
                else:
                    print("No valid languages provided. Configuration unchanged.")
            except ValueError as e:
                print(f"Error setting languages: {e}")
        
        if add_language is not None:
            # Add a single language
            try:
                if add_language not in LANGUAGES:
                    print(f"Warning: '{add_language}' is not a recognized language code. Skipping.")
                else:
                    current_languages = config_adapter.get_languages()
                    if any(lang.code == add_language for lang in current_languages):
                        print(f"Language '{add_language}' already in configuration. No changes made.")
                    else:
                        new_languages = current_languages + [Language(add_language)]
                        config_adapter.set_languages(new_languages)
                        print(f"Added language: {add_language}")
            except ValueError as e:
                print(f"Error adding language: {e}")
        
        if remove_language is not None:
            # Remove a single language
            current_languages = config_adapter.get_languages()
            new_languages = [lang for lang in current_languages if lang.code != remove_language]
            
            if len(current_languages) == len(new_languages):
                print(f"Language '{remove_language}' not found in configuration. No changes made.")
            else:
                config_adapter.set_languages(new_languages)
                print(f"Removed language: {remove_language}")
            
        # Display current configuration
        print("Current configuration:")
        print(f"  Languages: {', '.join([lang.code for lang in config_adapter.get_languages()])}")
        output_dir_value = config_adapter.get_output_dir()
        print(f"  Output directory: {output_dir_value if output_dir_value else 'Not set'}")
        model_name_value = config_adapter.get_model_name()
        print(f"  Model name: {model_name_value if model_name_value else 'Not set'}")
        
        return 0
    except Exception as e:
        logging.error(f"Error during configuration: {e}")
        return 1
