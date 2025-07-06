import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="📈 Technicalitool", layout="wide")
st.title("📈 Technicalitool – Koersanalyse")

ticker = st.text_input("Voer een ticker in (bijv. AAPL)", value="AAPL").upper()
start_date = st.date_input("Startdatum", value=datetime(2024, 1, 1))
end_date = st.date_input("Einddatum", value=datetime.today())

if ticker:
    data = yf.download(ticker, start=start_date, end=end_date)
    if data.empty:
        st.error("Geen data gevonden voor deze ticker.")
    else:
        # Indicatoren
        data["MA20"] = data["Close"].rolling(window=20).mean()
        data["MA50"] = data["Close"].rolling(window=50).mean()

        # Plot candlestick met MA
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=data.index,
                                     open=data["Open"], high=data["High"],
                                     low=data["Low"], close=data["Close"],
                                     name="Candlestick"))

        fig.add_trace(go.Scatter(x=data.index, y=data["MA20"], name="MA20", line=dict(color="blue")))
        fig.add_trace(go.Scatter(x=data.index, y=data["MA50"], name="MA50", line=dict(color="red")))

        fig.update_layout(xaxis_rangeslider_visible=False, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

        # Toggle extra analyses
        with st.expander("📊 Technische data"):
            st.dataframe(data.tail(100).dropna().round(2))


