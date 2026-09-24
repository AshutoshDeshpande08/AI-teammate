"""
Central place for application configuration.

Kept intentionally simple for the hackathon MVP: plain environment
variables with sensible defaults, no extra config framework.
"""

import os


class Settings:
    # SQLite file lives inside backend/ by default. Override with an env
    # var if you ever want to point at Postgres later.
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./aiteammate.db")

    APP_NAME: str = "AI-Teammate Backend"
    APP_VERSION: str = "0.1.0"


settings = Settings()
