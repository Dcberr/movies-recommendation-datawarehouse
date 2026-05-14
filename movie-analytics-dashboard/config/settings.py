# config/settings.py

import os

DB_CONFIG = {
    "driver": os.getenv("DB_DRIVER", "ODBC Driver 18 for SQL Server"),
    "server": os.getenv("DB_SERVER", "moviedw.database.windows.net"),
    "database": os.getenv("DB_NAME", "moviedatawarehouse"),
    "username": os.getenv("DB_USER", "datawarehouse"),
    "password": os.getenv("DB_PASSWORD", "MovieDW123!"),
}

APP_CONFIG = {
    "title": "Movie Analytics Dashboard",
    "page_size": 10,
    "ai_service_url": os.getenv("AI_SERVICE_URL", "").rstrip("/"),
}
