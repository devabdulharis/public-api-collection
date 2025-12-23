from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    api_key: str = Field(default="CHANGE-ME", alias="API_KEY")
    cors_allow_origins: str = Field(default="*", alias="CORS_ALLOW_ORIGINS")

    bmkg_cache_ttl_seconds: int = Field(default=30, alias="BMKG_CACHE_TTL_SECONDS")
    ytdlp_cache_ttl_seconds: int = Field(default=15, alias="YTDLP_CACHE_TTL_SECONDS")


settings = Settings()


def cors_origins_list() -> list[str]:
    raw = settings.cors_allow_origins.strip()
    if raw == "*" or raw == "":
        return ["*"]
    return [x.strip() for x in raw.split(",") if x.strip()]