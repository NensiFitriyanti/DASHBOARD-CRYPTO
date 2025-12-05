import streamlit as st
import pandas as pd
import requests
import time

st.set_page_config(page_title="Crypto Trend Realtime", layout="wide")

st.title("📈 Real-Time Crypto Price Trend")
st.write("Data diambil dari CoinGecko API (Polling 1 detik, bebas API Key).")

# pilih crypto
crypto = st.selectbox(
    "Pilih Cryptocurrency:",
    ["bitcoin", "ethereum", "binancecoin", "dogecoin", "solana", "cardano", "ripple"]
)

st.write(f"Menampilkan trend harga **{crypto.capitalize()}** terhadap USD.")

# session data
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=["time", "price"])

placeholder_price = st.empty()
placeholder_chart = st.empty()

def get_price(coin):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"
        r = requests.get(url, timeout=5)
        data = r.json()
        return float(data[coin]["usd"])
    except:
        return None

# fetch harga
price = get_price(crypto)

if price is not None:
    now = pd.Timestamp.now()
    st.session_state.df.loc[len(st.session_state.df)] = [now, price]

    if len(st.session_state.df) > 300:
        st.session_state.df = st.session_state.df.iloc[-300:]

    placeholder_price.markdown(
        f"### 💰 Harga Terbaru: **{price:.5f} USD**  
        ⏳ Auto refresh setiap 1 detik"
    )

    placeholder_chart.line_chart(
        st.se
