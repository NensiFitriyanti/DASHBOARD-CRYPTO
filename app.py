import streamlit as st
import pandas as pd
import websocket
import json
import threading
import time

# ---------------------------------------
# PAGE CONFIG
# ---------------------------------------
st.set_page_config(page_title="Real-Time DOGE Dashboard", layout="wide")

st.title("🚀 Real-Time DOGE/USDT Dashboard")
st.write("Monitoring harga Dogecoin secara real-time menggunakan Binance WebSocket API.")


# ---------------------------------------
# SESSION STATE SETUP
# ---------------------------------------
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=["time", "price"])

if "current_price" not in st.session_state:
    st.session_state.current_price = 0.0

if "prev_price" not in st.session_state:
    st.session_state.prev_price = 0.0


# ---------------------------------------
# WEBSOCKET CALLBACK
# ---------------------------------------
def on_message(ws, message):
    data = json.loads(message)
    price = float(data["p"])
    timestamp = pd.Timestamp.now()

    st.session_state.prev_price = st.session_state.current_price
    st.session_state.current_price = price

    # tambah data baru
    st.session_state.df.loc[len(st.session_state.df)] = [timestamp, price]

    # batasi 300 data biar ringan
    if len(st.session_state.df) > 300:
        st.session_state.df = st.session_state.df.iloc[-300:]


# ---------------------------------------
# WEBSOCKET RUNNER
# ---------------------------------------
def run_ws():
    ws = websocket.WebSocketApp(
        "wss://stream.binance.com:9443/ws/dogeusdt@trade",
        on_message=on_message
    )
    ws.run_forever()


# jalankan WebSocket sekali saja
if "ws_started" not in st.session_state:
    t = threading.Thread(target=run_ws)
    t.daemon = True
    t.start()
    st.session_state.ws_started = True


# ---------------------------------------
# UI PLACEHOLDERS
# ---------------------------------------
col1, col2, col3 = st.columns(3)
ph_price = col1.empty()
ph_change = col2.empty()
ph_highlow = col3.empty()
ph_chart = st.empty()


# ---------------------------------------
# NON-BLOCKING UI UPDATE
# ---------------------------------------
def update_ui():

    df = st.session_state.df

    if len(df) > 2:
        curr = st.session_state.current_price
        prev = st.session_state.prev_price

        # indikator
        if curr > prev:
            color = "green"
            arrow = "▲"
        elif curr < prev:
            color = "red"
            arrow = "▼"
        else:
            color = "white"
            arrow = "▬"

        # harga
        ph_price.markdown(
            f"""
            <h3 style='color:#bbb;'>Harga Sekarang</h3>
            <h1 style='color:{color};'>{arrow} {curr:.6f} USDT</h1>
            """,
            unsafe_allow_html=True
        )

        # persen perubahan
        try:
            p_change = ((curr - prev) / prev) * 100
        except:
            p_change = 0

        ph_change.markdown(
            f"""
            <h3 style='color:#bbb;'>% Perubahan</h3>
            <h1 style='color:{color};'>{p_change:.4f}%</h1>
            """,
            unsafe_allow_html=True
        )

        # high low session
        ph_highlow.markdown(
            f"""
            <h3 style='color:#bbb;'>High - Low</h3>
            <h4 style='color:#0ff;'>High : {df.price.max():.6f}</h4>
            <h4 style='color:#fa0;'>Low : {df.price.min():.6f}</h4>
            """,
            unsafe_allow_html=True
        )

        # grafik
        ph_chart.line_chart(df, x="time", y="price")


# Loop update UI tanpa blocking
for i in range(10000):
    update_ui()
    time.sleep(0.5)
    st.experimental_rerun()
