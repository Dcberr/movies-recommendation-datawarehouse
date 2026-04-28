# config/settings.py

import os

DB_CONFIG = {
    "driver": os.getenv("DB_DRIVER", "ODBC Driver 18 for SQL Server"),
    "server": os.getenv("DB_SERVER", "moiverecommendation.database.windows.net"),
    "database": os.getenv("DB_NAME", "moviedw"),
    "username": os.getenv("DB_USER", "datawarehouse_admin"),
    "password": os.getenv("DB_PASSWORD", "Movie@123"),
}

APP_CONFIG = {
    "title": "Movie Analytics Dashboard",
    "page_size": 10,
    "ai_service_url": os.getenv("AI_SERVICE_URL", "").rstrip("/"),
}
