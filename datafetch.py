import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import requests
import pandas_market_calendars as mcal

@st.cache_data(ttl=3600)
def search_ticker(query, fmp_api_key="D2MyI4eYNXDNJzpYT4N6nTQ2amVbJaG5"):
    query = query.upper().strip()

    # Probeer eerst of het een geldige yfinance-ticker is
    try:
        info = yf.Ticker(query).info
        if info and "regularMarketPrice" in info:
            naam = info.get("shortName") or info.get("longName") or query
            return [(query, naam)]
    except Exception:
        pass  # yfinance gaf geen geldige data terug

    # Als fallback → FMP doorzoeken
    try:
        url = f"https://financialmodelingprep.com/api/v3/search?query={query}&limit=50&apikey={fmp_api_key}"
        response = requests.get(url)
        data = response.json()
        resultaten = [(item["symbol"], item.get("name", item["symbol"])) for item in data]
        return resultaten
    except Exception as e:
        st.error(f"Fout bij ophalen FMP-tickers: {e}")
        return []

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
    st.write(f"📡 Ophalen data voor: {ticker} ({periode})")
    interval = bepaal_interval(periode)
    df = yf.download(ticker, period=periode, interval=interval)

    st.write("📊 Rijen vóór filtering:", len(df))

    if df.empty:
        return pd.DataFrame()

    # 🛡️ Fix voor MultiIndex zoals ('Close', 'AAPL')
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    if "Close" not in df.columns:
        st.warning(f"⚠️ 'Close'-kolom niet gevonden. Kolommen: {df.columns.tolist()}")
        return pd.DataFrame()

    df.index = pd.to_datetime(df.index, errors="coerce")
    df = df[~df.index.isna()]

    # 🔍 Bepaal type
    if ticker.upper().endswith("-USD"):
        st.write("🪙 Crypto ticker gedetecteerd")
    else:
        st.write("📈 Stock ticker gedetecteerd")
        try:
            cal = mcal.get_calendar("Euronext") if ticker.upper().endswith(".AS") else mcal.get_calendar("NYSE")
            schedule = cal.schedule().loc[df.index.min():df.index.max()]
            valid_days = schedule.index.tz_localize(None).normalize()
            df = df[df.index.normalize().isin(valid_days)]
            st.write("✅ Na beursdagenfilter:", len(df))
        except Exception as e:
            st.error(f"❌ Kalenderfout: {e}")
        
    # Indicatoren
    df["MA35"] = df["Close"].rolling(window=35, min_periods=1).mean()
    df["MA50"] = df["Close"].rolling(window=50, min_periods=1).mean()
    df["MA150"] = df["Close"].rolling(window=150, min_periods=1).mean()

    df["BB_middle"] = df["Close"].rolling(window=20, min_periods=1).mean()
    df["BB_std"] = df["Close"].rolling(window=20, min_periods=1).std()
    df["BB_upper"] = df["BB_middle"] + 2 * df["BB_std"]
    df["BB_lower"] = df["BB_middle"] - 2 * df["BB_std"]

    st.write("📉 Laatste datum in gefilterde data:", df.index[-1])
    return df

# ✅ Custom candlestick-plotter
def draw_custom_candlestick_chart(df, ticker="", selected_lines=[]):
    fig = go.Figure()

    for i in range(len(df)):
        kleur = "green" if df["Close"][i] > df["Open"][i] else "red"
        fig.add_trace(go.Scatter(
            x=[df.index[i], df.index[i]],
            y=[df["Low"][i], df["High"][i]],
            mode="lines",
            line=dict(color=kleur, width=1),
            showlegend=False,
            hoverinfo='skip'
        ))

        fig.add_trace(go.Scatter(
            x=[df.index[i], df.index[i]],
            y=[df["Open"][i], df["Close"][i]],
            mode="lines",
            line=dict(color=kleur, width=3),
            showlegend=False,
            hoverinfo="text",
            text=f"Open: {df['Open'][i]:.2f}<br>Close: {df['Close'][i]:.2f}"
        ))

    # Overlay lijnen
    if not df.empty:
        if "MA35" in selected_lines:
            fig.add_trace(go.Scatter(x=df.index, y=df["MA35"], mode="lines", name="MA 35"))
        if "MA50" in selected_lines:
            fig.add_trace(go.Scatter(x=df.index, y=df["MA50"], mode="lines", name="MA 50"))
        if "MA150" in selected_lines:
            fig.add_trace(go.Scatter(x=df.index, y=df["MA150"], mode="lines", name="MA 150"))
        if "Bollinger Bands" in selected_lines:
            fig.add_trace(go.Scatter(x=df.index, y=df["BB_upper"], mode="lines", name="BB Upper", line=dict(dash="dot")))
            fig.add_trace(go.Scatter(x=df.index, y=df["BB_lower"], mode="lines", name="BB Lower", line=dict(dash="dot")))

    fig.update_layout(
        title=f"📊 Aangepaste Candlestick-grafiek: {ticker}",
        xaxis_title="Datum",
        yaxis_title="Prijs",
        xaxis_rangeslider_visible=False,
        template="plotly_white",
        height=600,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
    )

    return fig















# wit
