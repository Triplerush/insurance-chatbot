"""Application configuration management for environment variables."""
from __future__ import annotations

from functools import lru_cache
from typing import Literal, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Centralised configuration for the Insurance Chatbot backend."""
    formatter: Literal["mock", "langchain"] = Field(
        "mock", validation_alias="INSURANCE_CHATBOT_FORMATTER"
    )
    langchain_runner: Optional[str] = Field(
        default="services.agent.app.langchain_runner:run_langchain_agent",
        validation_alias="INSURANCE_CHATBOT_LANGCHAIN_RUNNER",
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    @field_validator("formatter", mode="before")
    @classmethod
    def _normalise_formatter(cls, value: str | None) -> str:
        return (value or "mock").lower()

@lru_cache()
def get_settings() -> Settings:
    """Return a cached instance of application settings."""
    return Settings()
