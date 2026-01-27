# weather-data-pipeline

### Overview
This project implements an automated ETL (Extract, Transform, Load) pipeline for weather data, designed to collect, process, and store meteorological information for analysis.

### Pipeline Workflow
1.  **Data Extraction**: Build a cron job to retrieve real-time weather metrics from the Central Weather Administration (CWA) API every 6 hours.
2.  **Data Transformation**: Cleanse JSON responses, handle missing values, and use processing libraries to standardize data formats.
3.  **Data Loading**: Persist structured data into a relational database (MySQL).
4.  **Data Usage**: Establish a REST API using FastAPI to interface with the database for downstream applications.
5.  **Data Presentation**: Create a web app using Streamlit as the interface for displaying weather forecasts.

Additionally, the project provides relevant files such as Dockerfile, docker-compose.yml, and requirements.txt to facilitate rapid deployment.

### 專案簡介
本專案實現了一個自動化的天氣數據 ETL (擷取、轉換、載入) 流水線，旨在收集、處理並儲存氣象資訊以供後續分析使用。

### 工作流程
1.  **數據擷取 (Extraction)**：建立一個 cron job，每 6 小時從中央氣象署(CWA)的 API 獲取即時天氣指標。
2.  **數據轉換 (Transformation)**：清洗 JSON 回應、處理缺失值，並使用處理套件將數據格式標準化。
3.  **數據載入 (Loading)**：將結構化數據持久化至關聯式資料庫(MySQL)。
4.  **數據使用 (Usage)**：使用 FastAPI 建立 REST API，串接資料庫，供下游應用使用。
5.  **數據呈現 (Presentation)**：使用 streamlit 建立 web app，作為展示天氣預報的介面。

此外，專案提供 Dockerfile、docker-compose.yml、requirements.txt 等相關檔案，以方便快速部署。

![Dashboard Preview](images/web-app-screenshot.png)