import streamlit as st
import requests
from core.config import Config

# streamlit run web/app.py

st.set_page_config(page_title="City Weather Dashboard", page_icon="🌦️", layout="wide")

@st.cache_data # use cache
def get_all_cities():
    res = requests.get(f"http://{Config.BACKEND_HOST}:8000/locations", timeout=5)
    return res.json()

# --- Sidebar Layout ---
st.sidebar.header("📍 城市查詢")
city_list = sorted(get_all_cities())
target_city = st.sidebar.selectbox("請選擇城市:", options=city_list)
query_btn = st.sidebar.button("查詢天氣", use_container_width=True)

# --- Main Content ---
st.title("🌦️ City Weather Dashboard")

if query_btn:
    with st.spinner('正在獲取最新天氣資訊...'):
        try:
            response = requests.get(f"http://{Config.BACKEND_HOST}:8000/get-weather/{target_city}", timeout=5)
            data = response.json()

            if "error" not in data:
                forecast = data['Fact_Weather_Forecast']

                # 第一排: 城市與預報時間
                st.markdown(f"### 🏙️ {target_city if target_city else '未選擇'} ｜ 📅 {data['Dim_Date']['full_date']} {data['Dim_Time']['full_time']}")

                # 第二排: 核心天氣資訊
                st.markdown("---")
                col1, col2, col3 = st.columns(3)
                col1.metric("**🌡️ 天氣現象**", forecast['wx'])
                col2.metric("**☔ 降雨機率**", f"{forecast['pop']} %")
                col3.metric("**🧘 舒適度**", forecast['ci'])

                # 第三排: 溫度範圍
                st.markdown("---")
                t_col1, t_col2 = st.columns(2)
                t_col1.metric("**❄️ 最低溫**", f"{forecast['mint']} °C")
                t_col2.metric("**🔥 最高溫**", f"{forecast['maxt']} °C")

                # 第四排: 時間戳記
                st.markdown("---")
                footer = st.columns(1)
                footer[0].caption(f"🔄 **資料更新時間**：{forecast['data_pull_time']}")
            else:
                st.error(f"找不到 {target_city} 的天氣資料！")
        except Exception as e:
            st.error(f"連線後端 API 發生錯誤: {e}")
else:
    st.info("請從左側選單選擇城市，並點擊「查詢天氣」按鈕。")