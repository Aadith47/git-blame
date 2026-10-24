from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# The .env file sits in the project root, next to app.py. Building the path from this file
# means the app finds it no matter which folder Streamlit was started from.
ENV_FILE = Path(__file__).resolve().parent.parent / ".env"

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


class Settings(BaseSettings):
    """Reads the API keys and options from the environment or .env."""

    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    github_token: str = Field(min_length=1)
    gemini_api_key: str = Field(min_length=1)  # the main AI model
    openrouter_api_key: str | None = None      # first backup, tried if Gemini fails
    openrouter_models: str = "openai/gpt-5-mini"  # comma-separated; OpenRouter tries them in order
    openai_api_key: str | None = None          # last backup
    daily_review_limit: int = Field(default=50, ge=0)  # AI reviews per day, shared by all visitors
    review_deadline_seconds: float = Field(default=12, gt=0)  # the longest one AI model may take
    review_budget_seconds: float = Field(default=20, gt=0)    # the longest a whole review may take

    @field_validator("openai_api_key", "openrouter_api_key", mode="before")
    @classmethod
    def blank_means_not_set(cls, value):
        return value or None


def backup_providers(settings) -> list[str]:
    """Names of the backup AI providers that have a key, in the order they are tried."""
    names = []
    if getattr(settings, "openrouter_api_key", None):
        names.append("OpenRouter")
    if getattr(settings, "openai_api_key", None):
        names.append("OpenAI")
    return names


def openrouter_model_list(settings) -> list[str]:
    """The OpenRouter models from the comma-separated setting, with blanks removed."""
    return [model.strip() for model in settings.openrouter_models.split(",") if model.strip()]