import streamlit as st
import pandas as pd

# 1. Sidkonfiguration
st.set_page_config(page_title="Logistikplanering & Orderstyrning", layout="wide")

# =========================================================================
# SYSTEMLAGRING (session_state) - Ser till att ingen data försvinner
# =========================================================================
# Lagring för alla bilars körscheman
if 'all_trucks_data' not in st.session_state:
    st.session_state['all_trucks_data'] = {
        "Bil 1": pd.DataFrame({
            "Ordningsnummer": [1, 2, 3],
            "Adress": [
                "Landvetter Airport 3B1210 438 80 HÄRRYDA", 
                "Sandgärdsgatan 15 503 34 BORÅS", 
                "Härrydavägen 250 438 92 HÄRRYDA"
            ],
            "Status": ["Problem", "Väntar", "Väntar"]
        }),
        "Bil 2": pd.DataFrame({
            "Ordningsnummer": [1, 2],
            "Adress": [
                "Fibervägen 7 435 33 MÖLNLYCKE",
                "Carlbergsgatan 10-14 412 66 GÖTEBORG"
            ],
            "Status": ["Väntar", "Väntar"]
        })
    }

# Lagring för foton (strukturerat per bil och adress)
if 'saved_photos' not in st.session_state:
    st.session_state['saved_photos'] = {}


# --- HUVUDRUBRIK ---
st.title("🚛 Logistikplanering & Orderstyrning")

# Skapa flikar för Chef och Chaufför
flik_chef, flik_chauffor = st.tabs(["👨‍💼 Chefsvy - Hantera Bilar & Rutter", "🚚 Chaufförsvy - Körschema & Kamera"])


# =========================================================================
# 👨‍💼 FLIK 1: CHEFENS DEL (Hantera flera bilar och rutter)
# =========================================================================
with flik_chef:
    st.header("Administrera Fordon och Körlistor")
    
    # Sektion A: Lägg till en helt ny bil i systemet
    st.subheader("➕ Lägg till ny bil")
    nytt_bilsnamn = st.text_input("Ange namn på ny bil (t.ex. 'Bil 3'):").strip()
    if st.button("Registrera nytt fordon"):
        if nytt_bilsnamn and nytt_bilsnamn not in st.session_state['all_trucks_data']:
            st.session_state['all_trucks_data'][nytt_bilsnamn] = pd.DataFrame(columns=["Ordningsnummer", "Adress", "Status"])
            st.success(f"{nytt_bilsnamn} har lagts till i systemet!")
            st.rerun()
        elif nytt_bilsnamn:
            st.warning("Det fordonet finns redan.")

    st.write("---")

    # Sektion B: Uppdatera rutt för en specifik bil
    st.subheader("✏️ Uppdatera rutt för valt fordon")
    valda_bilar_lista = list(st.session_state['all_trucks_data'].keys())
    chef_vald_bil = st.selectbox("Välj vilken bil du vill hantera:", valda_bilar_lista, key="chef_bil_select")
    
    # Hämta nuvarande adresser för den valda bilen för att visa i textrutan
    nuvarande_df = st.session_state['all_trucks_data'][chef_vald_bil]
    nuvarande_text = "\n".join(nuvarande_df["Adress"].tolist()) if not nuvarande_df.empty else ""
    
    ny_data_text = st.text_area(
        f"Klistra in adresser för {chef_vald_bil} (en adress per rad):",
        value=nuvarande_text,
        height=150
    )
    
    if st.button(f"Spara och optimera körordning för {chef_vald_bil}"):
        nya_adresser = [line.strip() for line in ny_data_text.split("\n") if line.strip()]
        
        # Bygg upp den nya tabellen för just den valda bilen
        ny_df = pd.DataFrame({
            "Ordningsnummer": list(range(1, len(nya_adresser) + 1)),
            "Adress": nya_adresser,
            "Status": ["Väntar"] * len(nya_adresser)
        })
        
        # Spara tillbaka till den specifika bilen i vårt systemminne
        st.session_state['all_trucks_data'][chef_vald_bil] = ny_df
        st.success(f"Körschemat för {chef_vald_bil} har uppdaterats!")
        st.rerun()


# =========================================================================
# 🚚 FLIK 2: CHAUFFÖRENS DEL (Välj bil, se rutt & ta foto)
# =========================================================================
with flik_chauffor:
    st.header("Chaufförsportal")
    
    # Chauffören måste välja vilken bil de kör just nu
    alla_tillgangliga_bilar = list(st.session_state['all_trucks_data'].keys())
    chauffor_vald_bil = st.selectbox("Välj vilket fordon du kör idag:", alla_tillgangliga_bilar, key="chauffor_bil_select")
    
    # Hämta rätt körschema baserat på valet av bil
    bil_df = st.session_state['all_trucks_data'][chauffor_vald_bil]
    
    st.subheader(f"Körschema för {chauffor_vald_bil}")
    
    if not bil_df.empty:
        # Visa tabellen för den valda bilen
        st.dataframe(bil_df, use_container_width=True, hide_index=True)
        
        # --- FOTODOKUMENTATION ---
        st.write("---")
        st.subheader("📸 Fotoverifiering & Avvikelsehantering")
        
        # Hämta adresserna för just denna bil till rullistan
        bilens_adresser = bil_df["Adress"].tolist()
        vald_adress = st.selectbox(f"Välj adress i {chauffor_vald_bil} att dokumentera:", bilens_adresser)
        
        # Kameran aktiveras
        photo_input = st.camera_input("Ta kort för att bekräfta leverans eller rapportera problem")
        
        # Skapa en unik nyckel för fotolagringen baserat på både bil och adress
        foto_nyckel = f"{chauffor_vald_bil}_{vald_adress}"
        
        if photo_input:
            # Spara fotot under sin unika nyckel
            st.session_state['saved_photos'][foto_nyckel] = photo_input
            st.success(f"Foto registrerat för {vald_adress.split()[0]} på {chauffor_vald_bil}!")
            st.rerun()
            
        # FIXEN: Hämtar och visar fotot direkt på skärmen så det inte försvinner
        if foto_nyckel in st.session_state['saved_photos']:
            st.write("✅ **Registrerat foto för denna adress:**")
            st.image(st.session_state['saved_photos'][foto_nyckel], caption=f"Foto: {vald_adress}", width=400)
            
        # --- LIVE STATUS (Dynamiska mätare för vald bil) ---
        st.write("---")
        st.subheader(f"Live Status - {chauffor_vald_bil}")
        
        totalt = len(bil_df)
        klara = len(bil_df[bil_df["Status"] == "Klar"])
        problem = len(bil_df[bil_df["Status"] == "Problem"])
        aterstar = totalt - klara
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Totalt antal stopp", value=f"{totalt} st")
        with col2:
            procent = f"{(klara/totalt)*100:.0f}%" if totalt > 0 else "0%"
            st.metric(label="Utförda leveranser", value=f"{klara} st", delta=procent)
        with col3:
            st.metric(label="Aktiva avvikelser / Problem", value=f"{problem} st", delta=f"{aterstar} återstår", delta_color="inverse")
            
    else:
        st.info(f"Det finns inga registrerade adresser för {chauffor_vald_bil} just nu. Gå till Chefsvyn för att lägga till en rutt.")
