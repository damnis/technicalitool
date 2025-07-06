import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import streamlit as st  # nodig voor caching

# ✅ Slimme intervalkiezer op basis van gekozen periode
def bepaal_interval(periode):
    if periode in ["1d", "5d"]:
        return "15m"
    elif periode in ["1mo", "3mo"]:
        return "1h"
    elif periode in ["6mo", "1y", "ytd"]:
        return "1d"
    elif periode in ["3y", "5y"]:
        return "1wk"
    else:  # "10y", "max"
        return "1mo"

# ✅ Gecachete functie voor data-ophaal (TTL 15 min)
@st.cache_data(ttl=900)
def fetch_chart_data(ticker, periode):
    interval = bepaal_interval(periode)
    df = yf.download(ticker, period=periode, interval=interval)

    if df.empty or "Close" not in df.columns:
        return pd.DataFrame()

    df.index = pd.to_datetime(df.index)
    df = df[~df.index.isna()]

    # MA & Bollinger berekenen
    df["MA20"] = df["Close"].rolling(window=20).mean()
    df["MA50"] = df["Close"].rolling(window=50).mean()
    df["MA200"] = df["Close"].rolling(window=200).mean()

    df["BB_middle"] = df["Close"].rolling(window=20).mean()
    df["BB_std"] = df["Close"].rolling(window=20).std()
    df["BB_upper"] = df["BB_middle"] + 2 * df["BB_std"]
    df["BB_lower"] = df["BB_middle"] - 2 * df["BB_std"]

    return df.dropna()

# ✅ Teken candlestick-grafiek met overlays
def draw_candlestick_chart(df, ticker, selected_lines):
    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        name="Candlestick"
    ))

    if "MA20" in selected_lines:
        fig.add_trace(go.Scatter(x=df.index, y=df["MA20"], mode="lines", name="MA 20"))
    if "MA50" in selected_lines:
        fig.add_trace(go.Scatter(x=df.index, y=df["MA50"], mode="lines", name="MA 50"))
    if "MA200" in selected_lines:
        fig.add_trace(go.Scatter(x=df.index, y=df["MA200"], mode="lines", name="MA 200"))
    if "Bollinger Bands" in selected_lines:
        fig.add_trace(go.Scatter(x=df.index, y=df["BB_upper"], mode="lines", name="BB Upper", line=dict(dash="dot")))
        fig.add_trace(go.Scatter(x=df.index, y=df["BB_lower"], mode="lines", name="BB Lower", line=dict(dash="dot")))

    fig.update_layout(
        title=f"📈 Koersgrafiek: {ticker}",
        xaxis_title="Datum",
        yaxis_title="Prijs",
        xaxis_rangeslider_visible=False,
        template="plotly_white",
        height=600
    )

    return fig
