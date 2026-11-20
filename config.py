import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import URL

BASE_DIR = Path(__file__).resolve().parent

env_path = BASE_DIR / ".env"

load_dotenv(env_path, override=True)

print("ENV file exists:", env_path.exists())
print("DB_USERNAME loaded:", bool(os.getenv("DB_USERNAME")))
print("DB_PASSWORD loaded:", bool(os.getenv("DB_PASSWORD")))
print("DB_HOST loaded:", bool(os.getenv("DB_HOST")))
print("DB_NAME loaded:", bool(os.getenv("DB_NAME")))


class Config:

    SQLALCHEMY_DATABASE_URI = URL.create(
        drivername="mysql+pymysql",
        username=os.getenv("DB_USERNAME"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        database=os.getenv("DB_NAME"),
        query={"charset": "utf8mb4"}
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = os.getenv("SECRET_KEY")