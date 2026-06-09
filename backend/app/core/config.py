import os

from dotenv import load_dotenv


load_dotenv()


class Settings:
    JWT_KEY: str = os.getenv("SECRET_KEY", "change-me-in-prod-use-a-long-secret-key")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )


settings = Settings()
