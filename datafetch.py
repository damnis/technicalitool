import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# 🔁 Slimme intervalkeuze obv periode
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

# ✅ Caching van volledige dataset (candlestick + overlays)
@st.cache_data(ttl=900)
def fetch_data(ticker, periode):
    interval = bepaal_interval(periode)
    df = yf.download(ticker, period=periode, interval=interval, group_by="ticker")

    if df.empty:
        return pd.DataFrame()

    # Flatten kolommen als nodig
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df.index = pd.to_datetime(df.index, errors="coerce")
    df = df[~df.index.isna()]

    # MA & Bollinger
    df["MA20"] = df["Close"].rolling(20, min_periods=1).mean()
    df["MA50"] = df["Close"].rolling(50, min_periods=1).mean()
    df["MA200"] = df["Close"].rolling(200, min_periods=1).mean()
    df["BB_middle"] = df["Close"].rolling(20, min_periods=1).mean()
    df["BB_std"] = df["Close"].rolling(20, min_periods=1).std()
    df["BB_upper"] = df["BB_middle"] + 2 * df["BB_std"]
    df["BB_lower"] = df["BB_middle"] - 2 * df["BB_std"]

    return df

# ✅ Custom candlestick-plotter
def draw_custom_candlestick_chart(df, ticker="", selected_lines=[]):
    fig = go.Figure()

    for i in range(len(df)):
        # Wick (Low - High)
        fig.add_trace(go.Scatter(
            x=[df.index[i], df.index[i]],
            y=[df["Low"][i], df["High"][i]],
            mode="lines",
            line=dict(color="gray", width=1),
            showlegend=False,
            hoverinfo='skip'
        ))

        # Body (Open - Close)
        kleur = "green" if df["Close"][i] > df["Open"][i] else "red"
        fig.add_trace(go.Scatter(
            x=[df.index[i], df.index[i]],
            y=[df["Open"][i], df["Close"][i]],
            mode="lines",
            line=dict(color=kleur, width=6),
            showlegend=False,
            hoverinfo="text",
            text=f"Open: {df['Open'][i]:.2f}<br>Close: {df['Close'][i]:.2f}"
        ))

    # Overlay lijnen
    if not df.empty:
        if "MA20" in selected_lines:
            fig.add_trace(go.Scatter(x=df.index, y=df["MA20"], mode="lines", name="MA 20"))
        if "MA50" in selected_lines:
            fig.add_trace(go.Scatter(x=df.index, y=df["MA50"], mode="lines", name="MA 50"))
        if "MA200" in selected_lines:
            fig.add_trace(go.Scatter(x=df.index, y=df["MA200"], mode="lines", name="MA 200"))
        if "Bollinger Bands" in selected_lines:
            fig.add_trace(go.Scatter(x=df.index, y=df["BB_upper"], mode="lines", name="BB Upper", line=dict(dash="dot")))
            fig.add_trace(go.Scatter(x=df.index, y=df["BB_lower"], mode="lines", name="BB Lower", line=dict(dash="dot")))

    # Layout
    fig.update_layout(
        title=f"📊 Aangepaste Candlestick-grafiek: {ticker}",
        xaxis_title="Datum",
        yaxis_title="Prijs",
        xaxis_rangeslider_visible=False,
        template="plotly_white",
        height=600
    )

    return fig





















# wit
