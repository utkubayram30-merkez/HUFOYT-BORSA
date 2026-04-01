import streamlit as st
import random
import pandas as pd
import plotly.graph_objects as go

# --- Sektörler ve Şirketler ---
SEKTORLER = {
    "Savunma": ["Aselsan-A", "Roketsan-B", "Tusaş-C", "Baykar-D", "Havelsan-E"],
    "Bankacılık": ["İş-A", "Garanti-B", "Akbank-C", "Yapı-D", "Halk-E"],
    "Enerji": ["Enerji-A", "Tüpraş-B", "Eren-C", "Zorlu-D", "Aksa-E"],
    "Emtia": ["Altın-A", "Gümüş-B", "Bakır-C", "Demir-D", "Petrol-E"],
    "Gayrimenkul": ["Emlak-A", "Toki-B", "Sinpaş-C", "Rönesans-D", "Kuzu-E"],
    "Teknoloji": ["Logo-A", "Soft-B", "Asels-C", "Tech-D", "Data-E"]
}

if 'init' not in st.session_state:
    data = []
    for sek, sirketler in SEKTORLER.items():
        for s in sirketler:
            data.append({"Şirket": s, "Sektör": sek, "Fiyat": 100.0})
    st.session_state.update({
        'df': pd.DataFrame(data), 'cash': 50000.0, 'init': True,
        'ai_cash': 50000.0, 'ai_shares': {s: 0 for sirketler in SEKTORLER.values() for s in sirketler},
        'portfolio': {s: 0 for sirketler in SEKTORLER.values() for s in sirketler},
        'history': {s: [100.0] for sirketler in SEKTORLER.values() for s in sirketler},
        'round': 1, 'ai_log': "AI piyasayı izliyor...", 'scenario_mode': "Normal"
    })

st.set_page_config(page_title="Hacettepe Finans", layout="wide")
st.title("🏛️ Akıllı AI Borsa Simülasyonu")

# --- SENARYO SEÇİMİ (SideBar) ---
st.sidebar.header("📡 Makro Ekonomik Durum")
scenario = st.sidebar.radio("Senaryoyu Değiştir", ["Normal", "Kriz (Panik Satışı)", "Büyüme (Ralli)"])
st.session_state.scenario_mode = scenario
vol_multiplier = {"Normal": 1.0, "Kriz (Panik Satışı)": 2.8, "Büyüme (Ralli)": 1.8}[scenario]

# --- Üst Bilgi ---
u_stock_val = sum(st.session_state.portfolio[s] * st.session_state.df.loc[st.session_state.df['Şirket']==s, 'Fiyat'].values[0] for s in st.session_state.portfolio)
st.markdown(f"### 👤 Nakit: **{round(st.session_state.cash, 2)} TL** | 📦 Toplam Varlık: **{round(st.session_state.cash + u_stock_val, 2)} TL**")

# --- Grafik ---
target = st.selectbox("Hisse Detay", st.session_state.df['Şirket'].tolist())
fig = go.Figure(go.Scatter(y=st.session_state.history[target], mode='lines+markers', line=dict(color='#00FF00')))
fig.update_layout(template="plotly_dark", height=250, margin=dict(l=5, r=5, t=5, b=5))
st.plotly_chart(fig, use_container_width=True)

# --- İŞLEM PANELİ (Fix: Al-Sat Garantili) ---
st.markdown("---")
s_name = st.selectbox("İşlem Yapılacak Şirket", st.session_state.df['Şirket'].tolist(), key="trade_target")
fiyat = st.session_state.df[st.session_state.df['Şirket'] == s_name]['Fiyat'].values[0]
st.write(f"Cari Fiyat: **{round(fiyat, 2)} TL** | Elindeki: **{st.session_state.portfolio[s_name]} Adet**")

miktar = st.number_input("İşlem Adedi", min_value=1, step=1, value=1)

