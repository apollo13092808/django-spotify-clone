import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / "subdir".
BASE_DIR = Path(__file__).resolve().parent.parent

# # ========== SQLite ==========
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#     }
# }

# ========== PostgreSQL ==========
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv(key="DB_NAME"),
        "USER": os.getenv(key="DB_USER"),
        "PASSWORD": os.getenv(key="DB_PASSWORD"),
        "HOST": os.getenv(key="DB_HOST"),
        "PORT": os.getenv(key="DB_PORT"),
    }
}

# # ========== MySQL ==========
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.mysql",
#         "NAME": "DATABASE_NAME",
#         "USER": "USER_NAME",
#         "PASSWORD": "PASSWORD",
#         "HOST": "HOST_ADDRESS",
#         "PORT": "PORT",
#     }
# }

# # ========== MSSQL SERVER ==========
# DATABASES = {
#     "default": {
#         "ENGINE": "mssql",
#         "NAME": "DATABASE_NAME",
#         "USER": "USER_NAME",
#         "PASSWORD": "PASSWORD",
#         "HOST": "HOST_ADDRESS",
#         "PORT": "1433",
#         "OPTIONS": {"driver": "ODBC Driver 17 for SQL Server",
#         },
#     },
# }
