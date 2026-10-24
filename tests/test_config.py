from github_analyser.config import ENV_FILE


def test_env_file_is_found_from_the_project_root_not_the_current_folder():
    # Must be an absolute path next to app.py, so it works from any working directory.
    assert ENV_FILE.is_absolute()
    assert ENV_FILE.name == ".env"
    assert (ENV_FILE.parent / "app.py").exists()