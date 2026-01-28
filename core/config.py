import os
from dotenv import load_dotenv
from pathlib import Path
from urllib.parse import quote_plus

# Read environment variables from .env file
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Config:
    # Use os.getenv to fetch variables, with optional default values
    HOST=os.getenv('DB_HOST')
    USER=os.getenv('DB_USER')
    PASSWORD=os.getenv('DB_PASSWORD')
    DATABASE=os.getenv('DB_NAME')
    PORT=os.getenv('DB_PORT')
    QUOTE_PASSWD = quote_plus(str(PASSWORD))
    DATABASE_URL = os.getenv("DATABASE_URL",  f"mysql+pymysql://{USER}:{QUOTE_PASSWD}@{HOST}:{PORT}/{DATABASE}?charset=utf8mb4")
    AUTHORIZATION_TOKEN = os.getenv("AUTHORIZATION_TOKEN")
    BACKEND_HOST = os.getenv("BACKEND_HOST")
