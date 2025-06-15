from speechdown.presentation.cli.commands import init


def test_init_command_creates_database(tmp_path):
    directory = tmp_path
    init(directory)
    assert (directory / ".speechdown" / "speechdown.db").exists()
    assert (directory / ".speechdown" / "config.json").exists()
