import streamlit as st
import pandas as pd
import random
import plotly.graph_objects as go

# --- 1. AYARLAR ---
st.set_page_config(page_title="HUFOYT-BORSA TERMİNALİ", layout="wide")

# --- 2. VERİ SETİ ---
SIRKETLER = ["Aselsan", "Logo", "Tüpraş", "Baykar", "Ereğli", "Sasa"]

if 'init_v4' not in st.session_state:
    st.session_state.update({
        'prices': {k: random.uniform(90, 110) for k in SIRKETLER},
        'history': {k: [100.0] for k in SIRKETLER},
        'cash': 100000.0,
        'portfolio': {k: 0 for k in SIRKETLER},
        'ai_cash': 100000.0,
        'ai_portfolio': {k: 0 for k in SIRKETLER},
        'round': 1,
        'ai_log': "AI piyasayı izliyor...",
        'selected_stock': "Aselsan",
        'user_id': "",
        'init_v4': True
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
# Sen butona basmasan da her etkileşimde botlar fiyatları titretir
for k in SIRKETLER:
    bot_pressure = random.uniform(-0.006, 0.006) # %0.6'lık bot dalgalanması
    st.session_state.prices[k] *= (1 + bot_pressure)

# --- 5. CANLI TABELA ---
st.title("🏛️ HUFOYT-BORSA CANLI TERMİNAL")
st.markdown(f"👤 **Operatör:** {st.session_state.user_id} | ⏱ **TUR:** {st.session_state.round}")

cols = st.columns(len(SIRKETLER))
for i, s in enumerate(SIRKETLER):
    f_suan = st.session_state.prices[s]
    f_once = st.session_state.history[s][-1]
    degisim = ((f_suan - f_once) / f_once) * 100
    cols[i].metric(s, f"{round(f_suan, 2)} TL", f"{round(degisim, 2)}%")

st.divider()

# --- 6. GRAFİK VE İŞLEM ---
cl, cr = st.columns([2, 1])

with cl:
    st.subheader(f"📈 {st.session_state.selected_stock} Anlık Grafiği")
    fig = go.Figure(go.Scatter(y=st.session_state.history[st.session_state.selected_stock] + [st.session_state.prices[st.session_state.selected_stock]], 
                               mode='lines+markers', line=dict(color='#00FF00', width=2)))
    fig.update_layout(template="plotly_dark", height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Hızlı Hisse Değiştirme (Tıklayınca fiyatlar da oto güncellenir)
    st.write("Şirket Seçimi:")
    b_cols = st.columns(len(SIRKETLER))
    for i, s in enumerate(SIRKETLER):
        if b_cols[i].button(s):
            st.session_state.selected_stock = s
            st.rerun()

with cr:
    st.subheader("🏦 Cüzdan & Emir")
    fiyat = st.session_state.prices[st.session_state.selected_stock]
    st.info(f"**Nakit:** {round(st.session_state.cash, 2)} TL")
    st.write(f"**Elinizde:** {st.session_state.portfolio[st.session_state.selected_stock]} Adet")
    
    mik = st.number_input("İşlem Miktarı", min_value=1, value=100, step=10)
    cal, csat = st.columns(2)
    if cal.button("✅ SATIN AL", use_container_width=True):
        if st.session_state.cash >= fiyat * mik:
            st.session_state.cash -= fiyat * mik
            st.session_state.portfolio[st.session_state.selected_stock] += mik
            st.rerun()
    if csat.button("❌ SATIŞ YAP", use_container_width=True):
        if st.session_state.portfolio[st.session_state.selected_stock] >= mik:
            st.session_state.cash += fiyat * mik
            st.session_state.portfolio[st.session_state.selected_stock] -= mik
            st.rerun()

# --- 7. AI PORTFÖYÜ (ÇEŞİTLENDİRİLMİŞ) ---
st.divider()
st.subheader("🤖 Yapay Zeka (AI) Portföyü")
ai_total = st.session_state.ai_cash + sum(v * st.session_state.prices[k] for k, v in st.session_state.ai_portfolio.items())
st.write(f"🗨️ **AI Mesajı:** {st.session_state.ai_log} | **Toplam Varlık:** {round(ai_total, 2)} TL")

ai_df = pd.DataFrame([{"Hisse": k, "Adet": v, "Bakiye": round(v*st.session_state.prices[k], 2)} 
                      for k, v in st.session_state.ai_portfolio.items() if v > 0])
st.dataframe(ai_df, use_container_width=True, hide_index=True)

# --- 8. TUR YÖNETİMİ ---
st.divider()
if st.button("🚀 SONRAKİ TURU BAŞLAT (Büyük Dalga & AI Kararı)", use_container_width=True):
    ai_actions = []
    for k in SIRKETLER:
        old_p = st.session_state.prices[k]
        change = random.uniform(-0.10, 0.10) # Max %10 limit
        
        # AI Stratejisi: Akıllı Nakit ve Portföy Yönetimi
        if change < -0.05 and st.session_state.ai_cash > old_p * 20:
            st.session_state.ai_cash -= old_p * 20
            st.session_state.ai_portfolio[k] += 20
            ai_actions.append(f"{k} toplandı.")
        elif change > 0.07 and st.session_state.ai_portfolio[k] > 10:
            st.session_state.ai_cash += old_p * 10
            st.session_state.ai_portfolio[k] -= 10
            ai_actions.append(f"{k} kâr alındı.")

        st.session_state.history[k].append(st.session_state.prices[k])
        st.session_state.prices[k] *= (1 + change)

    st.session_state.round += 1
    st.session_state.ai_log = " | ".join(ai_actions[-3:]) if ai_actions else "AI bekleyişte."
    st.balloons()
    st.rerun()
