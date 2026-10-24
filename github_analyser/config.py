from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).resolve().parent.parent / ".env"

class Settings(BaseSettings):

    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    github_token: str = Field(min_length=1)
    gemini_api_key: str = Field(min_length=1)
    openrouter_api_key: str | None = None
    daily_review_limit: int = Field(default=50, ge=0)
    review_deadline_seconds: float = Field(default=12, gt=0)
    review_budget_seconds: float = Field(default=20, gt=0)

    @field_validator("openrouter_api_key", mode="before")
    @classmethod
    def blank_means_not_set(cls, value):
        return value or None