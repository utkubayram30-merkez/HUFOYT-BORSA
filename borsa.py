import streamlit as st
import pandas as pd
import random
import plotly.graph_objects as go
import time

# --- 1. AYARLAR ---
st.set_page_config(page_title="HUFOYT-BORSA SİMÜLASYONU", layout="wide")

# --- 2. VERİ SETİ VE BAŞLATMA ---
SIRKETLER = ["Aselsan", "Logo", "Tüpraş", "Baykar", "Ereğli", "Sasa"]

# Session State Kontrolü (Hata payı sıfır)
if 'user_id' not in st.session_state:
    st.session_state.user_id = ""

if 'init_pro' not in st.session_state:
    st.session_state.update({
        'prices': {k: random.uniform(95, 105) for k in SIRKETLER},
        'history': {k: [100.0] for k in SIRKETLER},
        'cash': 100000.0,
        'portfolio': {k: 0 for k in SIRKETLER},
        'ai_cash': 100000.0,
        'ai_portfolio': {k: 0 for k in SIRKETLER},
        'round': 1,
        'ai_log': "AI piyasayı analiz ediyor...",
        'selected_stock': "Aselsan",
        'init_pro': True
    })

# --- 3. GİRİŞ EKRANI (DÜZELTİLDİ) ---
if st.session_state.user_id == "":
    st.title("🏛️ HUFOYT-BORSA SİMÜLASYONU")
    st.markdown("### Hacettepe Finansal Okuryazarlık Topluluğu | v3.1")
    
    # Form kullanarak girişi garantiye alıyoruz
    with st.form("login_form"):
        nick = st.text_input("Kullanıcı Adı:", placeholder="Utku")
        submit = st.form_submit_button("Sisteme Bağlan")
        if submit and nick:
            st.session_state.user_id = nick
            st.rerun()
    st.stop()

# --- 4. BOT SİMÜLASYONU (Fiyat Titretme) ---
for k in SIRKETLER:
    noise = random.uniform(-0.003, 0.003) # %0.3 anlık oynama
    st.session_state.prices[k] *= (1 + noise)

# --- 5. ÜST PANEL: CANLI TABELA ---
st.title("🏛️ HUFOYT-BORSA SİMÜLASYONU")
st.markdown(f"👤 **Hoş Geldin {st.session_state.user_id}** | ⏱ **TUR:** {st.session_state.round}")

# Canlı Fiyat Bandı
cols = st.columns(len(SIRKETLER))
for i, s in enumerate(SIRKETLER):
    fiyat = st.session_state.prices[s]
    degisim = ((fiyat - st.session_state.history[s][-1]) / st.session_state.history[s][-1]) * 100
    cols[i].metric(s, f"{round(fiyat, 2)} TL", f"{round(degisim, 2)}%")

st.markdown("---")

# --- 6. ANA TERMİNAL (GRAFİK VE İŞLEM) ---
c_left, c_right = st.columns([2, 1])

with c_left:
    st.subheader(f"📈 {st.session_state.selected_stock} Canlı Veri")
    # Grafik oluşturma
    fig = go.Figure(go.Scatter(y=st.session_state.history[st.session_state.selected_stock], 
                               mode='lines+markers', line=dict(color='#00FF00', width=2)))
    fig.update_layout(template="plotly_dark", height=380, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
    
    # Hızlı Şirket Değiştirme Butonları
    st.write("Hızlı Grafik Değiştir:")
    btn_cols = st.columns(len(SIRKETLER))
    for i, s in enumerate(SIRKETLER):
        if btn_cols[i].button(s, key=f"nav_{s}"):
            st.session_state.selected_stock = s
            st.rerun()

with c_right:
    st.subheader("🏦 Portföy Yönetimi")
    curr_f = st.session_state.prices[st.session_state.selected_stock]
    
    st.info(f"**Nakit:** {round(st.session_state.cash, 2)} TL")
    st.write(f"**{st.session_state.selected_stock} Mevcut:** {st.session_state.portfolio[st.session_state.selected_stock]} Adet")
    
    miktar = st.number_input("İşlem Adedi", min_value=1, value=100, step=10)
    
    c_al, c_sat = st.columns(2)
    if c_al.button("✅ AL", use_container_width=True):
        if st.session_state.cash >= curr_f * miktar:
            st.session_state.cash -= curr_f * miktar
            st.session_state.portfolio[st.session_state.selected_stock] += miktar
            st.rerun()
    
    if c_sat.button("❌ SAT", use_container_width=True):
        if st.session_state.portfolio[st.session_state.selected_stock] >= miktar:
            st.session_state.cash += curr_f * miktar
            st.session_state.portfolio[st.session_state.selected_stock] -= miktar
            st.rerun()

# --- 7. AI STRATEJİ VE PORTFÖYÜ ---
st.divider()
ca1, ca2 = st.columns([1, 2])

with ca1:
    st.subheader("🤖 Yapay Zeka (AI)")
    st.write(f"**Güncel Durum:** {st.session_state.ai_log}")
    ai_total = st.session_state.ai_cash + sum(v * st.session_state.prices[k] for k, v in st.session_state.ai_portfolio.items())
    st.metric("AI Toplam Varlık", f"{round(ai_total, 2)} TL")

with ca2:
    st.subheader("🤖 AI Portföy Dağılımı")
    ai_p_list = [{"Hisse": k, "Adet": v, "Değer": round(v*st.session_state.prices[k], 2)} 
                 for k, v in st.session_state.ai_portfolio.items() if v > 0]
    if ai_p_list:
        st.dataframe(pd.DataFrame(ai_p_list), use_container_width=True, hide_index=True)
    else:
        st.write("AI şu an sadece Nakit tutuyor.")

# --- 8. TUR SONU (YÖNETİCİ BUTONU) ---
st.divider()
if st.button("🚀 SONRAKİ TURU BAŞLAT (Fiyatları Oynat & AI Hamlesi)", use_container_width=True):
    ai_msgs = []
    for k in SIRKETLER:
        old_p = st.session_state.prices[k]
        # Max %10 oynama
        change = random.uniform(-0.10, 0.10)
        
        # Akıllı AI: Çeşitlendirme (Her hisseden almaya çalışır)
        if change < -0.04 and st.session_state.ai_cash > old_p * 30:
            st.session_state.ai_cash -= old_p * 30
            st.session_state.ai_portfolio[k] += 30
            ai_msgs.append(f"{k} dip toplama.")
        elif change > 0.08 and st.session_state.ai_portfolio[k] > 10:
            st.session_state.ai_cash += old_p * 10
            st.session_state.ai_portfolio[k] -= 10
            ai_msgs.append(f"{k} kâr alımı.")

        # Fiyatı tarihe işle ve güncelle
        st.session_state.prices[k] *= (1 + change)
        st.session_state.history[k].append(st.session_state.prices[k])

    st.session_state.round += 1
    st.session_state.ai_log = " | ".join(ai_msgs[-3:]) if ai_msgs else "AI bekliyor."
    st.balloons()
    st.rerun()
