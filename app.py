import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objs as go
from datetime import datetime, timedelta

st.set_page_config(page_title="📈 Technicalitool", layout="wide")
st.title("📈 Technicalitool - Technische Analyse voor Aandelen")

# Keuze ticker
query = st.text_input("🔍 Zoek op naam of ticker (bijv. Apple of AAPL)", value="AAPL").upper().strip()

# Periode selectie
st.markdown("### Periode")
periode_keuze = st.selectbox("Kies standaardperiode", ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"], index=5)
vanaf = st.date_input("Startdatum", datetime.today() - timedelta(days=365))
tot = st.date_input("Einddatum", datetime.today())

# Indicator keuzes
st.markdown("### Overlay Indicatoren")
overlay_lijnen = st.multiselect("Selecteer lijnen op grafiek", ["Candlestick", "MA20", "MA50", "MA200", "Bollinger"], default=["MA20"])

st.markdown("### Onderliggende Indicatoren")
onder_grafiek = st.multiselect("Kies extra grafieken", ["Volume", "MACD", "RSI"], default=["Volume"])

# Gegevens ophalen
@st.cache_data(ttl=3600)
def get_data(ticker, periode, start, end):
    try:
        data = yf.download(ticker, period=periode)
        data_custom = yf.download(ticker, start=start, end=end)
        return data, data_custom
    except:
        return None, None

if query:
    ticker = query
    data, data_custom = get_data(query, periode_keuze, vanaf, tot)

    if data is not None and not data.empty:
        df = data.copy()

        # Bereken indicatoren indien nodig
        if "MA20" in overlay_lijnen:
            df["MA20"] = df["Close"].rolling(window=20).mean()
        if "MA50" in overlay_lijnen:
            df["MA50"] = df["Close"].rolling(window=50).mean()
        if "MA200" in overlay_lijnen:
            df["MA200"] = df["Close"].rolling(window=200).mean()
        if "Bollinger" in overlay_lijnen:
            ma20 = df["Close"].rolling(window=20).mean()
            std20 = df["Close"].rolling(window=20).std()
            df["BB_upper"] = ma20 + 2 * std20
            df["BB_lower"] = ma20 - 2 * std20

        # 📊 Candlestick-grafiek met overlays
        fig = go.Figure()

        # Voeg candlestick toe
        df.index = pd.to_datetime(df.index)  # altijd even expliciet zetten

        fig.add_trace(go.Candlestick(
            x=df.index.strftime("%Y-%m-%d"),  # werkt op Streamlit/Plotly Cloud
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="Candlestick"
        ))

        # Voeg overlays toe
        if "MA20" in overlay_lijnen:
            fig.add_trace(go.Scatter(x=df.index, y=df["MA20"], mode="lines", name="MA 20"))
        if "MA50" in overlay_lijnen:
            fig.add_trace(go.Scatter(x=df.index, y=df["MA50"], mode="lines", name="MA 50"))
        if "MA200" in overlay_lijnen:
            fig.add_trace(go.Scatter(x=df.index, y=df["MA200"], mode="lines", name="MA 200"))
        if "Bollinger" in overlay_lijnen:
            fig.add_trace(go.Scatter(x=df.index, y=df["BB_upper"], mode="lines", name="BB Upper", line=dict(dash="dot")))
            fig.add_trace(go.Scatter(x=df.index, y=df["BB_lower"], mode="lines", name="BB Lower", line=dict(dash="dot")))

        # Grafiek opmaak
        fig.update_layout(
            title=f"📈 Koersgrafiek: {ticker}",
            xaxis_title="Datum",
            yaxis_title="Prijs",
            xaxis_rangeslider_visible=False,
            template="plotly_white",
            height=600
        )

        st.plotly_chart(fig, use_container_width=True)
        

        
        # Extra grafieken
        if "Volume" in onder_grafiek:
            st.subheader("📉 Volume")
            vol_fig = go.Figure()
            vol_fig.add_trace(go.Bar(x=data.index, y=data['Volume'], name='Volume'))
            vol_fig.update_layout(height=200, margin=dict(l=20, r=20, t=20, b=20), template="plotly_white")
            st.plotly_chart(vol_fig, use_container_width=True)

        # Tabel kort en lang
        st.markdown("### 📋 Koersdata (laatste 20 / alle 100)")
        if st.toggle("Toon laatste 100 regels"):
            df = data_custom.tail(100)
        else:
            df = data_custom.tail(20)

        def kleur_koers(val, col):
            try:
                idx = val.name
                next_idx = df.index[df.index.get_loc(idx) + 1] if df.index.get_loc(idx) + 1 < len(df.index) else None
                if next_idx:
                    if df.at[idx, col] > df.at[next_idx, col]:
                        return 'color: green'
                    elif df.at[idx, col] < df.at[next_idx, col]:
                        return 'color: red'
                    else:
                        return 'color: gray'
            except:
                return ''
            return ''

        styled_df = df.style.applymap(lambda v: 'color: gray', subset=["Open", "High", "Low", "Close"])
        for col in ["Open", "High", "Low", "Close"]:
            styled_df = styled_df.apply(lambda s: [kleur_koers(s, col) for _ in s], subset=[col])

        st.dataframe(styled_df, use_container_width=True)

    else:
        st.warning("❌ Ticker niet gevonden of geen data beschikbaar.")
