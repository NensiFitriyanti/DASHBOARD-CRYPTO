import streamlit as st
import pandas as pd
import websocket
import json
import threading
import time

# ---------------------------------------
# PAGE CONFIG
# ---------------------------------------
st.set_page_config(
    page_title="Real-Time DOGE Dashboard",
    layout="wide"
)

st.markdown(
    """
    <h1 style='color:#00FFAA; font-weight:700;'>🚀 Real-Time DOGE/USDT Dashboard</h1>
    <p style='color:#cccccc;'>Monitoring harga Dogecoin secara real-time menggunakan Binance WebSocket API.</p>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------
# LOAD SECRET
# ---------------------------------------
try:
    WS_URL = st.secrets["WS_URL"]
except:
    WS_URL = "wss://stream.binance.com:9443/ws/dogeusdt@trade"  # fallback aman


# ---------------------------------------
# DATA STORAGE
# ---------------------------------------
df = pd.DataFrame(columns=["time", "price"])
current_price = 0.0
prev_price = 0.0

# UI placeholders
col1, col2, col3 = st.columns(3)
placeholder_price = col1.empty()
placeholder_change = col2.empty()
placeholder_highlow = col3.empty()
placeholder_chart = st.empty()


# ---------------------------------------
# WEBSOCKET CALLBACK
# ---------------------------------------
def on_message(ws, message):
    global df, current_price, prev_price

    data = json.loads(message)
    price = float(data["p"])
    timestamp = pd.Timestamp.now()

    prev_price = current_price
    current_price = price

    df.loc[len(df)] = [timestamp, price]

    # limiting dataframe so memory stays light
    if len(df) > 500:
        df = df.iloc[-500:]


# ---------------------------------------
# RUN WEBSOCKET
# ---------------------------------------
def run_ws():
    ws = websocket.WebSocketApp(WS_URL, on_message=on_message)
    ws.run_forever()


# Jalankan WebSocket sebagai thread
ws_thread = threading.Thread(target=run_ws)
ws_thread.daemon = True
ws_thread.start()


# ---------------------------------------
# MAIN STREAMLIT LOOP
# ---------------------------------------
while True:
    if len(df) > 2:

        # indikator harga naik/turun
        if current_price > prev_price:
            price_color = "#00FF00"
            arrow = "▲"
        elif current_price < prev_price:
            price_color = "#FF5555"
            arrow = "▼"
        else:
            price_color = "#FFFFFF"
            arrow = "▬"

        # persen perubahan
        try:
            percent_change = ((current_price - prev_price) / prev_price) * 100
        except:
            percent_change = 0

        # card harga
        placeholder_price.markdown(
            f"""
            <div style="background-color:#111111; padding:15px; border-radius:10px;">
                <h3 style="color:#bbbbbb;">Harga Sekarang</h3>
                <h1 style="color:{price_color};">{arrow} {current_price:.6f} USDT</h1>
            </div>
            """,
            unsafe_allow_html=True
        )

        # card perubahan
        placeholder_change.markdown(
            f"""
            <div style="background-color:#111111; padding:15px; border-radius:10px;">
                <h3 style="color:#bbbbbb;">Perubahan Harga</h3>
                <h1 style="color:{price_color};">{percent_change:.4f}%</h1>
            </div>
            """,
            unsafe_allow_html=True
        )

        # card high–low session
        high_price = df["price"].max()
        low_price = df["price"].min()

        placeholder_highlow.markdown(
            f"""
            <div style="background-color:#111111; padding:15px; border-radius:10px;">
                <h3 style="color:#bbbbbb;">High - Low (Session)</h3>
                <h2 style="color:#00FFFF;">High : {high_price:.6f}</h2>
                <h2 style="color:#FFAA00;">Low  : {low_price:.6f}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

        # grafik real-time
        with placeholder_chart.container():
            st.line_chart(df, x="time", y="price")

    time.sleep(0.5)
