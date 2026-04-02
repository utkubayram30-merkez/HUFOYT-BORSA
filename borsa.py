import streamlit as st
import pandas as pd
import random
import plotly.graph_objects as go

# --- 1. AYARLAR ---
st.set_page_config(page_title="HUFOYT-BORSA | Canlı Arena", layout="wide")

# Senin CSV linkin (Burada kalsın, liderlik tablosu için lazım)
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTgboIt-V17NgEk0YWa6s7_K3II40CpZoi5wR5Mm4cN4TbAGl_F1M5VCJw6dN9x_-OI36J8jtGucFEf/pub?output=csv"

# --- 2. SESSION STATE (BELLEK) ---
if 'prices' not in st.session_state:
    st.session_state.update({
        'prices': {"Aselsan": 100.0, "Logo": 100.0, "Tüpraş": 100.0, "Baykar": 100.0},
        'history': {"Aselsan": [100.0], "Logo": [100.0], "Tüpraş": [100.0], "Baykar": [100.0]},
        'round': 1,
        'user_id': "",
        'cash': 50000.0
    })

# --- 3. GİRİŞ EKRANI ---
if st.session_state.user_id == "":
    st.title("🏛️ HUFOYT-BORSA SİMÜLASYONU")
    st.subheader("Hacettepe Finansal Okuryazarlık Topluluğu")
    
    nick = st.text_input("Yarışmacı Adın (Nida / Utku):")
    if st.button("Piyasaya Bağlan"):
        if nick:
            st.session_state.user_id = nick
            st.success(f"Hoş geldin {nick}! Giriş yapılıyor...")
            st.rerun() # Sayfayı yenileyip içeri sokar
        else:
            st.error("Lütfen bir isim gir!")
else:
    # --- 4. ANA OYUN EKRANI (BAĞLANDIKTAN SONRA BURASI GÖRÜNÜR) ---
    st.title(f"📊 HUFOYT-BORSA | Canlı Piyasa")
    st.write(f"👤 Oyuncu: **{st.session_state.user_id}** | 💰 Bakiye: **{round(st.session_state.cash, 2)} TL**")

    # Liderlik Tablosu (Excel'den Canlı Çekim)
    with st.expander("🏆 Canlı Liderlik Tablosunu Gör"):
        try:
            df_leader = pd.read_csv(CSV_URL)
            st.table(df_leader)
        except:
            st.write("Liderlik tablosu şu an yüklenemedi.")

    # Grafik ve Tur Yönetimi
    hisse = st.selectbox("Hisse Seç", list(st.session_state.prices.keys()))
    fiyat = st.session_state.prices[hisse]
    
    fig = go.Figure(go.Scatter(y=st.session_state.history[hisse], mode='lines+markers', line=dict(color='#00FF00')))
    fig.update_layout(template="plotly_dark", height=300)
    st.plotly_chart(fig, use_container_width=True)

    if st.button("🚀 PİYASAYI OYNAT (HERKES İÇİN)"):
        for k in st.session_state.prices.keys():
            change = random.uniform(-0.08, 0.08)
            st.session_state.prices[k] *= (1 + change)
            st.session_state.history[k].append(st.session_state.prices[k])
        st.session_state.round += 1
        st.balloons()
        st.rerun()

    if st.button("Çıkış Yap"):
        st.session_state.user_id = ""
        st.rerun()
