# 1. 使用 Python 3.10 作為基底
FROM python:3.10

# 安裝 cron 與基礎工具
RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

# 2. 設定容器內的工作目錄
WORKDIR /app

# 3. 先複製 requirements.txt，利用 Docker 的快取機制縮短後續構建時間
COPY requirements.txt .

# 4. 根據 requirements.txt 安裝套件
RUN pip install --no-cache-dir -r requirements.txt

# 5. 複製當前目錄下所有檔案
COPY . .

# 確保 logs 目錄存在
RUN mkdir -p /app/logs && touch /app/logs/cwa_fetch.log

# 處理 Cron 檔案（如果不再用掛載的）
COPY crontab_file /etc/cron.d/weather-cron
RUN chmod 0644 /etc/cron.d/weather-cron && crontab /etc/cron.d/weather-cron

# 6. 映射 FastAPI 的 8000 埠
EXPOSE 8000

# 7. 啟動命令：main 為檔案名，app 為程式裡的 FastAPI 物件名
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]