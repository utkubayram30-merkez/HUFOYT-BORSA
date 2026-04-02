import streamlit as st
import pandas as pd
import random
import plotly.graph_objects as go
import time

# --- 1. AYARLAR ---
st.set_page_config(page_title="HUFOYT-BORSA TERMİNALİ", layout="wide")

# --- 2. VERİ SETİ VE BAŞLATMA ---
SIRKETLER = ["Aselsan", "Logo", "Tüpraş", "Baykar", "Ereğli", "Sasa"]
SENARYOLAR = {
    "🐂 BOĞA PİYASASI": (0.02, 0.12, "Piyasa coşkulu, alımlar güçlü!"),
    "🐻 AYI PİYASASI": (-0.12, -0.02, "Panik satışları hakim, dikkat!"),
    "⚖️ STABİL PİYASA": (-0.04, 0.04, "Yatay seyir devam ediyor.")
}

if 'init_final' not in st.session_state:
    st.session_state.update({
        'prices': {k: random.uniform(90, 110) for k in SIRKETLER},
        'history': {k: [100.0] for k in SIRKETLER},
        'cash': 100000.0,
        'portfolio': {k: 0 for k in SIRKETLER},
        'ai_cash': 100000.0,
        'ai_portfolio': {k: 0 for k in SIRKETLER},
        'round': 1,
        'ai_log': "AI piyasayı kokluyor...",
        'selected_stock': "Aselsan",
        'user_id': "",
        'current_scenario': "⚖️ STABİL PİYASA",
        'init_final': True
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

# --- 4. BOT SİMÜLASYONU ---
for k in SIRKETLER:
    st.session_state.prices[k] *= (1 + random.uniform(-0.004, 0.004))

# --- 5. ÜST PANEL VE VARLIK ---
user_total = st.session_state.cash + sum(v * st.session_state.prices[k] for k, v in st.session_state.portfolio.items())
ai_total = st.session_state.ai_cash + sum(v * st.session_state.prices[k] for k, v in st.session_state.ai_portfolio.items())

st.title("🏛️ HUFOYT-BORSA CANLI TERMİNAL")
st.warning(f"📢 **MEVCUT SENARYO:** {st.session_state.current_scenario} | {SENARYOLAR[st.session_state.current_scenario][2]}")

c1, c2, c3 = st.columns(3)
c1.metric("👤 Oyuncu", st.session_state.user_id)
c2.metric("💰 Toplam Varlığınız", f"{round(user_total, 2)} TL")
c3.metric("🤖 AI Varlığı", f"{round(ai_total, 2)} TL")

st.divider()
cols = st.columns(len(SIRKETLER))
for i, s in enumerate(SIRKETLER):
    f_now = st.session_state.prices[s]
    f_old = st.session_state.history[s][-1]
    diff = ((f_now - f_old) / f_old) * 100
    cols[i].metric(s, f"{round(f_now, 2)} TL", f"{round(diff, 2)}%")

# --- 6. GRAFİK VE İŞLEM ---
cl, cr = st.columns([2, 1])

with cl:
    st.subheader(f"📈 {st.session_state.selected_stock} Analiz")
    fig = go.Figure(go.Scatter(y=st.session_state.history[st.session_state.selected_stock] + [st.session_state.prices[st.session_state.selected_stock]], 
                               mode='lines+markers', line=dict(color='#00FF00', width=2)))
    fig.update_layout(template="plotly_dark", height=300, margin=dict(l=0,r=0,b=0,t=0))
    st.plotly_chart(fig, use_container_width=True)
    
    scols = st.columns(len(SIRKETLER))
    for i, s in enumerate(SIRKETLER):
        if scols[i].button(s, key=f"s_{s}"):
            st.session_state.selected_stock = s
            st.rerun()

with cr:
    st.subheader("🏦 Portföyüm")
    fiyat = st.session_state.prices[st.session_state.selected_stock]
    st.write(f"Nakit: **{round(st.session_state.cash, 2)} TL**")
    
    my_df = pd.DataFrame([{"Hisse": k, "Adet": v} for k, v in st.session_state.portfolio.items() if v > 0])
    st.dataframe(my_df if not my_df.empty else "Portföy boş.", use_container_width=True, hide_index=True)

    mik = st.number_input("Adet", min_value=1, value=100)
    b_al, b_sat = st.columns(2)
    if b_al.button("✅ AL", use_container_width=True):
        if st.session_state.cash >= fiyat * mik:
            st.session_state.cash -= fiyat * mik
            st.session_state.portfolio[st.session_state.selected_stock] += mik
            st.rerun()
    if b_sat.button("❌ SAT", use_container_width=True):
        if st.session_state.portfolio[st.session_state.selected_stock] >= mik:
            st.session_state.cash += fiyat * mik
            st.session_state.portfolio[st.session_state.selected_stock] -= mik
            st.rerun()

# --- 7. AI VE TUR YÖNETİMİ ---
st.divider()
st.subheader("🤖 AI Strateji Masası")
st.info(f"🗨️ **AI Kararı:** {st.session_state.ai_log}")

if st.button("🚀 SONRAKİ TUR (Piyasayı Değiştir)", use_container_width=True):
    # Yeni Senaryo Seç
    st.session_state.current_scenario = random.choice(list(SENARYOLAR.keys()))
    min_ch, max_ch, _ = SENARYOLAR[st.session_state.current_scenario]
    
    ai_actions = []
    for k in SIRKETLER:
        st.session_state.history[k].append(st.session_state.prices[k])
        change = random.uniform(min_ch, max_ch)
        st.session_state.prices[k] *= (1 + change)
        
        # --- AKILLI AI MANTIĞI ---
        # 1. Kâr Al / Risk Yönetimi: Ayı piyasasında veya %10+ kârda hisse satar
        if (st.session_state.current_scenario == "🐻 AYI PİYASASI" or change > 0.10) and st.session_state.ai_portfolio[k] > 0:
            sat_mik = st.session_state.ai_portfolio[k] // 2
            st.session_state.ai_cash += st.session_state.prices[k] * sat_mik
            st.session_state.ai_portfolio[k] -= sat_mik
            ai_actions.append(f"{k} nakite geçildi.")
        
        # 2. Alttan Toplama: Boğa piyasasında veya çok düşmüşse alır
        elif (st.session_state.current_scenario == "🐂 BOĞA PİYASASI" or change < -0.07) and st.session_state.ai_cash > st.session_state.prices[k] * 20:
            st.session_state.ai_cash -= st.session_state.prices[k] * 20
            st.session_state.ai_portfolio[k] += 20
            ai_actions.append(f"{k} takviye edildi.")

    st.session_state.round += 1
    st.session_state.ai_log = " | ".join(list(set(ai_actions))[:3]) if ai_actions else "AI nakit dengesini koruyor."
    st.balloons()
    st.rerun()

# --- 8. OTO-REFRESH ---
time.sleep(5)
st.rerun()
