import streamlit as st
import pandas as pd
import random
import plotly.graph_objects as go
import time

# --- 1. AYARLAR VE OTOMATİK YENİLEME ---
st.set_page_config(page_title="HUFOYT-BORSA TERMİNALİ", layout="wide")

# --- 2. VERİ SETİ ---
SIRKETLER = ["Aselsan", "Logo", "Tüpraş", "Baykar", "Ereğli", "Sasa"]

if 'init_v6' not in st.session_state:
    st.session_state.update({
        'prices': {k: random.uniform(90, 110) for k in SIRKETLER},
        'history': {k: [100.0] for k in SIRKETLER},
        'cash': 100000.0,
        'portfolio': {k: 0 for k in SIRKETLER},
        'ai_cash': 100000.0,
        'ai_portfolio': {k: 0 for k in SIRKETLER},
        'round': 1,
        'ai_log': "AI analiz yapıyor...",
        'selected_stock': "Aselsan",
        'user_id': "",
        'init_v6': True
    })

# --- 3. GİRİŞ SİSTEMİ ---
if st.session_state.user_id == "":
    st.title("🏛️ HUFOYT-BORSA SİMÜLASYONU")
    with st.form("login"):
        u_name = st.text_input("Kullanıcı Adı:")
        if st.form_submit_button("Sisteme Bağlan") and u_name:
            st.session_state.user_id = u_name
            st.rerun()
    st.stop()

# --- 4. OTO-PİYASA (BOT SİMÜLASYONU) ---
for k in SIRKETLER:
    bot_noise = random.uniform(-0.005, 0.005) 
    st.session_state.prices[k] *= (1 + bot_noise)

# --- 5. CANLI ÜST TABELA VE VARLIK GÖSTERGESİ ---
# TOPLAM VARLIK HESAPLAMA (Nakit + Hisselerin Değeri)
user_hisse_degeri = sum(st.session_state.portfolio[k] * st.session_state.prices[k] for k in SIRKETLER)
user_toplam_varlik = st.session_state.cash + user_hisse_degeri

st.title("🏛️ HUFOYT-BORSA CANLI TERMİNAL")

# En üstte Toplam Varlık Metriği
c1, c2, c3 = st.columns([1,1,1])
c1.metric("👤 Kullanıcı", st.session_state.user_id)
c2.metric("💰 Toplam Varlığınız", f"{round(user_toplam_varlik, 2)} TL")
c3.metric("⏱ Mevcut Tur", st.session_state.round)

st.markdown("---")

# Canlı Fiyat Bandı
cols = st.columns(len(SIRKETLER))
for i, s in enumerate(SIRKETLER):
    f_suan = st.session_state.prices[s]
    f_once = st.session_state.history[s][-1]
    degisim = ((f_suan - f_once) / f_once) * 100
    color = "inverse" if degisim < 0 else "normal"
    cols[i].metric(s, f"{round(f_suan, 2)} TL", f"{round(degisim, 2)}%", delta_color=color)

st.divider()

# --- 6. GRAFİK VE İŞLEM ---
cl, cr = st.columns([2, 1])

with cl:
    st.subheader(f"📈 {st.session_state.selected_stock} Teknik Görünüm")
    fig = go.Figure(go.Scatter(y=st.session_state.history[st.session_state.selected_stock] + [st.session_state.prices[st.session_state.selected_stock]], 
                               mode='lines+markers', line=dict(color='#00FF00', width=2)))
    fig.update_layout(template="plotly_dark", height=350, margin=dict(l=0,r=0,b=0,t=0))
    st.plotly_chart(fig, use_container_width=True)
    
    st.write("Hisseler:")
    b_cols = st.columns(len(SIRKETLER))
    for i, s in enumerate(SIRKETLER):
        if b_cols[i].button(s, key=f"nav_{s}"):
            st.session_state.selected_stock = s
            st.rerun()

with cr:
    st.subheader("🏦 Cüzdanım & Portföy")
    fiyat = st.session_state.prices[st.session_state.selected_stock]
    st.write(f"**Boştaki Nakit:** {round(st.session_state.cash, 2)} TL")
    
    my_p = [{"Hisse": k, "Adet": v, "Değer": round(v*st.session_state.prices[k], 2)} 
            for k, v in st.session_state.portfolio.items() if v > 0]
    if my_p:
        st.dataframe(pd.DataFrame(my_p), use_container_width=True, hide_index=True)
    else:
        st.write("Portföyünüz şu an boş.")

    st.divider()
    mik = st.number_input("Adet", min_value=1, value=100, step=10)
    cal, csat = st.columns(2)
    if cal.button("✅ AL", use_container_width=True):
        if st.session_state.cash >= fiyat * mik:
            st.session_state.cash -= fiyat * mik
            st.session_state.portfolio[st.session_state.selected_stock] += mik
            st.rerun()
    if csat.button("❌ SAT", use_container_width=True):
        if st.session_state.portfolio[st.session_state.selected_stock] >= mik:
            st.session_state.cash += fiyat * mik
            st.session_state.portfolio[st.session_state.selected_stock] -= mik
            st.rerun()

# --- 7. AI PORTFÖYÜ ---
st.divider()
st.subheader("🤖 Yapay Zeka (AI) Portföyü")
ai_total = st.session_state.ai_cash + sum(v * st.session_state.prices[k] for k, v in st.session_state.ai_portfolio.items())
st.info(f"🗨️ **AI Hamlesi:** {st.session_state.ai_log} | **AI Toplam Varlık:** {round(ai_total, 2)} TL")

ai_df = pd.DataFrame([{"Hisse": k, "Adet": v, "Bakiye": round(v*st.session_state.prices[k], 2)} 
                      for k, v in st.session_state.ai_portfolio.items() if v > 0])
st.dataframe(ai_df, use_container_width=True, hide_index=True)

# --- 8. TUR YÖNETİMİ ---
st.divider()
if st.button("🚀 SONRAKİ TURU BAŞLAT (Yeni Pazar Verileri)", use_container_width=True):
    for k in SIRKETLER:
        st.session_state.history[k].append(st.session_state.prices[k])
        change = random.uniform(-0.10, 0.10)
        st.session_state.prices[k] *= (1 + change)
        
        # AI Strateji (Otomatik Karar)
        if change < -0.06 and st.session_state.ai_cash > st.session_state.prices[k] * 20:
            st.session_state.ai_cash -= st.session_state.prices[k] * 20
            st.session_state.ai_portfolio[k] += 20
            st.session_state.ai_log = f"{k} düşük fiyattan eklendi."

    st.session_state.round += 1
    st.balloons()
    st.rerun()

# --- 9. OTO-YENİLEME ---
time.sleep(5)
st.rerun()
