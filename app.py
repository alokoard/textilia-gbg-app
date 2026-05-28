import streamlit as st
import pandas as pd

# Sätt sidkonfiguration
st.set_page_config(page_title="Logistikplanering & Orderstyrning", layout="wide")

# Initiera lagring för foton i session_state så de inte försvinner när sidan laddas om
if 'saved_photos' not in st.session_state:
    st.session_state['saved_photos'] = {}

# --- HUVUDTITEL ---
st.title("Logistikplanering & Orderstyrning")

# --- SEKTION: KÖRSCHEMA ---
st.subheader("Körschema för Bil 1")

# Skapa testdata baserat på layouten i din bild
data = {
    "Ordningsnummer": [0, 1, 2, 3],
    "Adress": [
        "Landvetter Airport 3B1210 438 80 HÄRRYDA", 
        "Sandgärdsgatan 15 503 34 BORÅS", 
        "Härrydavägen 250 438 92 HÄRRYDA",
        "Kungsportsavenyen 10 411 36 GÖTEBORG"
    ],
    "Status": ["Problem", "Väntar", "Väntar", "Klar"]
}
df = pd.DataFrame(data)

# Visa tabellen i appen
st.dataframe(df, use_container_width=True, hide_index=True)


# --- SEKTION: FOTODOKUMENTATION (NY FUNKTION) ---
st.write("---")
st.subheader("📸 Fotoverifiering & Avvikelsehantering")

# Låt chauffören välja vilken adress fotot hör till från tabellen
alla_adresser = df["Adress"].tolist()
vald_adress = st.selectbox("Välj vilken adress du vill dokumentera eller ta kort för:", alla_adresser)

# Kamerakomponent
photo_input = st.camera_input("Ta kort för att verifiera leverans eller rapportera problem")

# Om ett foto tas, spara det i minnet kopplat till den valda adressen
if photo_input:
    st.session_state['saved_photos'][vald_adress] = photo_input
    st.success(f"Foto har registrerats och sparats för: {vald_adress.split()[0]}!")

# VIKTIGT: Denna del ser till att bilden ritas ut på skärmen direkt och stannar kvar!
if vald_adress in st.session_state['saved_photos']:
    st.write(f"✅ **Registrerat foto för denna adress:**")
    st.image(st.session_state['saved_photos'][vald_adress], caption=f"Foto för {vald_adress}", width=400)


# --- SEKTION: LIVE STATUS ---
st.write("---")
st.subheader("Live Status")

# Skapa tre kolumner för dina mätartavlor (metrics) längst ner
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Antal Adresser", value="4 st")
with col2:
    st.metric(label="Klara", value="1 st", delta="25%")
with col3:
    st.metric(label="Återstår", value="3 st", delta="-1", delta_color="inverse")
