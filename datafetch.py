import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
import matplotlib.pyplot as plt
from ta.trend import ADXIndicator

# geknipt uit app.py, oude wijze van ophalen data (verplaatst naar datafetch.py)
@st.cache_data(ttl=3600)
def get_data(ticker, periode, start, end):
    try:
        data = yf.download(ticker, period=periode)
        data_custom = yf.download(ticker, start=start, end=end)
        return data, data_custom
    except:
        return None, None


#--- Verbeterde Functie om data op te halen ---
# ✅ Gecachete downloadfunctie (15 minuten geldig)
@st.cache_data(ttl=900)
def fetch_data_cached(ticker, interval, period):
    return yf.download(ticker, interval=interval, period=period)

# ✅ Weighted Moving Average functie
def weighted_moving_average(series, window):
    weights = np.arange(1, window + 1)
    return series.rolling(window).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)

# ✅ Wrapper-functie met dataschoonmaak en fallback
def fetch_data(ticker, interval):
    # 🔁 Interval naar periode
    if interval == "15m":
        period = "30d"
    elif interval == "1h":
        period = "720d"
    elif interval == "4h":
        period = "360d"
    elif interval == "1d":
        period = "20y"
    elif interval == "1wk":
        period = "20y"
    elif interval == "1mo":
        period = "25y"
    else:
        period = "25y"  # fallback

    # ⬇️ Ophalen via gecachete functie
    df = fetch_data_cached(ticker, interval, period)

    # 🛡️ Check op geldige data
    if df.empty or "Close" not in df.columns or "Open" not in df.columns:
        return pd.DataFrame()

    # 🧹 Verwijder irrelevante of foutieve rijen
    df = df[
        (df["Volume"] > 0) &
        ((df["Open"] != df["Close"]) | (df["High"] != df["Low"]))
    ]

    # 🕓 Zorg dat index datetime is
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index, errors="coerce")
    df = df[~df.index.isna()]

    # 🔁 Vul NaN's per kolom
    for col in ["Close", "Open", "High", "Low", "Volume"]:
        df[col] = df[col].fillna(method="ffill").fillna(method="bfill")

    # 🧪 Check minimale lengte
    if len(df) < 30:
        st.warning(f"⚠️ Slechts {len(df)} datapunten opgehaald — mogelijk te weinig voor indicatoren.")
        return pd.DataFrame()

    return df



# 📆 Periode voor candlestick-grafiek op basis van realtime
def bepaal_grafiekperiode(interval):
    if interval == "15m":
        return timedelta(days=7)        # 7 dagen à ~96 candles per dag = ±672 punten
    elif interval == "1h":
        return timedelta(days=5)        # 5 dagen à ~7 candles = ±35 punten
    elif interval == "4h":
        return timedelta(days=90)       # 3 maanden à ~6 candles per week
    elif interval == "1d":
        return timedelta(days=720)      # 180=6 maanden à 1 candle per dag
    elif interval == "1wk":
        return timedelta(weeks=150)     # 104=2 jaar aan weekly candles (104 candles)
    elif interval == "1mo":
        return timedelta(weeks=520)     # 520=0 jaar aan monthly candles (120 candles)
    else:
        return timedelta(weeks=260)     # Fallback = 5 jaar

































# wit
    
