import os
from dotenv import load_dotenv
from pathlib import Path
from urllib.parse import quote_plus

# 讀取 .env 檔案
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Config:
    # 使用 os.getenv 抓取變數，後方可以設定預設值
    HOST=os.getenv('DB_HOST')
    USER=os.getenv('DB_USER')
    PASSWORD=os.getenv('DB_PASSWORD')
    DATABASE=os.getenv('DB_NAME')
    QUOTE_PASSWD = quote_plus(str(PASSWORD))
    DATABASE_URL = os.getenv("DATABASE_URL",  f"mysql+pymysql://{USER}:{QUOTE_PASSWD}@{HOST}:3306/{DATABASE}")
    AUTHORIZATION_TOKEN = os.getenv("AUTHORIZATION_TOKEN")

# from pydantic_settings import BaseSettings

# class Settings(BaseSettings):
#     CWA_API_KEY: str
#     DATABASE_URL: str = "mysql+pymysql://user:pass@localhost/db"

#     class Config:
#         env_file = ".env"

# settings = Settings()