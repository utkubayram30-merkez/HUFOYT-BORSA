import streamlit as st
import pandas as pd
import random
import plotly.graph_objects as go

# --- 1. AYARLAR ---
st.set_page_config(page_title="HUFOYT-BORSA | Canlı Arena", layout="wide")

# Senin aldığın CSV linkini buraya sabitledim
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTgboIt-V17NgEk0YWa6s7_K3II40CpZoi5wR5Mm4cN4TbAGl_F1M5VCJw6dN9x_-OI36J8jtGucFEf/pub?output=csv"

# --- 2. VERİ ÇEKME ---
def verileri_al():
    try:
        # Google Sheets'ten canlı veriyi (CSV) çekiyoruz
        # 'storage_options' hatasını önlemek için basit read_csv kullanıyoruz
        df = pd.read_csv(CSV_URL)
        return df
    except Exception as e:
        # Hata durumunda boş bir şablon göster
        return pd.DataFrame(columns=["Kullanıcı", "Nakit", "Varlık", "Hisseler"])

# --- 3. SESSION STATE (BELLEK) ---
if 'init' not in st.session_state:
    st.session_state.update({
        'prices': {"Aselsan": 100.0, "Logo": 100.0, "Tüpraş": 100.0, "Baykar": 100.0},
        'history': {"Aselsan": [100.0], "Logo": [100.0], "Tüpraş": [100.0], "Baykar": [100.0]},
        'round': 1,
        'user_id': ""
    })

# --- 4. GİRİŞ ---
if not st.session_state.user_id:
    st.title("🏛️ HUFOYT-BORSA SİMÜLASYONU")
    st.subheader("Hacettepe Finansal Okuryazarlık Topluluğu")
    nick = st.text_input("Yarışmacı Adın:")
    if st.button("Piyasaya Bağlan"):
        if nick:
            st.session_state.user_id = nick
            st.rerun()
    st.stop()

# --- 5. CANLI LİDERLİK TABLOSU ---
st.title("📊 HUFOYT-BORSA | Canlı Piyasa")
st.write(f"👤 Oyuncu: **{st.session_state.user_id}**")

st.subheader("🏆 Hacettepe Canlı Sıralama")
# Bu tablo Excel'deki verileri canlı çeker
df_leader = verileri_al()
if not df_leader.empty:
    st.table(df_leader)
else:
    st.info("Henüz Excel'de veri yok. Excel'e (A2: UTKU, B2: 50000) yazıp kaydederseniz burada görünür.")

# --- 6. GRAFİK VE TUR YÖNETİMİ ---
hisse = st.selectbox("Hisse Analizi", list(st.session_state.prices.keys()))
fiyat = st.session_state.prices[hisse]

fig = go.Figure(go.Scatter(y=st.session_state.history[hisse], mode='lines+markers', line=dict(color='#00FF00')))
fig.update_layout(template="plotly_dark", height=300)
st.plotly_chart(fig, use_container_width=True)

# --- 7. PİYASAYI OYNAT (HERKES İÇİN) ---
if st.button("🚀 PİYASAYI TÜM SINIF İÇİN GÜNCELLE"):
    for k in st.session_state.prices.keys():
        change = random.uniform(-0.08, 0.08)
        st.session_state.prices[k] *= (1 + change)
        st.session_state.history[k].append(st.session_state.prices[k])
    st.session_state.round += 1
    st.balloons()
    st.success("Tüm piyasa güncellendi! Nida sayfasını yenileyebilir.")
