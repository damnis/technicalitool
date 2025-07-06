import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objs as go
from datetime import datetime, timedelta
from datafetch import fetch_data, draw_custom_candlestick_chart

st.set_page_config(page_title="📈 Technicalitool", layout="wide")
st.title("📈 Technicalitool - Technische Analyse voor Aandelen")

# 🔍 Ticker input
query = st.text_input("Zoek op naam of ticker (bijv. Apple of AAPL)", value="AAPL").upper().strip()

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

        # 📋 Kleurtabel onderaan
        st.markdown("### 📋 Koersdata (kleur per kolom)")
        if st.toggle("Toon laatste 100 regels"):
            df_tail = df.tail(100)
        else:
            df_tail = df.tail(20)

        def kleur_koers(val, col):
            try:
                idx = val.name
                next_idx = df_tail.index[df_tail.index.get_loc(idx) + 1] if df_tail.index.get_loc(idx) + 1 < len(df_tail.index) else None
                if next_idx:
                    if df_tail.at[idx, col] > df_tail.at[next_idx, col]:
                        return 'color: green'
                    elif df_tail.at[idx, col] < df_tail.at[next_idx, col]:
                        return 'color: red'
                    else:
                        return 'color: gray'
            except:
                return ''
            return ''

        styled_df = df_tail.style.applymap(lambda v: 'color: gray', subset=["Open", "High", "Low", "Close"])
        for col in ["Open", "High", "Low", "Close"]:
            styled_df = styled_df.apply(lambda s: [kleur_koers(s, col) for _ in s], subset=[col])

        st.dataframe(styled_df, use_container_width=True)

    else:
        st.warning("⚠️ Geen geldige data gevonden voor deze ticker of periode.")


















# wit
