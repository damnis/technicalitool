# 📊 Tabel met toggle (nu bovenaan)
if not overlay_df.empty and not candle_df.empty:
    st.success(f"✅ Gegevens opgehaald: {len(candle_df)} datapunten")

    with st.expander("📋 Laatste 100 koersregels"):
        toon_aantal = st.radio("Aantal rijen tonen:", [20, 50, 100], horizontal=True)
        df_display = overlay_df.tail(toon_aantal).copy()

        # 🎨 Kleur op koersbeweging
        for kolom in ["Close", "Open", "High", "Low"]:
            if kolom in df_display.columns:
                df_display[kolom] = df_display[kolom].round(2)

        st.dataframe(df_display)

    # 📈 Candlestick-grafiek direct onder tabel
    fig = draw_candlestick_chart(candle_df, overlay_df, query, overlay_lijnen)
    st.plotly_chart(fig, use_container_width=True)

    # 📉 Extra grafiek direct onder koersgrafiek
    if "Volume" in onder_grafiek:
        st.subheader("📉 Volume")
        vol_fig = go.Figure()
        vol_fig.add_trace(go.Bar(x=candle_df.index, y=candle_df['Volume'], name='Volume'))
        vol_fig.update_layout(height=200, margin=dict(l=20, r=20, t=20, b=20), template="plotly_white")
        st.plotly_chart(vol_fig, use_container_width=True)

    # 📋 Koersdata opnieuw met kleuring toggle
    st.markdown("### 📋 Koersdata (kleur per kolom)")
    if st.toggle("Toon laatste 100 regels"):
        df = overlay_df.tail(100)
    else:
        df = overlay_df.tail(20)

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












 # wit




