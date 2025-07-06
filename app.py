
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import date, timedelta

st.set_page_config(page_title="📈 Technicalitool", layout="wide")
st.title("📈 Technicalitool – Technische Analyse App")

def load_data(ticker, period):
    try:
        data = yf.download(ticker, period=period)
        if data.empty:
            return None
        data.reset_index(inplace=True)
        return data
    except:
        return None

def plot_candlestick(data, show_ma):
    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=data["Date"],
        open=data["Open"],
        high=data["High"],
        low=data["Low"],
        close=data["Close"],
        name="Candlestick"
    ))

    if "MA20" in show_ma:
        data["MA20"] = data["Close"].rolling(window=20).mean()
        fig.add_trace(go.Scatter(x=data["Date"], y=data["MA20"], mode="lines", name="MA20"))
    if "MA50" in show_ma:
        data["MA50"] = data["Close"].rolling(window=50).mean()
        fig.add_trace(go.Scatter(x=data["Date"], y=data["MA50"], mode="lines", name="MA50"))
    if "MA200" in show_ma:
        data["MA200"] = data["Close"].rolling(window=200).mean()
        fig.add_trace(go.Scatter(x=data["Date"], y=data["MA200"], mode="lines", name="MA200"))

    fig.update_layout(xaxis_rangeslider_visible=False, height=600)
    return fig

ticker = st.text_input("🎯 Voer een ticker in (bijv. AAPL, MSFT)", value="AAPL").upper().strip()
period = st.selectbox("📅 Kies een periode", ["1mo", "3mo", "6mo", "ytd", "1y", "5y", "max"])
show_ma = st.multiselect("📊 Toon moving averages", ["MA20", "MA50", "MA200"], default=["MA20", "MA50"])

if ticker:
    with st.spinner("📡 Data ophalen..."):
        data = load_data(ticker, period)
    if data is not None:
        st.plotly_chart(plot_candlestick(data, show_ma), use_container_width=True)
        st.dataframe(data.set_index("Date")[["Open", "High", "Low", "Close", "Volume"]].tail(20))
    else:
        st.error("⚠️ Geen geldige data gevonden. Controleer de ticker of probeer een andere periode.")
