import pandas as pd 
import plotly.graph_objects as go 
import streamlit as st 
import requests

FMP_API_KEY = "D2MyI4eYNXDNJzpYT4N6nTQ2amVbJaG5"

@st.cache_data(ttl=3600) def search_ticker(query): query = query.strip() try: url = f"https://financialmodelingprep.com/api/v3/search?query={query}&limit=100&apikey={FMP_API_KEY}" response = requests.get(url) data = response.json()

# Prioriteit aan tickers uit VS (NYSE/NASDAQ) met exacte of bijna-exacte match
    def sort_key(item):
        score = 0
        if item["symbol"].upper() == query.upper():
            score -= 10
        if query.lower() in item["name"].lower():
            score -= 5
        if item.get("exchangeShortName", "") in ["NASDAQ", "NYSE"]:
            score -= 2
        return score

    sorted_results = sorted(data, key=sort_key)
    resultaten = [(item["symbol"], item.get("name", item["symbol"])) for item in sorted_results]
    return resultaten
except Exception as e:
    st.error(f"Fout bij ophalen FMP-tickers: {e}")
    return []

@st.cache_data(ttl=900) def fetch_data(ticker, periode): st.write(f"📡 Ophalen data voor: {ticker} ({periode})") resolution = bepaal_interval(periode)

url = f"https://financialmodelingprep.com/api/v3/historical-chart/{resolution}/{ticker}?apikey={FMP_API_KEY}"
try:
    response = requests.get(url)
    data = response.json()
    df = pd.DataFrame(data)
    if df.empty or 'date' not in df.columns:
        return pd.DataFrame()

    df["date"] = pd.to_datetime(df["date"])
    df.set_index("date", inplace=True)
    df.sort_index(inplace=True)

    df = df.rename(columns={"open": "Open", "high": "High", "low": "Low", "close": "Close", "volume": "Volume"})

    df["MA35"] = df["Close"].rolling(window=35, min_periods=1).mean()
    df["MA50"] = df["Close"].rolling(window=50, min_periods=1).mean()
    df["MA150"] = df["Close"].rolling(window=150, min_periods=1).mean()

    df["BB_middle"] = df["Close"].rolling(window=20, min_periods=1).mean()
    df["BB_std"] = df["Close"].rolling(window=20, min_periods=1).std()
    df["BB_upper"] = df["BB_middle"] + 2 * df["BB_std"]
    df["BB_lower"] = df["BB_middle"] - 2 * df["BB_std"]

    st.write(f"✅ Gegevens opgehaald: {len(df)} datapunten")
    return df
except Exception as e:
    st.error(f"Fout bij ophalen koersdata: {e}")
    return pd.DataFrame()

def bepaal_interval(periode): if periode in ["1d", "5d"]: return "5min" elif periode in ["1mo", "3mo"]: return "30min" elif periode in ["6mo", "1y", "ytd"]: return "1hour" elif periode in ["3y", "5y"]: return "4hour" else: return "1day"

✅ Custom candlestick-plotter

def draw_custom_candlestick_chart(df, ticker="", selected_lines=[]): fig = go.Figure()

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

