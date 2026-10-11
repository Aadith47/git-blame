from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Reads GITHUB_TOKEN, GEMINI_API_KEY and OPENAI_API_KEY from the environment or a .env file."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    github_token: str = Field(min_length=1)
    gemini_api_key: str = Field(min_length=1)
    openai_api_key: str | None = None  # optional backup for when Gemini fails

    @field_validator("openai_api_key", mode="before")
    @classmethod
    def blank_means_not_set(cls, value):
        return value or None