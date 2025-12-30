from fastapi import FastAPI
import httpx

# 創建一個 FastAPI 應用實例
# app 是你的主要交互對象
app = FastAPI()

# 定義一個路徑操作 (Path Operation)
# @app.get("/") 表示當收到對根路徑 "/" 的 GET 請求時，執行下面的函數
@app.get("/test/")
def read_root(name: str = "World"):
    # 這個異步函數將處理請求並返回一個字典
    # FastAPI 會將字典轉換為 JSON 響應
    return {"message": f"Hello, {name}!"}

