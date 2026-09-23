import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

def required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value

@dataclass(frozen=True)
class Settings:
    bot_token: str
    api_id: int
    api_hash: str
    mongo_uri: str
    session_encryption_key: str
    admin_ids: tuple[int, ...]
    tag_delay: float
    log_level: str
    database_name: str

    @classmethod
    def from_env(cls):
        admins = tuple(
            int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",")
            if x.strip()
        )
        return cls(
            bot_token=required("BOT_TOKEN"),
            api_id=int(required("API_ID")),
            api_hash=required("API_HASH"),
            mongo_uri=required("MONGO_URI"),
            session_encryption_key=required("SESSION_ENCRYPTION_KEY"),
            admin_ids=admins,
            tag_delay=max(0.0, float(os.getenv("TAG_DELAY", "5"))),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            database_name=os.getenv("DATABASE_NAME", "telegram_userbot"),
        )

settings = Settings.from_env()
