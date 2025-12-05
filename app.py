import streamlit as st
import pandas as pd
import requests
import time
import plotly.graph_objects as go

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(page_title="Crypto Trend Realtime", layout="wide")

st.title("📈 Real-Time Crypto Price Trend")
st.write("Monitoring harga crypto menggunakan CoinGecko API (Realtime 1 detik, tanpa API Key).")

# -------------------------
# THEME MODE SWITCH
# -------------------------
mode = st.radio("Pilih Mode Tampilan:", ["🌞 Mode Siang", "🌙 Mode Malam"], horizontal=True)

if mode == "🌙 Mode Malam":
    bg_color = "#0d1117"
    text_color = "#e6edf3"
    card_color = "#161b22"
else:
    bg_color = "#ffffff"
    text_color = "#000000"
    card_color = "#f2f2f2"

# Apply global style
st.markdown(
    f"""
    <style>
        body {{
            background-color: {bg_color};
            color: {text_color};
        }}
        .stMarkdown, .stRadio, .stSelectbox, .stTitle, p, h1, h2, h3 {{
            color: {text_color} !important;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------
# PILIH CRYPTO
# -------------------------
crypto = st.selectbox(
    "Pilih Cryptocurrency:",
    ["bitcoin", "ethereum", "binancecoin", "dogecoin", "solana", "cardano", "ripple"]
)

st.write(f"Menampilkan trend harga **{crypto.capitalize()}** terhadap USD.")

# -------------------------
# SESSION STATE
# -------------------------
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=["time", "price"])

placeholder_price = st.empty()
placeholder_line = st.empty()
placeholder_area = st.empty()
placeholder_spark = st.empty()

# -------------------------
# GET PRICE (CoinGecko)
# -------------------------
def get_price(coin):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"
        r = requests.get(url, timeout=5)
        data = r.json()
        return float(data[coin]["usd"])
    except:
        return None

# -------------------------
# FETCH PRICE
# -------------------------
price = get_price(crypto)

if price is not None:
    now = pd.Timestamp.now()
    st.session_state.df.loc[len(st.session_state.df)] = [now, price]

    # batas data agar ringan
    if len(st.session_state.df) > 400:
        st.session_state.df = st.session_state.df.iloc[-400:]

    # -------------------------
    # DISPLAY PRICE
    # -------------------------
    placeholder_price.markdown(
        f"""
        <div style="padding:15px; border-radius:10px; background-color:{card_color};">
            <h2 style="color:{text_color};">💰 Harga Terbaru: {price:.5f} USD</h2>
            <p style="color:{text_color};">⏳ Auto refresh setiap 1 detik</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    df = st.session_state.df

    # -------------------------
    # LINE CHART (Utama)
    # -------------------------
    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=df["time"], y=df["price"],
        mode="lines",
        line=dict(width=3, color="#00ccff"),
        name="Price",
    ))
    fig_line.update_layout(
        title="📌 Trend Harga (Line Chart)",
        template="plotly_dark" if mode == "🌙 Mode Malam" else "plotly_white",
        height=350,
    )
    placeholder_line.plotly_chart(fig_line, use_container_width=True)

    # -------------------------
    # AREA CHART (Lebih Menarik)
    # -------------------------
    fig_area = go.Figure()
    fig_area.add_trace(go.Scatter(
        x=df["time"], y=df["price"],
        mode="lines",
        fill="tozeroy",
        line=dict(color="#00ff88", width=2),
        name="Price Area",
    ))
    fig_area.update_layout(
        title="🌄 Trend Area (Soft Gradient)",
        template="plotly_dark" if mode == "🌙 Mode Malam" else "plotly_white",
        height=300,
    )
    placeholder_area.plotly_chart(fig_area, use_container_width=True)

    # -------------------------
    # MINI SPARKLINE (Mini Chart)
    # -------------------------
    fig_spark = go.Figure()
    fig_spark.add_trace(go.Scatter(
        x=df["time"], y=df["price"],
        mode="lines",
        line=dict(color="#ffaa00", width=2),
        name="Sparkline",
    ))
    fig_spark.update_layout(
        title="✨ Sparkline Mini Chart",
        template="plotly_dark" if mode == "🌙 Mode Malam" else "plotly_white",
        height=180,
        margin=dict(l=20, r=20, t=30, b=20)
    )
    placeholder_spark.plotly_chart(fig_spark, use_container_width=True)

else:
    placeholder_price.error("Tidak bisa mengambil harga. API CoinGecko sedang padat.")

# -------------------------
# AUTO REFRESH
# -------------------------
time.sleep(1)
st.experimental_set_query_params(refresh=str(time.time()))
