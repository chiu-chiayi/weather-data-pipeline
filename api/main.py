from fastapi import FastAPI, Depends
from sqlmodel import Session, select, desc, asc

from core.database import get_session
from models.weather import *

# uvicorn api.main:app --reload
# http://127.0.0.1:8000/docs : Swagger UI

# SQLModel: 為一父類別，繼承它代表這個類別同時具備 Pydantic(格式檢查) 與 SQLAlchemy(資料庫操作) 的功能。
# Session: 程式與資料庫之間進行對話的視窗
# engine: 通往資料庫的大門

# fastAPI 是一個用於構建 API 的 Web 框架，基於標準 Python 類型提示。
# 需要安裝 FastAPI 本身，以及一個 ASGI 伺服器來運行它，如 Uvicorn。


# 創建一個 FastAPI 應用實例
# app 是你的主要交互對象
app = FastAPI()

# 定義一個路徑操作 (Path Operation)
# @app.get("/") 表示當收到對 "/get-weather" 的 GET 請求時(當使用者訪問網站的路徑時)，執行下面的函數。
# @app.get 把函數註冊到了 FastAPI 的路由系統中，這個「裝飾器」可以在函數執行前或執行後做一些額外的事情。
# FastAPI 會將字典轉換為 JSON 格式，傳回給瀏覽器

@app.get("/get-weather/{target_city}")
def read_weather(target_city: str, session: Session = Depends(get_session)):
    statement = (
        select(Fact_Weather_Forecast)
        .join(Dim_Location, Fact_Weather_Forecast.location_sk == Dim_Location.sk)
        .join(Dim_Date, Fact_Weather_Forecast.start_date_id == Dim_Date.id)
        .join(Dim_Time, Fact_Weather_Forecast.start_time_id == Dim_Time.id)
        .where(Dim_Location.location_name == target_city)
        .order_by(desc(Fact_Weather_Forecast.sk))
    )
    results = session.exec(statement).first()
    if results:
        return results
    return {"error": "找不到資料"}

@app.get("/locations")
def get_location(session: Session = Depends(get_session)):
    statement = select(Dim_Location.location_name)
    results = session.exec(statement).all()
    return results

@app.get("/hello")
def hello():
    return {"message": "Hello World"}