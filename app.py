import streamlit as st
import pandas as pd

# 1. Sidkonfiguration
st.set_page_config(page_title="Logistikplanering & Orderstyrning", layout="wide")

# 2. Initiera session_state så att data sparas mellan flikar och sidomladdningar
if 'saved_photos' not in st.session_state:
    st.session_state['saved_photos'] = {}

# Om det inte finns någon sparad körlista än, skapar vi en standardlista
if 'korlista_df' not in st.session_state:
    initial_data = {
        "Ordningsnummer": [0, 1, 2, 3],
        "Adress": [
            "Landvetter Airport 3B1210 438 80 HÄRRYDA", 
            "Sandgärdsgatan 15 503 34 BORÅS", 
            "Härrydavägen 250 438 92 HÄRRYDA",
            "Kungsportsavenyen 10 411 36 GÖTEBORG"
        ],
        "Status": ["Problem", "Väntar", "Väntar", "Klar"]
    }
    st.session_state['korlista_df'] = pd.DataFrame(initial_data)

# --- HUVUDRUBRIK ---
st.title("Logistikplanering & Orderstyrning")

# 3. Skapa flikar för de olika vyerna (Chef och Chaufför)
flik_chef, flik_chauffor = st.tabs(["👨‍💼 Chefsvy - Hantera & Mata in listor", "🚚 Chaufförsvy - Körschema"])


# =========================================================================
# 👨‍💼 FLIK 1: CHEFENS DEL (Inmatning och hantering av listor)
# =========================================================================
with flik_chef:
    st.header("Administrera Körlistor")
    
    st.subheader("Skapa eller uppdatera lista")
    st.write("Här kan du klistra in eller mata in nya adresser och rutter till chaufförerna.")
    
    # Textruta för att kunna klistra in adresser direkt (eller rader)
    ny_data_text = st.text_area(
        "Klistra in adresser (en per rad) för att uppdatera listan:",
        value="\n".join(st.session_state['korlista_df']["Adress"].tolist()),
        height=150
    )
    
    if st.button("Uppdatera körschema för Bil 1"):
        # Dela upp texten till en lista av adresser
        nya_adresser = [line.strip() for line in ny_data_text.split("\n") if line.strip()]
        
        # Skapa en ny DataFrame med nollställd status
        ny_df = pd.DataFrame({
            "Ordningsnummer": list(range(len(nya_adresser))),
            "Adress": nya_adresser,
            "Status": ["Väntar"] * len(nya_adresser)
        })
        
        # Spara i session_state så att Chaufförs-fliken ser ändringen direkt
        st.session_state['korlista_df'] = ny_df
        st.success("Körschemat har uppdaterats och skickats till chauffören!")


# =========================================================================
# 🚚 FLIK 2: CHAUFFÖRENS DEL (Körschema, Status & Kamera)
# =========================================================================
with flik_chauffor:
    # Hämta den aktuella listan från minnet
    current_df = st.session_state['korlista_df']
    
    st.subheader("Körschema för Bil 1")
    
    # Visa tabellen precis som på din bild
    st.dataframe(current_df, use_container_width=True, hide_index=True)
    
    # --- NY FOTOFUNKTION SOM DU BAD OM ---
    st.write("---")
    st.subheader("📸 Fotoverifiering & Avvikelsehantering")
    
    # Rullista med adresserna från den aktuella listan
    alla_adresser = current_df["Adress"].tolist()
    if alla_adresser:
        vald_adress = st.selectbox("Välj vilken adress fotot tillhör:", alla_adresser)
        
        # Kamera-komponenten
        photo_input = st.camera_input("Ta kort för att dokumentera status eller problem")
        
        if photo_input:
            # Spara fotot i minnet kopplat till just denna adress
            st.session_state['saved_photos'][vald_adress] = photo_input
            st.success(f"Foto har registrerats för: {vald_adress.split()[0]}!")
        
        # HÄR ÄR FIXEN: Visar bilden direkt så den INTE försvinner efter man tagit kortet
        if vald_adress in st.session_state['saved_photos']:
            st.write(f"✅ **Registrerat foto för denna adress:**")
            st.image(st.session_state['saved_photos'][vald_adress], caption=f"Foto för {vald_adress}", width=400)
    else:
        st.warning("Det finns inga adresser i listan ännu. Chefen måste lägga till adresser först.")


    # --- LIVE STATUS MÄTARE (Längst ner på chaufförssidan) ---
    st.write("---")
    st.subheader("Live Status")
    
    # Räkna ut statistik dynamiskt baserat på listan
    totalt = len(current_df)
    klara = len(current_df[current_df["Status"] == "Klar"])
    aterstar = totalt - klara
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Antal Adresser", value=f"{totalt} st")
    with col2:
        procent = f"{(klara/totalt)*100:.0f}%" if totalt > 0 else "0%"
        st.metric(label="Klara", value=f"{klara} st", delta=procent)
    with col3:
        st.metric(label="Återstår", value=f"{aterstar} st")
