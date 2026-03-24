from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    database_url: str = Field(
        "postgresql+asyncpg://postgres:postgres@db:5432/postgres",
        validation_alias="DATABASE_URL",
    )
    log_level: str = "INFO"
    admin_id: str = Field(
        "99999999-9999-9999-9999-999999999999",
        validation_alias="ADMIN",
    )
    user_id: str = Field(
        "11111111-1111-1111-1111-111111111111",
        validation_alias="USER",
    )
    time_jwt_minutes: int = Field(
        30,
        validation_alias="TIME_JWT_MINUTES",
    )
    secret_key: str = Field(
        "t8aBv2feeg-Pk4_UJveM0DUwYM01cMRRpUldKsWm31M",
        validation_alias="SECRET_KEY",
    )
    algorithm: str = Field(
        "HS256",
        validation_alias="ALGORITHM",
    )


settings = Settings()
