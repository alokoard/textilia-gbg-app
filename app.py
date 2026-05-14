import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import urllib.parse  # FIXAR DITT NAMEERROR
import uuid
import json

# --- GRUNDINSTÄLLNINGAR ---
st.set_page_config(page_title="Textilia Gbg Logistik", layout="wide")

# Fixar svensk tid (UTC+2 för sommartid)
def svensk_tid():
    return (datetime.utcnow() + timedelta(hours=2)).strftime("%H:%M")

# --- MINNESHANTERING ---
if 'rutter' not in st.session_state:
    st.session_state.rutter = {} 
if 'fleet' not in st.session_state:
    st.session_state.fleet = {}

# --- NAVBAR / APP-VÄLJARE ---
st.sidebar.title("🚛 Textilia Gbg")
app_mode = st.sidebar.radio("Välj arbetsläge:", ["🏗️ Planering (Chef)", "🚚 Leverans (Chaufför)"])

# ==========================================
# APP 1: PLANERING & LOGISTIK (CHEF)
# ==========================================
if app_mode == "🏗️ Planering (Chef)":
    st.header("🏗️ Logistikplanering & Orderstyrning")
    
    pwd = st.sidebar.text_input("Chefskod:", type="password")
    if pwd == "textilia2026":
        
        # 1. Skapa och hantera rutter
        with st.sidebar:
            st.subheader("Hantera Rutter")
            ny_r = st.text_input("Namn på rutt (ex: Rutt 1):")
            if st.button("Skapa Rutt"):
                if ny_r and ny_r not in st.session_state.rutter:
                    st.session_state.rutter[ny_r] = []
                    st.session_state.fleet[ny_r] = {"bil": 70, "släp": 0}
                    st.rerun()
            
            st.divider()
            if st.session_state.rutter:
                valda = st.selectbox("Redigera rutt:", list(st.session_state.rutter.keys()))
                st.session_state.fleet[valda]["bil"] = st.number_input("Kapacitet Bil:", value=st.session_state.fleet[valda]["bil"])
                st.session_state.fleet[valda]["släp"] = st.number_input("Kapacitet Släp:", value=st.session_state.fleet[valda]["släp"])
                if st.button("🗑️ Radera rutt"):
                    del st.session_state.rutter[valda]
                    st.rerun()

        if st.session_state.rutter:
            # 2. Lägg till adresser
            with st.expander("➕ Mass-import adresser"):
                bulk = st.text_area("Klistra in adresser (en per rad):")
                info_text = st.text_input("Viktig info till chauffören (t.ex. Portkod 1234)")
                if st.button("Lägg till i planering"):
                    for rad in bulk.split("\n"):
                        if rad.strip():
                            nr = max([s['Ordning'] for s in st.session_state.rutter[valda]], default=0) + 1
                            st.session_state.rutter[valda].append({
                                "ID": str(uuid.uuid4())[:8],
                                "Ordning": nr,
                                "Adress": rad.strip(),
                                "Info": info_text,
                                "Status": "Väntar",
                                "Tid": "",
                                "Vagnar_In": 0
                            })
                    st.rerun()

            # 3. MANUELL ORDNING (THE MASTER PLAN)
            st.subheader(f"Körschema för {valda}")
            df = pd.DataFrame(st.session_state.rutter[valda])
            if not df.empty:
                # Här kan du ändra Ordning, Adress och Info direkt
                edited_df = st.data_editor(
                    df,
                    column_order=["Ordning", "Adress", "Info", "Status", "Tid"],
                    use_container_width=True,
                    key=f"editor_{valda}"
                )
                
                if st.button("💾 Spara & Optimera Körordning"):
                    st.session_state.rutter[valda] = edited_df.sort_values(by="Ordning").to_dict('records')
                    st.success("Körordningen sparad och uppdaterad för chauffören!")
    else:
        st.info("Logga in för att se planeringen.")

# ==========================================
# APP 2: LEVERANS (CHAUFFÖR)
# ==========================================
else:
    st.header("🚚 Chaufför: Leverans & Retur")
    
    if not st.session_state.rutter:
        st.info("Inga rutter är planerade än.")
    else:
        c_rutt = st.selectbox("Välj din rutt för idag:", list(st.session_state.rutter.keys()))
        
        # 1. LASTNINGSLISTA (LIFO-princip: Sista stoppet längst fram)
        with st.expander("📦 SE LASTNINGSLISTA (Packa bilen rätt)"):
            lastning = sorted(st.session_state.rutter[c_rutt], key=lambda x: x['Ordning'], reverse=True)
            for s in lastning:
                st.write(f"▪️ Lasta: **{s['Adress']}**")
            st.caption("Lastas i denna ordning: Sista stoppet först (längst in). Första stoppet sist (vid dörren).")

        # 2. KÖRNING
        st.divider()
        mina_stopp = [s for s in st.session_state.rutter[c_rutt] if s['Status'] == "Väntar"]
        
        if not mina_stopp:
            st.success("🎉 Alla leveranser klara! Kör tillbaka till tvätteriet.")
        else:
            nasta = mina_stopp[0]
            st.subheader(f"Nästa stopp: {nasta['Adress']}")
            
            if nasta['Info']:
                st.warning(f"ℹ️ **INFO:** {nasta['Info']}")
            
            # GPS - FIXAT NAMEERROR HÄR
            q_addr = urllib.parse.quote(f"{nasta['Adress']}, Göteborg")
            st.link_button("🗺️ Öppna GPS (Google Maps)", f"https://www.google.com/maps/search/?api=1&query={q_addr}")
            
            st.divider()
            # Returflöde (Smutstvätt in)
            v_in = st.number_input("Hämtat Smutstvätt (Antal vagnar):", value=1, min_value=0)
            
            col1, col2 = st.columns(2)
            if col1.button("✅ LEVERERAT & KLART", use_container_width=True):
                nasta['Status'] = "Levererad"
                nasta['Vagnar_In'] = v_in
                nasta['Tid'] = svensk_tid()
                st.rerun()
            
            if col2.button("⚠️ PROBLEM", use_container_width=True):
                st.session_state[f"prob_{nasta['ID']}"] = True
            
            if st.session_state.get(f"prob_{nasta['ID']}"):
                st.error("Beskriv felet och ta en bild:")
                st.camera_input("Foto på hinder/skada", key=f"cam_{nasta['ID']}")
                if st.button("Skicka Felrapport"):
                    nasta['Status'] = "Problem"
                    nasta['Tid'] = svensk_tid()
                    st.rerun()

# ==========================================
# DASHBOARD (STATUS FÖR KONTORET)
# ==========================================
if st.session_state.rutter and app_mode == "🏗️ Planering (Chef)":
    st.divider()
    st.subheader("🖥️ Live Status - Alla Rutter")
    for r_namn, stopp_lista in st.session_state.rutter.items():
        klara = len([s for s in stopp_lista if s['Status'] == "Levererad"])
        tot = len(stopp_lista)
        v_in_tot = sum([s.get('Vagnar_In', 0) for s in stopp_lista])
        
        st.write(f"**{r_namn}**: {klara}/{tot} klara. Smutstvätt på väg in: **{v_in_tot} vagnar**.")
