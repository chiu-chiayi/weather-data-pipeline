from sqlmodel import Session, create_engine

from core.config import Config


# 1. 建立引擎
# echo=True 可以讓你在終端機看到實際執行的 SQL 指令，開發時很好用
engine = create_engine(Config.DATABASE_URL)


# 2. 建立一個工具函數，這就是 FastAPI 依賴注入 (Depends) 會用到的東西
def get_session():
    with Session(engine) as session:
        yield session # yield 會讓 API 執行完後，自動回來執行 session 關閉