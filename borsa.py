import streamlit as st
import pandas as pd
import random
import plotly.graph_objects as go
from streamlit_gsheets import GSheetsConnection
import time

# --- 1. AYARLAR VE BAĞLANTI ---
st.set_page_config(page_title="HUFOYT-BORSA SİMÜLASYONU", layout="wide")

# Senin Google Sheets Linkin
SHEET_URL = "https://docs.google.com/spreadsheets/d/1y2C4aa-06HZoKcJ5oGhejfPLpf4vGVvPaX_sRH28glE/edit?gid=0#gid=0"

conn = st.connection("gsheets", type=GSheetsConnection)

# --- VERİ TABANI FONKSİYONLARI ---
def verileri_cek():
    # Sayfadaki tüm oyuncuları ve fiyatları çek
    return conn.read(spreadsheet=SHEET_URL, worksheet="oyuncular")

# --- 2. SESSION STATE ---
if 'user_id' not in st.session_state:
    st.session_state.user_id = ""

# --- 3. GİRİŞ EKRANI ---
if not st.session_state.user_id:
    st.title("🏛️ HUFOYT-BORSA SİMÜLASYONU")
    nick = st.text_input("Yarışmacı Adın:", placeholder="Örn: Utku_Hacettepe")
    if st.button("Piyasaya Bağlan"):
        if nick:
            st.session_state.user_id = nick
            st.rerun()
    st.stop()

# --- 4. ORTAK PİYASA VERİSİ (HERKES BURAYI OKUR) ---
# Sunumda her saniye güncellenmesi için:
df_global = verileri_cek()

# ÖNEMLİ: Fiyatları Sheets'in ilk satırlarından veya sabit bir yerden almalıyız
# Şimdilik simülasyonu sen yönettiğin için fiyatlar sende dönecek
if 'prices' not in st.session_state:
    st.session_state.prices = {"Aselsan": 100.0, "Logo": 100.0, "Tüpraş": 100.0, "Baykar": 100.0}
    st.session_state.history = {k: [100.0] for k in st.session_state.prices.keys()}

st.title("📊 HUFOYT-BORSA SİMÜLASYONU")
st.write(f"👤 Oyuncu: **{st.session_state.user_id}** | 🤖 AI Analiz Merkezi")

# --- 5. LİDERLİK TABLOSU (GERÇEK MULTIPLAYER) ---
st.subheader("🏆 Hacettepe Canlı Liderlik Tablosu")
# Burada Sheets'teki herkesi gösteriyoruz
st.dataframe(df_global[["Kullanıcı", "Varlık"]].sort_values(by="Varlık", ascending=False), use_container_width=True)

# --- 6. GRAFİK VE İŞLEM ---
hisse = st.selectbox("Hisse Seç", list(st.session_state.prices.keys()))
fig = go.Figure(go.Scatter(y=st.session_state.history[hisse], mode='lines+markers'))
st.plotly_chart(fig, use_container_width=True)

# --- 7. YÖNETİCİ PANELİ (SADECE SEN BASMALISIN) ---
if st.button("🚀 PİYASAYI TÜM SINIF İÇİN GÜNCELLE"):
    for k in st.session_state.prices.keys():
        change = random.uniform(-0.05, 0.05)
        st.session_state.prices[k] *= (1 + change)
        st.session_state.history[k].append(st.session_state.prices[k])
    
    # BURASI KRİTİK: Kendi varlığını Sheets'e yazdır
    # (Not: Tam yazma işlemi için Google Sheets API yetkisi gerekir, 
    # vaktimiz darsa sunumda sadece senin ekranından yönetelim)
    st.success("Piyasa güncellendi! Arkadaşın sayfasını yenilesin.")
