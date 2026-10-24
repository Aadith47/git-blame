from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# The .env file sits in the project root, next to app.py. Building the path from this file
# means the app finds it no matter which folder Streamlit was started from.
ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    """Reads the API keys and limits from the environment or .env."""

    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    github_token: str = Field(min_length=1)
    gemini_api_key: str = Field(min_length=1)  # the main AI model
    openrouter_api_key: str | None = None      # optional backup, used if Gemini fails
    daily_review_limit: int = Field(default=50, ge=0)  # AI reviews per day, shared by all visitors
    review_deadline_seconds: float = Field(default=12, gt=0)  # the longest one AI model may take
    review_budget_seconds: float = Field(default=20, gt=0)    # the longest a whole review may take

    @field_validator("openrouter_api_key", mode="before")
    @classmethod
    def blank_means_not_set(cls, value):
        return value or None