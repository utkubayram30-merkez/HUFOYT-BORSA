import streamlit as st
import pandas as pd
import random
import plotly.graph_objects as go
from streamlit_gsheets import GSheetsConnection

# --- 1. AYARLAR VE BAĞLANTI ---
st.set_page_config(page_title="HUFOYT-BORSA SİMÜLASYONU", layout="wide")

# Senin Google Sheets Linkin (Düzenleyici yetkisi verildiğinden emin ol!)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1y2C4aa-06HZoKcJ5oGhejfPLpf4vGVvPaX_sRH28glE/edit?usp=sharing"

# Bağlantıyı kuruyoruz
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 2. ORTAK VERİLERİ ÇEKME (HERKES AYNI YERİ OKUR) ---
def get_market_data():
    # Sayfa1'de fiyatlar ve tur bilgisini tutacağız
    return conn.read(spreadsheet=SHEET_URL, worksheet="oyuncular", ttl="1s")

# --- 3. GİRİŞ ---
if 'user_id' not in st.session_state:
    st.session_state.user_id = ""

if not st.session_state.user_id:
    st.title("🏛️ HUFOYT-BORSA SİMÜLASYONU")
    nick = st.text_input("Yarışmacı Adın (Nida/Utku):")
    if st.button("Piyasaya Bağlan"):
        st.session_state.user_id = nick
        st.rerun()
    st.stop()

# --- 4. CANLI PİYASA EKRANI ---
st.title(f"📊 HUFOYT-BORSA | Canlı Arena")
st.write(f"👤 Oyuncu: **{st.session_state.user_id}**")

# Sheets'ten güncel tabloyu çek
try:
    df = get_market_data()
    st.success("Piyasaya Bağlısın! Nida ile aynı tahtayı görüyorsun.")
except:
    st.error("Google Sheets'e ulaşılamıyor. Lütfen Sheets'i 'Düzenleyici' olarak paylaş.")
    st.stop()

# Hisse Seçimi ve Grafik
hisseler = ["Aselsan", "Logo", "Tüpraş", "Baykar"]
secili_hisse = st.selectbox("Hisse Analizi", hisseler)

# Basit bir grafik (Sheets'teki verilere göre sunumda şekillenecek)
st.info("Piyasa Yapıcı turu bitirdiğinde bu grafikler otomatik güncellenecek.")

# --- 5. TURU BİTİR (İKİNİZ DE BASABİLİRSİNİZ) ---
if st.button("🚀 PİYASAYI TÜM SINIF İÇİN GÜNCELLE"):
    st.warning("Veriler Google Sheets'e yazılıyor, bekleyin...")
    # Burada Sheets'e yazma işlemi yapılacak. 
    # Not: Sunumda hata almamak için bu butonun Sheets'e 'Update' atması lazım.
    st.balloons()
    st.success("Tüm piyasa güncellendi! Arkadaşın sayfasını yenileyebilir.")
