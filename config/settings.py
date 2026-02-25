from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI_Service"
    app_version: str = "1.0.0"
    app_env: str = "development"

    # Google Gemini / LangChain
    google_api_key: str = ""
    gemini_model: str = "gemini-3-flash-preview"

    model_config = SettingsConfigDict(
        env_file=(".env",),
        env_prefix="APP_",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
