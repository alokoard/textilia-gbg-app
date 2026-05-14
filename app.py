import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from datetime import datetime
from zoneinfo import ZoneInfo
import urllib.parse
import uuid
import time

# =====================================================
# KONFIGURATION
# =====================================================
st.set_page_config(
    page_title="Textilia Gbg - Logistikkedjan",
    page_icon="🧺",
    layout="wide"
)

CHEFSKOD = "textilia2026"
DEFAULT_DEPO = {
    "namn": "Depå Textilia Göteborg",
    "adress": "Fjällbo Park 5, Göteborg",
    "lat": 57.7409,
    "lon": 12.0634,
}

# =====================================================
# SESSION STATE
# =====================================================
def initiera_session():
    defaults = {
        "fleet": [],
        "rutten": [],
        "depo": DEFAULT_DEPO,
        "vald_fordon": None,
        "chef_inloggad": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

initiera_session()

# =====================================================
# HJÄLPFUNKTIONER
# =====================================================
def svensk_tid():
    return datetime.now(ZoneInfo("Europe/Stockholm")).strftime("%H:%M")


def svensk_datum_tid():
    return datetime.now(ZoneInfo("Europe/Stockholm")).strftime("%Y-%m-%d %H:%M")


@st.cache_data(show_spinner=False)
def hamta_gps(adress: str):
    """Hämtar koordinater via OpenStreetMap/Nominatim. Cache används för att minska antal anrop."""
    if not adress or not adress.strip():
        return None, None

    try:
        geolocator = Nominatim(user_agent="textilia_gbg_logistik_app")
        query = f"{adress}, Göteborg, Sweden"
        loc = geolocator.geocode(query, timeout=10)
        time.sleep(1)  # Nominatim bör inte belastas med många snabba anrop.
        if loc:
            return loc.latitude, loc.longitude
    except Exception:
        pass

    return None, None


def skapa_stopp(adress: str, vagnar_ut: int, prio: int = 2):
    lat, lon = hamta_gps(adress)
    return {
        "id": str(uuid.uuid4()),
        "stopp_nr": None,
        "adress": adress.strip(),
        "prio": prio,
        "vagnar_ut": int(vagnar_ut),
        "vagnar_in": 0,
        "lat": lat,
        "lon": lon,
        "status": "Planerad",
        "info": "",
        "problem": False,
        "problem_text": "",
        "tid": "",
        "leverans_tidpunkt": "",
    }


def optimera_rutt(stopp_lista):
    """En enkel närmaste-stopp-optimering. Prio 1 hamnar först, därefter närmaste stopp från depån."""
    if not stopp_lista:
        return []

    prio_stopp = [s for s in stopp_lista if s.get("prio", 2) == 1]
    ovriga = [s for s in stopp_lista if s.get("prio", 2) != 1]

    sorterad = []
    nuvarande_pos = (st.session_state.depo["lat"], st.session_state.depo["lon"])

    # Lägg prioriterade stopp först i den ordning de skrevs in.
    for stopp in prio_stopp:
        sorterad.append(stopp)
        if stopp.get("lat") is not None and stopp.get("lon") is not None:
            nuvarande_pos = (stopp["lat"], stopp["lon"])

    med_gps = [s for s in ovriga if s.get("lat") is not None and s.get("lon") is not None]
    utan_gps = [s for s in ovriga if s.get("lat") is None or s.get("lon") is None]

    while med_gps:
        narmsta = min(
            med_gps,
            key=lambda s: geodesic(nuvarande_pos, (s["lat"], s["lon"])).km,
        )
        sorterad.append(narmsta)
        nuvarande_pos = (narmsta["lat"], narmsta["lon"])
        med_gps.remove(narmsta)

    sorterad.extend(utan_gps)

    for index, stopp in enumerate(sorterad, start=1):
        stopp["stopp_nr"] = index

    return sorterad


def total_kapacitet():
    if not st.session_state.vald_fordon:
        return 0
    for f in st.session_state.fleet:
        if f["id"] == st.session_state.vald_fordon:
            return f["cap"]
    return 0


def rakna_total_vagnar_ut():
    return sum(int(s.get("vagnar_ut", 0)) for s in st.session_state.rutten)


def google_maps_lank(adress: str):
    query = urllib.parse.quote(f"{adress}, Göteborg")
    return f"https://www.google.com/maps/search/?api=1&query={query}"


def visa_status_badge(status):
    if status == "Levererad":
        return "✅ Levererad"
    if status == "Pågående":
        return "🚚 Pågående"
    return "🕒 Planerad"

# =====================================================
# SIDOMENY
# =====================================================
st.sidebar.title("🧺 Textilia Gbg")
st.sidebar.caption("Logistikflöde: planering, lastning, leverans och retur")

pwd = st.sidebar.text_input("Chefskod", type="password")
if pwd == CHEFSKOD:
    st.session_state.chef_inloggad = True
    st.sidebar.success("Inloggad som chef/planerare")
elif pwd:
    st.sidebar.error("Fel kod")

st.sidebar.divider()
st.sidebar.subheader("Depå")
st.sidebar.write(st.session_state.depo["namn"])
st.sidebar.caption(st.session_state.depo["adress"])

if st.sidebar.button("🔴 Nollställ hela dagen"):
    st.session_state.rutten = []
    st.session_state.fleet = []
    st.session_state.vald_fordon = None
    st.rerun()

# =====================================================
# HEADER
# =====================================================
st.title("🧺 Textilia Gbg Logistik – Hela kedjan")
st.caption(f"Senast uppdaterad: {svensk_datum_tid()}")

tab1, tab2, tab3, tab4 = st.tabs([
    "🏗️ 1. Planering",
    "📦 2. Lastning",
    "🚚 3. Chaufför",
    "🖥️ 4. Dashboard",
])

# =====================================================
# FLIK 1: PLANERING
# =====================================================
with tab1:
    st.header("🏗️ Planering på kontoret")

    if not st.session_state.chef_inloggad:
        st.warning("Ange chefskod i sidomenyn för att planera fordon och rutter.")
    else:
        c1, c2 = st.columns([1, 2])

        with c1:
            st.subheader("🚛 Fordon och chaufför")
            v_id = st.text_input("Bil/chaufför-ID", placeholder="Exempel: Bil 12 - Ahmed")
            v_typ = st.selectbox("Fordonstyp", ["Singelbil", "Lastbil + släp"])
            cap_bil = st.number_input("Kapacitet bil, antal vagnar", min_value=1, value=70)
            cap_slap = 0
            if v_typ == "Lastbil + släp":
                cap_slap = st.number_input("Kapacitet släp, antal vagnar", min_value=1, value=30)

            if st.button("➕ Spara fordon", use_container_width=True):
                if not v_id.strip():
                    st.error("Skriv bil/chaufför-ID först.")
                else:
                    st.session_state.fleet.append({
                        "id": v_id.strip(),
                        "typ": v_typ,
                        "cap": int(cap_bil + cap_slap),
                    })
                    st.success("Fordon sparat.")

            if st.session_state.fleet:
                fordonslista = [f["id"] for f in st.session_state.fleet]
                st.session_state.vald_fordon = st.selectbox(
                    "Välj fordon till rutten",
                    fordonslista,
                    index=0,
                )
                vald = next(f for f in st.session_state.fleet if f["id"] == st.session_state.vald_fordon)
                st.info(f"Vald kapacitet: {vald['cap']} vagnar")

        with c2:
            st.subheader("📍 Skapa rutt")
            st.caption("Skriv en adress per rad. Du kan lägga viktiga stopp med prioritet 1 om de måste köras först.")

            mass_addr = st.text_area(
                "Adresser",
                height=180,
                placeholder="Exempel:\nSahlgrenska, Göteborg\nÖstra sjukhuset, Göteborg\nMölndals sjukhus, Göteborg",
            )

            c21, c22 = st.columns(2)
            with c21:
                vagnar_ut = st.number_input("Rena vagnar ut per stopp", min_value=0, value=10)
            with c22:
                prio = st.selectbox("Standardprioritet", [2, 1], format_func=lambda x: "Normal" if x == 2 else "Viktig först")

            if st.button("⚡ Optimera och skapa rutt", use_container_width=True):
                adresser = [rad.strip() for rad in mass_addr.split("\n") if rad.strip()]

                if not adresser:
                    st.error("Skriv minst en adress.")
                elif not st.session_state.vald_fordon:
                    st.error("Spara och välj ett fordon först.")
                else:
                    with st.spinner("Hämtar GPS och optimerar rutten..."):
                        temp = [skapa_stopp(adress, vagnar_ut, prio) for adress in adresser]
                        st.session_state.rutten = optimera_rutt(temp)
                    st.success("Rutten är skapad och optimerad.")
                    st.rerun()

        if st.session_state.rutten:
            st.divider()
            st.subheader("📝 Viktig information till chauffören")

            for stopp in st.session_state.rutten:
                with st.expander(f"Stopp {stopp['stopp_nr']}: {stopp['adress']}"):
                    stopp["info"] = st.text_input(
                        "Information",
                        value=stopp.get("info", ""),
                        key=f"info_{stopp['id']}",
                        placeholder="Exempel: Ring kund innan leverans, portkod, lämna vid lastkaj...",
                    )
                    stopp["vagnar_ut"] = st.number_input(
                        "Rena vagnar ut",
                        min_value=0,
                        value=int(stopp.get("vagnar_ut", 0)),
                        key=f"vut_{stopp['id']}",
                    )

            kapacitet = total_kapacitet()
            total_ut = rakna_total_vagnar_ut()
            st.divider()
            if kapacitet and total_ut > kapacitet:
                st.error(f"Överlast: {total_ut} vagnar planerade men fordonets kapacitet är {kapacitet} vagnar.")
            else:
                st.success(f"Planerad last: {total_ut} av {kapacitet} vagnar.")

# =====================================================
# FLIK 2: LASTNING
# =====================================================
with tab2:
    st.header("📦 Lastning på lagret")

    if not st.session_state.rutten:
        st.info("Ingen rutt är planerad ännu.")
    else:
        st.info("Lasta enligt LIFO: sista stoppet lastas först, så första stoppet hamnar lättast att ta ut.")

        last_lista = sorted(st.session_state.rutten, key=lambda x: x["stopp_nr"], reverse=True)
        df_last = pd.DataFrame(last_lista)
        df_last["lastordning"] = range(1, len(df_last) + 1)

        st.dataframe(
            df_last[["lastordning", "stopp_nr", "adress", "vagnar_ut", "info"]],
            use_container_width=True,
            hide_index=True,
        )

        st.subheader("Kapacitetskontroll")
        kapacitet = total_kapacitet()
        total_ut = rakna_total_vagnar_ut()
        st.progress(min(total_ut / kapacitet, 1.0) if kapacitet else 0)
        st.write(f"{total_ut} av {kapacitet} vagnar planerade.")

# =====================================================
# FLIK 3: CHAUFFÖR
# =====================================================
with tab3:
    st.header("🚚 Chaufförsläge")

    if not st.session_state.rutten:
        st.info("Ingen rutt är planerad ännu.")
    else:
        kvar = [s for s in st.session_state.rutten if s["status"] != "Levererad"]

        if not kvar:
            st.success("🎉 Alla leveranser är klara. Kör tillbaka till tvätteriet med returtvätten.")
        else:
            s = kvar[0]
            s["status"] = "Pågående"

            st.subheader(f"Nästa stopp: {s['adress']}")
            st.caption(f"Stopp {s['stopp_nr']} av {len(st.session_state.rutten)}")

            if s.get("info"):
                st.warning(f"⚠️ Info: {s['info']}")

            st.link_button("🧭 Öppna i Google Maps", google_maps_lank(s["adress"]), use_container_width=True)

            c31, c32 = st.columns(2)
            with c31:
                st.metric("Rena vagnar att lämna", s.get("vagnar_ut", 0))
            with c32:
                vagnar_in = st.number_input(
                    "Hämtad smutstvätt, antal vagnar",
                    min_value=0,
                    value=int(s.get("vagnar_ut", 0)),
                    key=f"vin_{s['id']}",
                )

            col1, col2 = st.columns(2)
            if col1.button("✅ Levererat och hämtat", use_container_width=True):
                s["status"] = "Levererad"
                s["vagnar_in"] = int(vagnar_in)
                s["tid"] = svensk_tid()
                s["leverans_tidpunkt"] = svensk_datum_tid()
                st.rerun()

            if col2.button("⚠️ Rapportera problem", use_container_width=True):
                s["problem"] = True

            if s.get("problem"):
                s["problem_text"] = st.text_area(
                    "Beskriv problemet",
                    value=s.get("problem_text", ""),
                    key=f"problemtext_{s['id']}",
                    placeholder="Exempel: Ingen på plats, blockerad lastkaj, fel antal vagnar...",
                )
                st.camera_input("Ta bild på hinder eller avvikelse", key=f"cam_{s['id']}")

# =====================================================
# FLIK 4: DASHBOARD
# =====================================================
with tab4:
    st.header("🖥️ Dashboard i realtid")

    if not st.session_state.rutten:
        st.info("Ingen data att visa ännu.")
    else:
        df = pd.DataFrame(st.session_state.rutten)

        klara = len(df[df["status"] == "Levererad"])
        totalt = len(df)
        total_ut = int(df["vagnar_ut"].sum())
        total_in = int(df["vagnar_in"].sum())
        problem = int(df["problem"].sum())

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Klara stopp", f"{klara}/{totalt}")
        c2.metric("Rena vagnar ut", total_ut)
        c3.metric("Smutsiga vagnar retur", total_in)
        c4.metric("Problem", problem)

        st.progress(klara / totalt if totalt else 0)

        st.divider()
        st.subheader("Leveranslogg")
        df_visning = df.copy()
        df_visning["status"] = df_visning["status"].apply(visa_status_badge)

        st.dataframe(
            df_visning[[
                "stopp_nr",
                "adress",
                "status",
                "tid",
                "vagnar_ut",
                "vagnar_in",
                "info",
                "problem_text",
            ]],
            use_container_width=True,
            hide_index=True,
        )

        st.subheader("Karta")
        df_map = df.dropna(subset=["lat", "lon"])
        if not df_map.empty:
            st.map(df_map, latitude="lat", longitude="lon", size=80)
        else:
            st.warning("Inga GPS-positioner kunde hittas för adresserna.")

        st.divider()
        csv = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "⬇️ Ladda ner körlogg som CSV",
            data=csv,
            file_name="textilia_korlogg.csv",
            mime="text/csv",
            use_container_width=True,
        )
