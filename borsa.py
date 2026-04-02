import streamlit as st
import pandas as pd
import random
import plotly.graph_objects as go
from streamlit_gsheets import GSheetsConnection

# --- 1. AYARLAR VE BAĞLANTI ---
st.set_page_config(page_title="HUFOYT-BORSA SİMÜLASYONU", layout="wide")

# Senin gönderdiğin linki buraya ekledim
SHEET_URL = "https://docs.google.com/spreadsheets/d/1y2C4aa-06HZoKcJ5oGhejfPLpf4vGVvPaX_sRH28glE/edit?gid=0#gid=0"

# --- 2. SESSION STATE (BELLEK) YÖNETİMİ ---
if 'init' not in st.session_state:
    st.session_state.update({
        'prices': {"Aselsan": 100.0, "Logo": 100.0, "Tüpraş": 100.0, "Baykar": 100.0},
        'history': {"Aselsan": [100.0], "Logo": [100.0], "Tüpraş": [100.0], "Baykar": [100.0]},
        'cash': 50000.0, 'portfolio': {"Aselsan": 0, "Logo": 0, "Tüpraş": 0, "Baykar": 0},
        'ai_cash': 50000.0, 'ai_portfolio': {"Aselsan": 0, "Logo": 0, "Tüpraş": 0, "Baykar": 0},
        'round': 1, 'ai_comment': "AI piyasayı analiz ediyor...", 'init': True, 'user_id': ""
    })

# --- 3. GİRİŞ EKRANI ---
if not st.session_state.user_id:
    st.title("🏛️ HUFOYT-BORSA SİMÜLASYONU")
    st.subheader("Hacettepe Finansal Okuryazarlık Topluluğu")
    nick = st.text_input("Yarışmacı Adın:", placeholder="Örn: Utku_Hacettepe")
    if st.button("Piyasaya Bağlan"):
        if nick:
            st.session_state.user_id = nick
            st.rerun()
    st.stop()

# --- 4. ÜST PANEL (CÜZDAN VE AI DURUMU) ---
st.title("📊 HUFOYT-BORSA SİMÜLASYONU")
u_val = st.session_state.cash + sum(v * st.session_state.prices[k] for k, v in st.session_state.portfolio.items())
a_val = st.session_state.ai_cash + sum(v * st.session_state.prices[k] for k, v in st.session_state.ai_portfolio.items())

c1, c2, c3 = st.columns(3)
c1.metric("👤 Senin Toplam Varlık", f"{round(u_val, 2)} TL", f"Nakit: {round(st.session_state.cash, 2)}")
c2.metric("🤖 AI Toplam Varlık", f"{round(a_val, 2)} TL", f"Nakit: {round(st.session_state.ai_cash, 2)}")
c3.info(f"⏱ **TUR:** {st.session_state.round}")

# --- 5. ANALİZ VE İŞLEM ---
col_graph, col_trade = st.columns([2, 1])

with col_graph:
    hisse = st.selectbox("Grafik İncele", list(st.session_state.prices.keys()))
    fig = go.Figure(go.Scatter(y=st.session_state.history[hisse], mode='lines+markers', line=dict(color='#00FF00')))
    fig.update_layout(template="plotly_dark", height=300, margin=dict(l=0, r=0, t=20, b=0))
    st.plotly_chart(fig, use_container_width=True)

with col_trade:
    st.subheader("🛒 İşlem Merkezi")
    fiyat = st.session_state.prices[hisse]
    st.write(f"Birim Fiyat: **{round(fiyat, 2)} TL**")
    st.write(f"Sendeki: **{st.session_state.portfolio[hisse]} Adet**")
    
    miktar = st.number_input("Adet", min_value=1, value=1, step=1)
    
    b1, b2 = st.columns(2)
    if b1.button("✅ SATIN AL", use_container_width=True):
        maliyet = fiyat * miktar
        if st.session_state.cash >= maliyet:
            st.session_state.cash -= maliyet
            st.session_state.portfolio[hisse] += miktar
            st.rerun()
    if b2.button("❌ SATIŞ YAP", use_container_width=True):
        if st.session_state.portfolio[hisse] >= miktar:
            st.session_state.cash += fiyat * miktar
            st.session_state.portfolio[hisse] -= miktar
            st.rerun()

# --- 6. AI ANALİZ PANELİ (AKILLI AI) ---
st.markdown("---")
st.subheader("🤖 Yapay Zeka Strateji Masası")
st.write(f"🗨️ **AI Diyor ki:** _{st.session_state.ai_comment}_")

# AI Portföyünü Görselleştirme
ai_p_df = pd.DataFrame([{"Hisse": k, "Adet": v, "Değer": round(v * st.session_state.prices[k], 2)} 
                        for k, v in st.session_state.ai_portfolio.items() if v > 0])
if not ai_p_df.empty:
    st.dataframe(ai_p_df, use_container_width=True, hide_index=True)
else:
    st.caption("AI şu an tamamen nakitte bekliyor.")

# --- 7. TURU BİTİR (BOTLAR VE AI HAREKETİ) ---
if st.button("🚀 SONRAKİ TUR (Piyasayı Oynat)", use_container_width=True):
    ai_actions = []
    for k in st.session_state.prices.keys():
        old_p = st.session_state.prices[k]
        
        # 1000 Bot (Arz-Talep Duyarlılığı)
        bot_sentiment = random.uniform(-0.07, 0.07)
        
        # Akıllı AI Karar Mekanizması
        momentum = (old_p - st.session_state.history[k][-1]) / (st.session_state.history[k][-1] + 1e-6)
        
        # AI Satın Alma (Stratejik)
        if momentum > 0.02 and st.session_state.ai_cash > old_p * 10:
            st.session_state.ai_cash -= old_p * 10
            st.session_state.ai_portfolio[k] += 10
            ai_actions.append(f"{k} hissesinde fırsat görüldü, alım yapıldı.")
        # AI Satma (Zarar Kes veya Kar Al)
        elif momentum < -0.04 and st.session_state.ai_portfolio[k] > 0:
            st.session_state.ai_cash += old_p * st.session_state.ai_portfolio[k]
            st.session_state.ai_portfolio[k] = 0
            ai_actions.append(f"{k} riskli görüldü, pozisyon kapatıldı.")

        # Fiyat Motoru
        new_p = old_p * (1 + bot_sentiment + (momentum * 0.25))
        st.session_state.prices[k] = max(5, new_p)
        st.session_state.history[k].append(new_p)

    st.session_state.round += 1
    st.session_state.ai_comment = " | ".join(ai_actions) if ai_actions else "Piyasa stabil, AI beklemeye geçti."
    st.rerun()

# --- 8. LİDERLİK TABLOSU ---
st.divider()
st.subheader("🏆 Hacettepe Şampiyonlar Ligi")
ldf = pd.DataFrame({
    "Sıra": [1, 2],
    "Oyuncu": [f"👤 {st.session_state.user_id}", "🤖 Yapay Zeka"],
    "Toplam Varlık": [f"{round(u_val, 2)} TL", f"{round(a_val, 2)} TL"]
})
st.table(ldf)
