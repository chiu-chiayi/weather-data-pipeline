import streamlit as st
import requests

# streamlit run web/app.py

# st.set_page_config(layout="wide")

st.title("🌦️ 最新天氣儀表板")

# method1. 輸入框
# city = st.text_input("輸入你想查詢的城市", value="臺北市")
# method2. 從 API 抓取所有可選的城市、並建立下拉選單
@st.cache_data # 使用快取，這樣不用每次重新整理網頁都去問資料庫
def get_all_cities():
    res = requests.get("http://127.0.0.1:8000/locations")
    return res.json()
city_list = get_all_cities()

# label: 顯示的文字, options: 選項清單
target_city = st.selectbox("請選擇要查詢的城市:", options=city_list)


# 按鈕與 API 串接
if st.button("查詢天氣"):
    # 呼叫 FastAPI
    response = requests.get(f"http://127.0.0.1:8000/get-weather/{target_city}")
    data = response.json()

    if "error" not in data:
        # 顯示卡片
        col1, col2, col3, col4 = st.columns(4)
        col5, = st.columns(1)

        col1.metric("天氣現象", f"{data['wx']}")
        col2.metric("降雨機率", f"{data['pop']} %")
        col3.metric("最低溫", f"{data['mint']} °C")
        col4.metric("最高溫", f"{data['maxt']} °C")
        col5.metric("舒適度", f"{data['ci']}")

        st.columns(1).metric("預報資料時間", f"{data['full_date']} {data['full_time']}")
        st.columns(1).metric("更新時間", f"{data['data_pull_timeS']}")
    else:
        st.error("找不到資料！")