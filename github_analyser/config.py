from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# The .env file sits in the project root, next to app.py. Building the path from this file
# means the app finds it no matter which folder Streamlit was started from.
ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    """Reads GITHUB_TOKEN, GEMINI_API_KEY and OPENAI_API_KEY from the environment or .env."""

    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    github_token: str = Field(min_length=1)
    gemini_api_key: str = Field(min_length=1)
    openai_api_key: str | None = None  # optional backup for when Gemini fails
    daily_review_limit: int = Field(default=50, ge=0)  # AI reviews per day, shared by all visitors

    @field_validator("openai_api_key", mode="before")
    @classmethod
    def blank_means_not_set(cls, value):
        return value or None