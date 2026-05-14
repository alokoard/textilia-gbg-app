import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse
import uuid

# Konfiguration för bred bildskärm
st.set_page_config(page_title="Textilia Logistik - Priority Edition", layout="wide")

# --- INITIALISERING ---
if 'fleet' not in st.session_state:
    st.session_state.fleet = []
if 'rutten' not in st.session_state:
    st.session_state.rutten = []

st.title("🚛 Textilia Gbg - Ruttplanering med Prio")

tab1, tab2, tab3 = st.tabs(["📋 Chef: Planera & Prio", "📍 Chaufför: Körning", "🖥️ Chef: Dashboard"])

# ==========================================
# FLIK 1: CHEFSVY (Planera, Fleet & Prio)
# ==========================================
with tab1:
    pwd = st.sidebar.text_input("Chefskod:", type="password")
    if pwd == "textilia2026":
        col_fleet, col_input = st.columns([1, 2])
        
        with col_fleet:
            st.subheader("🚐 Fleet & Kapacitet")
            v_name = st.text_input("Fordonsnamn", placeholder="Ex: Bil 1")
            v_type = st.radio("Typ", ["Singelbil", "Lastbil + Släp"])
            c1, c2 = st.columns(2)
            cap_b = c1.number_input("Kapacitet Bil", value=70)
            cap_s = c2.number_input("Kapacitet Släp", value=0) if v_type == "Lastbil + Släp" else 0
            
            if st.button("➕ Lägg till fordon"):
                st.session_state.fleet.append({"name": v_name, "cap": cap_b + cap_s})
                st.success(f"{v_name} tillagd (Totalt {cap_b + cap_s} cont)")

        with col_input:
            st.subheader("📍 Skapa rutt med Prioritet")
            rutt_nr = st.number_input("Rutt Nummer", min_value=1, step=1)
            
            with st.form("addr_form"):
                addr = st.text_input("Adress")
                prio = st.number_input("Prioritet (1 = Först i listan)", min_value=1, value=1)
                info = st.text_area("Viktig info (Portkod etc.)")
                submitted = st.form_submit_button("Lägg till i Rutt")
                
                if submitted and addr:
                    st.session_state.rutten.append({
                        "id": str(uuid.uuid4()),
                        "rutt": rutt_nr,
                        "adress": addr,
                        "prio": prio,
                        "info": info,
                        "status": "Väntar",
                        "tid": None,
                        "problem": False
                    })
                    st.rerun()

        st.divider()
        st.subheader("📝 Redigera körordning")
        if st.session_state.rutten:
            for i, stopp in enumerate(st.session_state.rutten):
                if stopp['status'] == "Väntar":
                    c1, c2, c3 = st.columns([3, 1, 1])
                    c1.write(f"Rutt {stopp['rutt']}: **{stopp['adress']}**")
                    # Här kan du ändra prio direkt i listan
                    stopp['prio'] = c2.number_input("Ändra Prio", min_value=1, value=stopp['prio'], key=f"edit_{stopp['id']}")
                    if c3.button("Ta bort", key=f"del_{stopp['id']}"):
                        st.session_state.rutten.pop(i)
                        st.rerun()
            
            if st.button("🔴 Rensa All Data"):
                st.session_state.rutten = []
                st.rerun()

    else:
        st.info("Logga in för att planera.")

# ==========================================
# FLIK 2: CHAUFFÖRSVY (Sorterad efter Prio)
# ==========================================
with tab2:
    if not st.session_state.rutten:
        st.info("Inga rutter inlagda.")
    else:
        val_rutt = st.selectbox("Välj din rutt:", sorted(list(set([r['rutt'] for r in st.session_state.rutten]))))
        
        # SORTERING: Här sorteras listan efter Prio-siffran
        mina_stopp = [s for s in st.session_state.rutten if s['rutt'] == val_rutt and s['status'] == "Väntar"]
        mina_stopp.sort(key=lambda x: x['prio'])
        
        st.subheader(f"Körschema Rutt {val_rutt} (Sorterat efter Prio)")
        
        for i, stopp in enumerate(mina_stopp):
            with st.expander(f"PRIO {stopp['prio']}: {stopp['adress']}", expanded=(i==0)):
                if stopp['info']:
                    st.warning(f"**INFO:** {stopp['info']}")
                
                enc_addr = urllib.parse.quote(f"{stopp['adress']}, Göteborg")
                st.link_button("🧭 Navigera", f"https://www.google.com/maps/search/?api=1&query={enc_addr}")
                
                c1, c2 = st.columns(2)
                if c1.button("✅ Levererat", key=f"ok_{stopp['id']}"):
                    stopp['status'] = "Levererad"
                    stopp['tid'] = datetime.now().strftime("%H:%M")
                    st.rerun()
                
                if c2.button("⚠️ Problem", key=f"err_{stopp['id']}"):
                    stopp['problem'] = True
                
                if stopp['problem']:
                    st.camera_input("Ta bild på problemet", key=f"cam_{stopp['id']}")
                    if st.button("Skicka felrapport", key=f"send_{stopp['id']}"):
                        stopp['status'] = "Problem"
                        stopp['tid'] = datetime.now().strftime("%H:%M")
                        st.rerun()

# ==========================================
# FLIK 3: DASHBOARD
# ==========================================
with tab3:
    st.subheader("🖥️ Status & Uppföljning")
    if st.session_state.rutten:
        df = pd.DataFrame(st.session_state.rutten)
        for r_nr in sorted(df['rutt'].unique()):
            r_data = df[df['rutt'] == r_nr]
            klar = len(r_data[r_data['status'] == "Levererad"])
            st.write(f"### Rutt {r_nr}: {klar}/{len(r_data)} klara")
            st.dataframe(r_data[['prio', 'adress', 'status', 'tid', 'info']], use_container_width=True)
