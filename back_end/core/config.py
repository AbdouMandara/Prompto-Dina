from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    hf_token: str | None = None
    default_provider: str = "huggingface"
    hf_router_url: str = "https://router.huggingface.co/v1"
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:8000",
    ]

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()
