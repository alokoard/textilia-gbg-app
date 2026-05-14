import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
import uuid

# --- KONFIGURATION ---
st.set_page_config(page_title="Textilia Gbg - Master Planner", layout="wide")

# Svensk tid (UTC+2)
def hämta_tid():
    return (datetime.utcnow() + timedelta(hours=2)).strftime("%H:%M")

# --- INITIALISERING ---
# Vi sparar allt i en rutt-katalog
if 'rutt_katalog' not in st.session_state:
    st.session_state.rutt_katalog = {} # { "Rutt 1": [stopp1, stopp2], "Rutt 2": [...] }
if 'valda_rutt_id' not in st.session_state:
    st.session_state.valda_rutt_id = "Rutt 1"

st.title("🚛 Textilia Gbg - Master Planner v18.0")

# Sidomeny för att hantera rutter
with st.sidebar:
    st.header("📂 Hantera Rutter")
    ny_rutt_namn = st.text_input("Skapa ny rutt (t.ex. Rutt 5):")
    if st.button("Skapa Rutt"):
        if ny_rutt_namn and ny_rutt_namn not in st.session_state.rutt_katalog:
            st.session_state.rutt_katalog[ny_rutt_namn] = []
            st.session_state.valda_rutt_id = ny_rutt_namn
            st.rerun()

    st.divider()
    all_rutts = list(st.session_state.rutt_katalog.keys())
    if all_rutts:
        st.session_state.valda_rutt_id = st.selectbox("Välj rutt att redigera/se:", all_rutts, index=all_rutts.index(st.session_state.valda_rutt_id))
        
        if st.button("🗑️ Radera valda rutt"):
            del st.session_state.rutt_katalog[st.session_state.valda_rutt_id]
            st.session_state.valda_rutt_id = all_rutts[0] if len(all_rutts) > 1 else "Rutt 1"
            st.rerun()

    st.divider()
    st.header("💾 Backup")
    # Export till JSON
    json_data = json.dumps(st.session_state.rutt_katalog)
    st.download_button("📥 Spara alla rutter till datorn", json_data, file_name=f"textilia_backup_{datetime.now().date()}.json")
    
    # Import från JSON
    uploaded_file = st.file_uploader("📤 Ladda upp sparade rutter", type="json")
    if uploaded_file:
        st.session_state.rutt_katalog = json.load(uploaded_file)
        st.success("Rutter laddade!")

tab1, tab2, tab3 = st.tabs(["🏗️ 1. Planera & Ändra Ordning", "🚚 2. Chaufförsvy", "🖥️ 3. Dashboard"])

# ==========================================
# FLIK 1: PLANERA & ÄNDRA ORDNING (Ditt "Excel")
# ==========================================
with tab1:
    st.header(f"Redigerar: {st.session_state.valda_rutt_id}")
    
    # Lägg till nya stopp
    with st.expander("➕ Lägg till nya adresser"):
        mass_addr = st.text_area("Klistra in adresser (en per rad):")
        default_info = st.text_input("Gemensam info för dessa (valfritt):")
        if st.button("Lägg till i listan"):
            if ny_rutt_namn := st.session_state.valda_rutt_id:
                if ny_rutt_namn not in st.session_state.rutt_katalog:
                    st.session_state.rutt_katalog[ny_rutt_namn] = []
                
                for rad in mass_addr.split("\n"):
                    if rad.strip():
                        # Hitta högsta ordningsnumret
                        nuvarande = st.session_state.rutt_katalog[ny_rutt_namn]
                        nasta_nr = max([s['Ordning'] for s in nuvarande], default=0) + 1
                        
                        st.session_state.rutt_katalog[ny_rutt_namn].append({
                            "ID": str(uuid.uuid4())[:8],
                            "Ordning": nasta_nr,
                            "Adress": rad.strip(),
                            "Info": default_info,
                            "Status": "Väntar",
                            "Vagnar Ut": 10,
                            "Tid": ""
                        })
                st.rerun()

    # REDIGERA TABELLEN (Här kan du ändra allt!)
    if st.session_state.valda_rutt_id in st.session_state.rutt_katalog:
        data = st.session_state.rutt_katalog[st.session_state.valda_rutt_id]
        if data:
            st.subheader("Ändra ordning och info direkt i tabellen:")
            df = pd.DataFrame(data)
            
            # Data Editor låter användaren skriva fritt
            edited_df = st.data_editor(
                df, 
                column_order=["Ordning", "Adress", "Info", "Vagnar Ut", "Status"],
                num_rows="dynamic",
                use_container_width=True,
                key="editor"
            )
            
            if st.button("💾 Spara ändringar i ordning"):
                # Sortera baserat på det nya "Ordning"-numret användaren skrev
                new_data = edited_df.sort_values(by="Ordning").to_dict('records')
                st.session_state.rutt_katalog[st.session_state.valda_rutt_id] = new_data
                st.success("Ordningen sparad!")
                st.rerun()
        else:
            st.info("Inga adresser i denna rutt än.")

# ==========================================
# FLIK 2: CHAUFFÖRSVY
# ==========================================
with tab2:
    all_rutts = list(st.session_state.rutt_katalog.keys())
    if not all_rutts:
        st.info("Inga rutter planerade.")
    else:
        c_rutt = st.selectbox("Välj rutt att köra:", all_rutts, key="chauffeur_sel")
        mina_stopp = [s for s in st.session_state.rutt_katalog[c_rutt] if s['Status'] == "Väntar"]
        
        if not mina_stopp:
            st.success("Rutt klar!")
        else:
            st.header(f"Körschema: {c_rutt}")
            # Chauffören ser alltid listan sorterad efter "Ordning"
            for i, stopp in enumerate(mina_stopp):
                with st.expander(f"STOPP {stopp['Ordning']}: {stopp['Adress']}", expanded=(i==0)):
                    if stopp['Info']:
                        st.warning(f"ℹ️ {stopp['Info']}")
                    
                    st.write(f"Leverera: {stopp['Vagnar Ut']} vagnar")
                    
                    if st.button("✅ Klarmarkera", key=f"btn_{stopp['ID']}"):
                        stopp['Status'] = "Levererad"
                        stopp['Tid'] = hämta_tid()
                        st.rerun()

# ==========================================
# FLIK 3: DASHBOARD
# ==========================================
with tab3:
    st.header("🖥️ Realtidsöversikt")
    if st.session_state.rutt_katalog:
        for r_namn, stopp_lista in st.session_state.rutt_katalog.items():
            if stopp_lista:
                df_dash = pd.DataFrame(stopp_lista)
                klar = len(df_dash[df_dash['Status'] == "Levererad"])
                total = len(df_dash)
                
                st.subheader(f"{r_namn} ({klar}/{total} klara)")
                st.dataframe(df_dash[["Ordning", "Adress", "Status", "Tid", "Info"]], use_container_width=True)
                st.divider()
