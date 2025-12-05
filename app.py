import streamlit as st
import pandas as pd
import requests
import time

st.set_page_config(page_title="DOGE Real-Time Dashboard", layout="wide")

st.title("🚀 Real-Time DOGE/USDT Dashboard")
st.write("Monitoring harga Dogecoin secara real-time menggunakan Binance Data API (Polling 1 detik).")

# Session state
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=["time", "price"])

placeholder_message = st.empty()
placeholder_chart = st.empty()


def get_price():
    try:
        r = requests.get(
            "https://data.binance.com/api/v3/ticker/price?symbol=DOGEUSDT",
            timeout=5
        )
        data = r.json()
        return float(data["price"])
    except Exception as e:
        return None


# Ambil harga terbaru
price = get_price()

if price is not None:
    now = pd.Timestamp.now()
    st.session_state.df.loc[len(st.session_state.df)] = [now, price]

    if len(st.session_state.df) > 300:
        st.session_state.df = st.session_state.df.iloc[-300:]

    placeholder_message.markdown(
        f"### 💰 Harga Terbaru: **{price:.6f} USDT**  \n⏳ Auto refresh setiap 1 detik"
    )

    placeholder_chart.line_chart(
        st.session_state.df,
        x="time",
        y="price"
    )
else:
    placeholder_message.error("❌ Tidak bisa mengakses Binance Data API.")

# auto refresh
time.sleep(1)
st.experimental_set_query_params(refresh=str(time.time()))

