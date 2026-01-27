import streamlit as st
import requests

from core.config import Config

# streamlit run web/app.py

st.set_page_config(layout="wide")

st.title("🌦️ 最新天氣儀表板")

# method1. 輸入框
# city = st.text_input("輸入你想查詢的城市", value="臺北市")
# method2. 從 API 抓取所有可選的城市、並建立下拉選單
@st.cache_data # 使用快取，這樣不用每次重新整理網頁都去問資料庫
def get_all_cities():
    res = requests.get(f"http://{Config.BACKEND_HOST}:8000/locations", timeout=5)
    return res.json()
city_list = get_all_cities()

# label: 顯示的文字, options: 選項清單
target_city = st.selectbox("請選擇要查詢的城市:", options=city_list)


# 按鈕與 API 串接
if st.button("查詢天氣"):
    # 呼叫 FastAPI
    response = requests.get(f"http://{Config.BACKEND_HOST}:8000/get-weather/{target_city}", timeout=5)
    data = response.json()

    if "error" not in data:
        # 顯示卡片
        col1, col2, col3, col4 = st.columns(4)
        col5, = st.columns(1)
        col_datatime, col_updatetime = st.columns(2)

        col1.metric("天氣現象", f"{data['Fact_Weather_Forecast']['wx']}")
        col2.metric("降雨機率", f"{data['Fact_Weather_Forecast']['pop']} %")
        col3.metric("最低溫", f"{data['Fact_Weather_Forecast']['mint']} °C")
        col4.metric("最高溫", f"{data['Fact_Weather_Forecast']['maxt']} °C")
        col5.metric("舒適度", f"{data['Fact_Weather_Forecast']['ci']}")

        col_datatime.metric("預報資料時間", f"{data['Dim_Date']['full_date']} {data['Dim_Time']['full_time']}")
        col_updatetime.metric("更新時間", f"{data['Fact_Weather_Forecast']['data_pull_time']}")
    else:
        st.error("找不到資料！")