from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 8000

    model_name: str = "ai4bharat/IndicF5"
    device: str = "cpu"
    dtype: str = "float32"

    default_language: str = "ben"
    default_voice: str = "default"
    inference_timeout: int = 120

    output_dir: str = str(Path.cwd() / "storage" / "audio")

    log_level: str = "INFO"

    model_config = {"env_prefix": "", "case_sensitive": False}


settings = Settings()
