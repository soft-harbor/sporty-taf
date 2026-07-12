from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        enable_decoding=False,
        case_sensitive=False,
        extra="ignore",
    )

    frontend_base_url: str
    backend_base_url: str
    sporty_test_user_id: str


settings = Settings()