c1, c2 = st.columns(2)
if c1.button("✅ SATIN AL"):
    maliyet = fiyat * miktar
    if st.session_state.cash >= maliyet:
        st.session_state.cash -= maliyet
        st.session_state.portfolio[s_name] += miktar
        st.success(f"{miktar} adet {s_name} alındı.")
        st.rerun()
    else: st.error("Yetersiz bakiye!")

if c2.button("❌ SATIŞ YAP"):
    if st.session_state.portfolio[s_name] >= miktar:
        st.session_state.cash += fiyat * miktar
        st.session_state.portfolio[s_name] -= miktar
        st.success(f"{miktar} adet {s_name} satıldı.")
        st.rerun()
    else: st.error("Elinizde o kadar hisse yok!")

# --- TUR MOTORU & AKILLI AI ---
st.markdown("---")
if st.button(f"🚀 TURU BİTİR (Tur: {st.session_state.round})", use_container_width=True):
    new_prices = []
    ai_actions = []
    
    for idx, row in st.session_state.df.iterrows():
        s = row['Şirket']
        cur_p = row['Fiyat']
        prev_p = st.session_state.history[s][-1]
        mom = (cur_p - prev_p) / (prev_p + 1e-6)
        
        # --- BOTLAR (1000 Bot) ---
        bot_buys = random.randint(400, 600)
        if st.session_state.scenario_mode == "Kriz (Panik Satışı)": bot_buys = random.randint(100, 400)
        elif st.session_state.scenario_mode == "Büyüme (Ralli)": bot_buys = random.randint(600, 900)
        
        dp = (bot_buys - (1000 - bot_buys)) / 1000

        # --- AKILLI AI MANTIĞI ---
        if st.session_state.scenario_mode == "Kriz (Panik Satışı)":
            # Krizde AI panik yapar ve satar
            if st.session_state.ai_shares[s] > 0:
                st.session_state.ai_cash += cur_p * st.session_state.ai_shares[s]
                st.session_state.ai_shares[s] = 0
                ai_actions.append(f"Kriz nedeniyle {s} satıldı.")
        elif st.session_state.scenario_mode == "Büyüme (Ralli)":
            # Büyümede AI agresifleşir
            if mom > 0.01 and st.session_state.ai_cash >= cur_p * 10:
                st.session_state.ai_cash -= cur_p * 10
                st.session_state.ai_shares[s] += 10
                ai_actions.append(f"Ralli beklentisiyle {s} toplandı.")
        else: # Normal Mod
            if mom > 0.03 and st.session_state.ai_cash >= cur_p:
                st.session_state.ai_cash -= cur_p; st.session_state.ai_shares[s] += 1
        
        # Fiyat Güncelleme (Ekonometrik Model)
        change = (dp * 0.45 + mom * 0.35 + random.uniform(-0.02, 0.02)) * vol_multiplier
        new_p = cur_p * (1 + change)
        new_prices.append(max(5, new_p))
        st.session_state.history[s].append(new_p)

    st.session_state.df['Fiyat'] = new_prices
    st.session_state.round += 1
    st.session_state.ai_log = ai_actions[0] if ai_actions else "AI piyasayı gözlemliyor."
    st.rerun()

st.warning(f"🤖 **AI Analizi:** {st.session_state.ai_log}")

# --- Portföy & Liderlik ---
tab1, tab2 = st.tabs(["🏆 Liderlik", "💼 Portföy"])
with tab1:
    ai_val = st.session_state.ai_cash + sum(st.session_state.ai_shares[s] * st.session_state.df.loc[st.session_state.df['Şirket']==s, 'Fiyat'].values[0] for s in st.session_state.ai_shares)
    st.table(pd.DataFrame({"Oyuncu": ["👤 Sen", "🤖 AI"], "Değer (TL)": [round(st.session_state.cash + u_stock_val, 2), round(ai_val, 2)]}))
with tab2:
    p_data = [{"Hisse": k, "Adet": v} for k, v in st.session_state.portfolio.items() if v > 0]
    if p_data: st.table(pd.DataFrame(p_data))
    else: st.write("Portföyün boş.")
