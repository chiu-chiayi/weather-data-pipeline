# weather-data-pipeline

### Overview
This project implements an automated ETL (Extract, Transform, Load) pipeline for weather data, designed to collect, process, and store meteorological information for analysis.
In order to present the data, we use streamlit to build a web app to display weather forecast.

### Pipeline Workflow
1.  **Data Extraction**: Fetches real-time weather metrics from external REST APIs.
2.  **Data Transformation**: Cleanses raw JSON responses, handles missing values, and normalizes data formats using processing libraries.
3.  **Data Loading**: Persists the structured data into a relational database or storage backend for downstream consumption.

### 專案簡介
本專案實現了一個自動化的天氣數據 ETL (擷取、轉換、載入) 流水線，旨在收集、處理並儲存氣象資訊以供後續分析使用。
為方便呈現，使用 streamlit 建立一個 web app，作為展示天氣預報的介面。

### 工作流程
1.  **數據擷取 (Extraction)**：從外部 REST API 獲取即時天氣指標。
2.  **數據轉換 (Transformation)**：清洗原始 JSON 回應、處理缺失值，並使用處理套件將數據格式標準化。
3.  **數據載入 (Loading)**：將結構化數據持久化至關聯式資料庫或存儲後端，供下游應用使用。
