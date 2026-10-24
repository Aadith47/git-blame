from types import SimpleNamespace

from github_analyser.config import ENV_FILE, backup_providers, openrouter_model_list


def test_env_file_is_found_from_the_project_root_not_the_current_folder():
    # Must be an absolute path next to app.py, so it works from any working directory.
    assert ENV_FILE.is_absolute()
    assert ENV_FILE.name == ".env"
    assert (ENV_FILE.parent / "app.py").exists()


def settings(**overrides):
    values = dict(openrouter_api_key=None, openai_api_key=None, openrouter_models="openai/gpt-5-mini")
    values.update(overrides)
    return SimpleNamespace(**values)


def test_no_backup_keys_means_no_backups():
    assert backup_providers(settings()) == []


def test_openrouter_is_tried_before_openai():
    assert backup_providers(settings(openrouter_api_key="r", openai_api_key="o")) == ["OpenRouter", "OpenAI"]


def test_openai_alone_is_the_only_backup():
    assert backup_providers(settings(openai_api_key="o")) == ["OpenAI"]


def test_openrouter_model_list_is_split_and_cleaned():
    assert openrouter_model_list(settings(openrouter_models=" a/x , b/y ,")) == ["a/x", "b/y"]