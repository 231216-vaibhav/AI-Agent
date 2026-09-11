import os
from pathlib import Path
from dotenv import load_dotenv

# Search for .env in current working directory and parent directories
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-5")
    MOCK_OPENAI: bool = os.getenv("MOCK_OPENAI", "false").lower() in ("true", "1", "yes")
    
    @classmethod
    def is_api_key_set(cls) -> bool:
        return bool(cls.OPENAI_API_KEY and cls.OPENAI_API_KEY.strip())

settings = Settings()
