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
overlay_lijnen = st.multiselect("Selecteer lijnen op grafiek", ["MA20", "MA50", "Bollinger Bands"], default=["MA20"])

st.markdown("### Onderliggende Indicatoren")
onder_grafiek = st.multiselect("Kies extra grafieken", ["Volume"], default=["Volume"])

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
    data, data_custom = get_data(query, periode_keuze, vanaf, tot)

    if data is not None and not data.empty:
        st.subheader(f"📊 Koersgrafiek: {query}")

        fig = go.Figure()

        # Candlestick
        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name='Candlestick'
        ))

        # Overlay lijnen
        if "MA20" in overlay_lijnen:
            data['MA20'] = data['Close'].rolling(window=20).mean()
            fig.add_trace(go.Scatter(x=data.index, y=data['MA20'], line=dict(width=1.5), name='MA20'))

        if "MA50" in overlay_lijnen:
            data['MA50'] = data['Close'].rolling(window=50).mean()
            fig.add_trace(go.Scatter(x=data.index, y=data['MA50'], line=dict(width=1.5), name='MA50'))

        if "Bollinger Bands" in overlay_lijnen:
            ma20 = data['Close'].rolling(window=20).mean()
            std20 = data['Close'].rolling(window=20).std()
            upper = ma20 + (2 * std20)
            lower = ma20 - (2 * std20)
            fig.add_trace(go.Scatter(x=data.index, y=upper, line=dict(width=1, dash='dot'), name='Bollinger Upper'))
            fig.add_trace(go.Scatter(x=data.index, y=lower, line=dict(width=1, dash='dot'), name='Bollinger Lower'))

        fig.update_layout(
            height=600,
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis_rangeslider_visible=False,
            template="plotly_white"
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