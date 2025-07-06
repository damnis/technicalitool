import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

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

# ✅ Caching van overlay-data (indicatoren zoals MA/Bollinger)
@st.cache_data(ttl=900)
def fetch_chart_data(ticker, periode):
    interval = bepaal_interval(periode)
    df = yf.download(ticker, period=periode, interval=interval)

    if df.empty or "Close" not in df.columns:
        return pd.DataFrame()

    # Datumindex wél omzetten (voor indicators correctheid)
    df.index = pd.to_datetime(df.index, errors="coerce")
    df = df[~df.index.isna()]

    # Indicatoren
    df["MA20"] = df["Close"].rolling(window=20, min_periods=1).mean()
    df["MA50"] = df["Close"].rolling(window=50, min_periods=1).mean()
    df["MA200"] = df["Close"].rolling(window=200, min_periods=1).mean()

    df["BB_middle"] = df["Close"].rolling(window=20, min_periods=1).mean()
    df["BB_std"] = df["Close"].rolling(window=20, min_periods=1).std()
    df["BB_upper"] = df["BB_middle"] + 2 * df["BB_std"]
    df["BB_lower"] = df["BB_middle"] - 2 * df["BB_std"]

    return df

# ✅ Candlestick-data apart en ongefilterd (voor raw x-as)
@st.cache_data(ttl=900)
def fetch_raw_candlestick_data(ticker, periode):
    interval = bepaal_interval(periode)
    df = yf.download(ticker, period=periode, interval=interval)

    if df.empty or "Close" not in df.columns:
        return pd.DataFrame()

    return df  # géén datetime conversie op index!

# ✅ Teken candlestick-grafiek met overlays
def draw_candlestick_chart(candle_df, overlay_df, ticker, selected_lines):
    fig = go.Figure()

    # Candlestick trace (ruwe data)
    fig.add_trace(go.Candlestick(
        x=candle_df.index,
        open=candle_df["Open"],
        high=candle_df["High"],
        low=candle_df["Low"],
        close=candle_df["Close"],
        name="Candlestick"
    ))

    # Overlay indicators (berekend uit overlay_df met datetime index)
    if not overlay_df.empty:
        if "MA20" in selected_lines:
            fig.add_trace(go.Scatter(x=overlay_df.index, y=overlay_df["MA20"], mode="lines", name="MA 20"))
        if "MA50" in selected_lines:
            fig.add_trace(go.Scatter(x=overlay_df.index, y=overlay_df["MA50"], mode="lines", name="MA 50"))
        if "MA200" in selected_lines:
            fig.add_trace(go.Scatter(x=overlay_df.index, y=overlay_df["MA200"], mode="lines", name="MA 200"))
        if "Bollinger Bands" in selected_lines:
            fig.add_trace(go.Scatter(x=overlay_df.index, y=overlay_df["BB_upper"], mode="lines", name="BB Upper", line=dict(dash="dot")))
            fig.add_trace(go.Scatter(x=overlay_df.index, y=overlay_df["BB_lower"], mode="lines", name="BB Lower", line=dict(dash="dot")))

    # Layout
    fig.update_layout(
        title=f"📈 Koersgrafiek: {ticker}",
        xaxis_title="Datum",
        yaxis_title="Prijs",
        xaxis_rangeslider_visible=False,
        template="plotly_white",
        height=600
    )

    return fig



















# wit
