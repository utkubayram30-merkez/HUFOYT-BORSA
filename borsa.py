import streamlit as st
import pandas as pd
import random
import plotly.graph_objects as go
import time

# --- 1. AYARLAR ---
st.set_page_config(page_title="HUFOYT-BORSA SİMÜLASYONU", layout="wide")

# --- 2. VERİ SETİ ---
SIRKETLER = ["Aselsan", "Logo", "Tüpraş", "Baykar", "Ereğli", "Sasa"]

if 'init_pro' not in st.session_state:
    st.session_state.update({
        'prices': {k: random.uniform(80, 120) for k in SIRKETLER},
        'history': {k: [100.0] for k in SIRKETLER},
        'cash': 100000.0,
        'portfolio': {k: 0 for k in SIRKETLER},
        'ai_cash': 100000.0,
        'ai_portfolio': {k: 0 for k in SIRKETLER},
        'round': 1,
        'ai_log': "AI piyasayı izliyor...",
        'last_update': time.time(),
        'user_id': "",
        'selected_stock': "Aselsan"
    })

# --- 3. GİRİŞ EKRANI ---
if not st.session_state.user_id:
    st.title("🏛️ HUFOYT-BORSA SİMÜLASYONU")
    st.markdown("### Hacettepe Finansal Okuryazarlık Topluluğu | Terminal v3.0")
    nick = st.text_input("Kullanıcı Adı:", placeholder="Utku")
    if st.button("Sisteme Bağlan"):
        if nick:
            st.session_state.user_id = nick
            st.rerun()
    st.stop()

# --- 4. BOT SİMÜLASYONU (CANLI AKIŞ) ---
# Her sayfa yenilendiğinde botlar ufak ufak fiyatları oynatır
for k in SIRKETLER:
    noise = random.uniform(-0.005, 0.005) # Botlar %0.5 oynatır
    st.session_state.prices[k] *= (1 + noise)

# --- 5. ÜST PANEL: CANLI FİYAT TABELASI ---
st.title("🏛️ HUFOYT-BORSA SİMÜLASYONU")
st.markdown("---")
cols = st.columns(len(SIRKETLER))
for i, sirket in enumerate(SIRKETLER):
    fiyat = st.session_state.prices[sirket]
    degisim = ((fiyat - st.session_state.history[sirket][-1]) / st.session_state.history[sirket][-1]) * 100
    cols[i].metric(sirket, f"{round(fiyat, 2)} TL", f"{round(degisim, 2)}%")
st.markdown("---")

# --- 6. ANA EKRAN (GRAFİK VE İŞLEM) ---
c_left, c_right = st.columns([2, 1])

with c_left:
    st.subheader(f"📈 {st.session_state.selected_stock} Teknik Analiz")
    fig = go.Figure(go.Scatter(y=st.session_state.history[st.session_state.selected_stock], 
                               mode='lines+markers', line=dict(color='#00FF00', width=2)))
    fig.update_layout(template="plotly_dark", height=400, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
    
    # Şirket Seçme Butonları (Hızlı Geçiş)
    st.write("Grafik Değiştir:")
    btn_cols = st.columns(len(SIRKETLER))
    for i, s in enumerate(SIRKETLER):
        if btn_cols[i].button(s, key=f"btn_{s}"):
            st.session_state.selected_stock = s
            st.rerun()

with c_right:
    st.subheader("🏦 Portföy & İşlem")
    curr_f = st.session_state.prices[st.session_state.selected_stock]
    
    st.info(f"**Nakit:** {round(st.session_state.cash, 2)} TL")
    st.write(f"**{st.session_state.selected_stock} Adet:** {st.session_state.portfolio[st.session_state.selected_stock]}")
    
    miktar = st.number_input("Adet", min_value=1, value=100, step=10)
    
    col_al, col_sat = st.columns(2)
    if col_al.button("✅ AL", use_container_width=True):
        if st.session_state.cash >= curr_f * miktar:
            st.session_state.cash -= curr_f * miktar
            st.session_state.portfolio[st.session_state.selected_stock] += miktar
            st.rerun()
    
    if col_sat.button("❌ SAT", use_container_width=True):
        if st.session_state.portfolio[st.session_state.selected_stock] >= miktar:
            st.session_state.cash += curr_f * miktar
            st.session_state.portfolio[st.session_state.selected_stock] -= miktar
            st.rerun()

# --- 7. AI STRATEJİ MERKEZİ ---
st.divider()
c_ai_info, c_ai_port = st.columns([1, 2])

with c_ai_info:
    st.subheader("🤖 Akıllı AI Masası")
    st.write(f"**Strateji:** {st.session_state.ai_log}")
    ai_toplam = st.session_state.ai_cash + sum(v * st.session_state.prices[k] for k, v in st.session_state.ai_portfolio.items())
    st.metric("AI Toplam Varlık", f"{round(ai_toplam, 2)} TL")

with c_ai_port:
    st.subheader("🤖 AI Portföy Dağılımı")
    ai_df = pd.DataFrame([{"Hisse": k, "Adet": v, "Değer": round(v*st.session_state.prices[k], 2)} 
                          for k, v in st.session_state.ai_portfolio.items() if v > 0])
    if not ai_df.empty:
        st.dataframe(ai_df, use_container_width=True, hide_index=True)
    else:
        st.write("AI şu an nakitte bekliyor.")

# --- 8. TUR YÖNETİMİ (PİYASA YAPICI) ---
st.divider()
if st.button("🚀 SONRAKİ TURU BAŞLAT (60 Saniyelik Yeni Periyot)", use_container_width=True):
    ai_actions = []
    
    # 1. Şirket Fiyatlarını Güncelle (Max %10)
    for k in SIRKETLER:
        old_p = st.session_state.prices[k]
        change = random.uniform(-0.10, 0.10)
        st.session_state.prices[k] *= (1 + change)
        st.session_state.history[k].append(st.session_state.prices[k])
        
        # 2. Akıllı AI İşlem Yapar (Çeşitlendirme Yapar)
        # Eğer hisse düştüyse ve nakit varsa al (Dip avcısı)
        if change < -0.05 and st.session_state.ai_cash > st.session_state.prices[k] * 50:
            alim = 50
            st.session_state.ai_cash -= st.session_state.prices[k] * alim
            st.session_state.ai_portfolio[k] += alim
            ai_actions.append(f"{k} dip görüldü, eklendi.")
        
        # Eğer hisse çok çıktıysa kâr al
        elif change > 0.07 and st.session_state.ai_portfolio[k] > 20:
            st.session_state.ai_cash += st.session_state.prices[k] * 20
            st.session_state.ai_portfolio[k] -= 20
            ai_actions.append(f"{k} kâr realizasyonu.")

    st.session_state.round += 1
    st.session_state.ai_log = " | ".join(ai_actions[-3:]) if ai_actions else "Pozisyonlar korunuyor."
    st.balloons()
    st.rerun()

st.caption("Not: Sayfa her yenilendiğinde botlar %0.5 volatilite ile fiyatları titretir.")
