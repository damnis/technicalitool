import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import plotly.graph_objs as go
from datetime import datetime, timedelta
from datafetch import fetch_data, draw_custom_candlestick_chart, search_ticker


st.set_page_config(page_title="📈 Technicalitool", layout="wide")
st.title("📈 Technicalitool - Technische Analyse voor Aandelen")

# 🔍 Ticker input
zoekterm = st.text_input("🔍 Zoek op naam of ticker", value="AAPL").strip()

suggesties = search_ticker(zoekterm)

if suggesties:
    ticker_opties = [f"{sym} - {naam}" for sym, naam in suggesties]
    selectie = st.selectbox("Kies ticker", ticker_opties, index=0)
    query = selectie.split(" - ")[0]  # extract ticker
else:
    st.warning("⚠️ Geen resultaten gevonden.")
    query = ""
    
#query = st.text_input("Zoek op naam of ticker (bijv. Apple of AAPL)", value="AAPL").upper().strip()

# 📅 Periode selectie
st.markdown("### Periode")
periode_keuze = st.selectbox("Kies standaardperiode", [
    "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "3y", "5y", "10y", "ytd", "max"
], index=5)
vanaf = st.date_input("Startdatum", datetime.today() - timedelta(days=365))
tot = st.date_input("Einddatum", datetime.today())

# 📏 Overlay indicatoren
st.markdown("### Overlay Indicatoren")
overlay_lijnen = st.multiselect(
    "Selecteer lijnen op grafiek", ["MA20", "MA50", "MA200", "Bollinger Bands"], default=["MA20"]
)

# 📉 Onderliggende grafieken
st.markdown("### Onderliggende Indicatoren")
onder_grafiek = st.multiselect("Kies extra grafieken", ["Volume", "MACD", "RSI"], default=["Volume"])

# ✅ Data ophalen en tonen
if query:
    df = fetch_data(query, periode_keuze)

    if not df.empty:
        st.success(f"✅ Gegevens opgehaald: {len(df)} datapunten")

        # 📋 Tabel bovenaan
        with st.expander("📋 Laatste 100 koersregels"):
            toon_aantal = st.radio("Aantal rijen tonen:", [20, 50, 100], horizontal=True)
            df_display = df.tail(toon_aantal).copy()

            for kolom in ["Close", "Open", "High", "Low"]:
                if kolom in df_display.columns:
                    df_display[kolom] = df_display[kolom].round(2)

            st.dataframe(df_display)

        # 📈 Candlestick-grafiek met overlay
        fig = draw_custom_candlestick_chart(df, query, overlay_lijnen)
        st.plotly_chart(fig, use_container_width=True)

        # 📉 Extra grafiek onder candlestick
        if "Volume" in onder_grafiek:
            st.subheader("📉 Volume")
            vol_fig = go.Figure()
            vol_fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume'))
            vol_fig.update_layout(height=200, margin=dict(l=20, r=20, t=20, b=20), template="plotly_white")
            st.plotly_chart(vol_fig, use_container_width=True)

        ## 📋 Koersdata (kleur per kolom)
        st.markdown("### 📋 Koersdata (kleur per kolom)")
        if st.toggle("Toon laatste 100 regels"):
            df_tail = df.tail(100).copy()
        else:
            df_tail = df.tail(20).copy()

        # 🔢 Afronden alle numerieke kolommen op 3 decimalen
        for col in df_tail.select_dtypes(include=["float", "int"]).columns:
            df_tail[col] = df_tail[col].round(3)

        # 🎨 Kleur per koerskolom (alleen Open, High, Low, Close)
        def kleur_koers_kolom(series):
            kleuren = []
            for i in range(len(series)):
                if i + 1 < len(series):
                    if series.iloc[i] > series.iloc[i + 1]:
                        kleuren.append('color: green')
                    elif series.iloc[i] < series.iloc[i + 1]:
                        kleuren.append('color: red')
                    else:
                        kleuren.append('color: gray')
                else:
                    kleuren.append('color: gray')
            return kleuren

        # 🖌️ Stijl toepassen
        styled_df = df_tail.style
        for kolom in ["Open", "High", "Low", "Close"]:
            if kolom in df_tail.columns:
                styled_df = styled_df.apply(kleur_koers_kolom, subset=[kolom])

        # 🖥️ Tabel tonen
        st.dataframe(styled_df, use_container_width=True)












# wit
