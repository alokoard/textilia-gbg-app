import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
import uuid

# --- GRUNDINSTÄLLNINGAR ---
st.set_page_config(page_title="Textilia Gbg PRO", layout="wide")

# Funktion för svensk tid (UTC+2)
def hämta_tid():
    return (datetime.utcnow() + timedelta(hours=2)).strftime("%H:%M")

# --- MINNESHANTERING (Garanterar att inget blandas ihop) ---
if 'rutter' not in st.session_state:
    st.session_state.rutter = {} # Struktur: {"Rutt 1": [stopp1, stopp2], "Rutt 2": []}
if 'fleet' not in st.session_state:
    st.session_state.fleet = {} # Struktur: {"Rutt 1": {"bil": 70, "släp": 30}}

st.title("🚛 Textilia Gbg Logistik - PRO v19.0")

# --- SIDOMENY: Hantera Rutter & Fordon ---
with st.sidebar:
    st.header("⚙️ Administration")
    ny_rutt = st.text_input("Namn på ny rutt:", placeholder="Ex: Rutt 1")
    if st.button("Skapa Rutt"):
        if ny_rutt and ny_rutt not in st.session_state.rutter:
            st.session_state.rutter[ny_rutt] = []
            st.session_state.fleet[ny_rutt] = {"bil": 70, "släp": 0}
            st.rerun()

    st.divider()
    if st.session_state.rutter:
        valda_rutt = st.selectbox("Välj rutt att hantera:", list(st.session_state.rutter.keys()))
        
        st.subheader(f"Kapacitet för {valda_rutt}")
        st.session_state.fleet[valda_rutt]["bil"] = st.number_input("Bil (vagnar)", value=st.session_state.fleet[valda_rutt]["bil"])
        st.session_state.fleet[valda_rutt]["släp"] = st.number_input("Släp (vagnar)", value=st.session_state.fleet[valda_rutt]["släp"])
        tot_cap = st.session_state.fleet[valda_rutt]["bil"] + st.session_state.fleet[valda_rutt]["släp"]
        st.info(f"Total kapacitet: **{tot_cap}** vagnar")
        
        if st.button("🗑️ Radera denna rutt"):
            del st.session_state.rutter[valda_rutt]
            del st.session_state.fleet[valda_rutt]
            st.rerun()

    st.divider()
    st.header("💾 Backup")
    if st.download_button("📥 Spara backup till datorn", json.dumps(st.session_state.rutter), file_name="textilia_backup.json"):
        st.success("Backup nedladdad!")

tab1, tab2, tab3 = st.tabs(["🏗️ 1. Planering (Chef)", "🚚 2. Körning (Chaufför)", "📊 3. Dashboard"])

# ==========================================
# FLIK 1: PLANERING (CHEF)
# ==========================================
with tab1:
    if not st.session_state.rutter:
        st.info("Börja med att skapa en rutt i sidomenyn till vänster.")
    else:
        st.header(f"Planerar: {valda_rutt}")
        
        # 1. Mass-import
        with st.expander("➕ Lägg till adresser (Mass-import)"):
            adresser = st.text_area("Klistra in adresser (en per rad):")
            gemensam_info = st.text_input("Gemensam info för dessa (t.ex. 'Smutstvätt retur')")
            if st.button("Lägg till i rutt"):
                for rad in adresser.split("\n"):
                    if rad.strip():
                        nasta_nr = max([s['Ordning'] for s in st.session_state.rutter[valda_rutt]], default=0) + 1
                        st.session_state.rutter[valda_rutt].append({
                            "ID": str(uuid.uuid4())[:8],
                            "Ordning": nasta_nr,
                            "Adress": rad.strip(),
                            "Info": gemensam_info,
                            "Status": "Väntar",
                            "Tid": "",
                            "Vagnar": 10
                        })
                st.rerun()

        # 2. Manuellt ändra ordning (Excel-vyn)
        st.subheader("Redigera körordning & information")
        if st.session_state.rutter[valda_rutt]:
            df = pd.DataFrame(st.session_state.rutter[valda_rutt])
            # Denna editor låter dig ändra siffran i "Ordning" för att flytta stopp
            redigerad_df = st.data_editor(
                df,
                column_order=["Ordning", "Adress", "Info", "Vagnar", "Status"],
                num_rows="dynamic",
                use_container_width=True,
                key=f"editor_{valda_rutt}"
            )
            
            if st.button("💾 Spara ändringar & Sortera"):
                ny_lista = redigerad_df.sort_values(by="Ordning").to_dict('records')
                st.session_state.rutter[valda_rutt] = ny_lista
                st.success("Listan är nu uppdaterad och sorterad!")
                st.rerun()

# ==========================================
# FLIK 2: KÖRNING (CHAUFFÖR)
# ==========================================
with tab2:
    if not st.session_state.rutter:
        st.info("Inga rutter är redo än.")
    else:
        c_rutt = st.selectbox("Vilken rutt kör du idag?", list(st.session_state.rutter.keys()))
        mina_stopp = [s for s in st.session_state.rutter[c_rutt] if s['Status'] == "Väntar"]
        
        if not mina_stopp:
            st.success("🎉 Alla leveranser klara för denna rutt!")
        else:
            st.header(f"Körschema: {c_rutt}")
            # Visar stoppen i den ordning chefen bestämt
            for i, stopp in enumerate(mina_stopp):
                with st.expander(f"STOPP {stopp['Ordning']}: {stopp['Adress']}", expanded=(i==0)):
                    if stopp['Info']:
                        st.warning(f"ℹ️ **Viktigt:** {stopp['Info']}")
                    
                    st.write(f"Vagnar ut: {stopp['Vagnar']}")
                    
                    # GPS
                    enc_addr = urllib.parse.quote(f"{stopp['Adress']}, Göteborg")
                    st.link_button("🧭 Navigera", f"https://www.google.com/maps/search/?api=1&query={enc_addr}")
                    
                    col1, col2 = st.columns(2)
                    if col1.button("✅ Levererat", key=f"ok_{stopp['ID']}", use_container_width=True):
                        stopp['Status'] = "Levererad"
                        stopp['Tid'] = hämta_tid()
                        st.rerun()
                    
                    if col2.button("⚠️ Problem", key=f"err_{stopp['ID']}", use_container_width=True):
                        st.error("Beskriv felet och ta en bild:")
                        st.camera_input("Foto på hinder", key=f"cam_{stopp['ID']}")
                        if st.button("Skicka felrapport", key=f"rep_{stopp['ID']}"):
                            stopp['Status'] = "Problem"
                            stopp['Tid'] = hämta_tid()
                            st.rerun()

# ==========================================
# FLIK 3: DASHBOARD (CHEF)
# ==========================================
with tab3:
    st.header("🖥️ Realtidsstatus - Göteborg")
    if st.session_state.rutter:
        for r_namn, stopp_lista in st.session_state.rutter.items():
            if stopp_lista:
                klara = len([s for s in stopp_lista if s['Status'] == "Levererad"])
                tot = len(stopp_lista)
                
                with st.container(border=True):
                    c1, c2 = st.columns([1, 3])
                    c1.metric(r_namn, f"{klara}/{tot} Klara")
                    with c2:
                        df_res = pd.DataFrame(stopp_lista)
                        st.dataframe(df_res[["Ordning", "Adress", "Status", "Tid"]], hide_index=True)
    else:
        st.info("Ingen data att visa.")
