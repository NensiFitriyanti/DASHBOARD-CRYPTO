import streamlit as st
import pandas as pd
import requests
import time

# Konfigurasi halaman
st.set_page_config(page_title="DOGE Real-Time Dashboard", layout="wide")

st.title("🚀 Real-Time DOGE/USDT Dashboard")
st.write("Monitoring harga Dogecoin secara real-time menggunakan Binance REST API (Polling 1 detik).")

# Session state data
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=["time", "price"])

# Placeholder UI
placeholder_message = st.empty()
placeholder_chart = st.empty()

# Loop auto-refresh
def get_price():
    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=DOGEUSDT", timeout=5)
        data = r.json()
        return float(data["price"])
    except:
        return None

# update data
price = get_price()

if price is not None:
    now = pd.Timestamp.now()
    st.session_state.df.loc[len(st.session_state.df)] = [now, price]

    # keep data lightweight
    if len(st.session_state.df) > 300:
        st.session_state.df = st.session_state.df.iloc[-300:]

    placeholder_message.markdown(
        f"### 💰 Harga Terbaru: **{price:.6f} USDT** (Auto Refresh 1 detik)"
    )

    # tampilkan grafik
    placeholder_chart.line_chart(
        st.session_state.df,
        x="time",
        y="price"
    )

else:
    placeholder_message.error("Gagal mengambil data dari Binance. Coba lagi.")

# refresh halaman tiap 1 detik
time.sleep(1)
st.experimental_set_query_params(refresh=str(time.time()))

