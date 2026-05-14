import streamlit as st
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
import json
import uuid
import urllib.parse

# =====================================================
# KONFIGURATION
# =====================================================
st.set_page_config(
    page_title="Textilia Gbg - Master Planner",
    page_icon="🚛",
    layout="wide"
)

APP_VERSION = "v19.0"
CHEFSKOD = "textilia2026"

STATUSAR = ["Väntar", "Pågående", "Levererad", "Problem", "Avbruten"]
FORDON_TYPER = ["Singelbil", "Lastbil + släp", "Liten bil", "Extra tur"]

# =====================================================
# TID OCH HJÄLPFUNKTIONER
# =====================================================
def svensk_tid():
    return datetime.now(ZoneInfo("Europe/Stockholm")).strftime("%H:%M")


def svensk_datum_tid():
    return datetime.now(ZoneInfo("Europe/Stockholm")).strftime("%Y-%m-%d %H:%M")


def skapa_id():
    return str(uuid.uuid4())[:8]


def maps_lank(adress):
    query = urllib.parse.quote(f"{adress}, Sverige")
    return f"https://www.google.com/maps/search/?api=1&query={query}"


def tomt_stopp(ordning=1):
    return {
        "ID": skapa_id(),
        "Ordning": ordning,
        "Kund": "",
        "Adress": "",
        "Info": "",
        "Status": "Väntar",
        "Vagnar Ut": 10,
        "Vagnar In": 0,
        "Prioritet": "Normal",
        "Leveransfönster": "",
        "Chaufför": "",
        "Fordon": "",
        "Problemtext": "",
        "Tid": "",
        "Senast ändrad": svensk_datum_tid(),
    }


def normalisera_stopp(stopp, ordning_fallback=1):
    """Gör gamla importerade stopp kompatibla med nya versionen."""
    mall = tomt_stopp(ordning_fallback)
    mall.update(stopp)

    if not mall.get("ID"):
        mall["ID"] = skapa_id()
    if not mall.get("Ordning"):
        mall["Ordning"] = ordning_fallback
    if mall.get("Status") not in STATUSAR:
        mall["Status"] = "Väntar"

    for fält in ["Vagnar Ut", "Vagnar In", "Ordning"]:
        try:
            mall[fält] = int(mall.get(fält, 0))
        except Exception:
            mall[fält] = 0

    return mall


def sortera_rutt(stopp_lista):
    stopp_lista = [normalisera_stopp(s, i + 1) for i, s in enumerate(stopp_lista)]
    stopp_lista = sorted(stopp_lista, key=lambda x: int(x.get("Ordning", 9999)))
    for i, stopp in enumerate(stopp_lista, start=1):
        stopp["Ordning"] = i
    return stopp_lista


def status_emoji(status):
    return {
        "Väntar": "🕒 Väntar",
        "Pågående": "🚚 Pågående",
        "Levererad": "✅ Levererad",
        "Problem": "⚠️ Problem",
        "Avbruten": "⛔ Avbruten",
    }.get(status, status)


def hamta_rutt(rutt_id):
    if rutt_id not in st.session_state.rutt_katalog:
        st.session_state.rutt_katalog[rutt_id] = []
    st.session_state.rutt_katalog[rutt_id] = sortera_rutt(st.session_state.rutt_katalog[rutt_id])
    return st.session_state.rutt_katalog[rutt_id]


def totaler_for_rutt(stopp_lista):
    if not stopp_lista:
        return 0, 0, 0, 0
    total = len(stopp_lista)
    klara = len([s for s in stopp_lista if s.get("Status") == "Levererad"])
    ut = sum(int(s.get("Vagnar Ut", 0)) for s in stopp_lista)
    returer = sum(int(s.get("Vagnar In", 0)) for s in stopp_lista)
    return total, klara, ut, returer


def exportera_backup():
    data = {
        "version": APP_VERSION,
        "exporterad": svensk_datum_tid(),
        "rutter": st.session_state.rutt_katalog,
        "fordon": st.session_state.fordon,
        "chaufforer": st.session_state.chaufforer,
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


def importera_backup(fil):
    data = json.load(fil)

    # Stöd både gamla backupformatet och nya formatet.
    if "rutter" in data:
        st.session_state.rutt_katalog = data.get("rutter", {})
        st.session_state.fordon = data.get("fordon", st.session_state.fordon)
        st.session_state.chaufforer = data.get("chaufforer", st.session_state.chaufforer)
    else:
        st.session_state.rutt_katalog = data

    for rutt_id in list(st.session_state.rutt_katalog.keys()):
        st.session_state.rutt_katalog[rutt_id] = sortera_rutt(st.session_state.rutt_katalog[rutt_id])

# =====================================================
# SESSION STATE
# =====================================================
def init_session():
    if "rutt_katalog" not in st.session_state:
        st.session_state.rutt_katalog = {"Rutt 1": []}
    if "valda_rutt_id" not in st.session_state:
        st.session_state.valda_rutt_id = "Rutt 1"
    if "fordon" not in st.session_state:
        st.session_state.fordon = [
            {"Fordon": "Bil 1", "Typ": "Singelbil", "Kapacitet": 70},
            {"Fordon": "Bil 2", "Typ": "Lastbil + släp", "Kapacitet": 100},
        ]
    if "chaufforer" not in st.session_state:
        st.session_state.chaufforer = ["Chaufför 1", "Chaufför 2", "Chaufför 3"]
    if "chef_inloggad" not in st.session_state:
        st.session_state.chef_inloggad = False

    # Säkerställ att vald rutt finns.
    if st.session_state.valda_rutt_id not in st.session_state.rutt_katalog:
        st.session_state.valda_rutt_id = list(st.session_state.rutt_katalog.keys())[0]

init_session()

# =====================================================
# SIDOMENY
# =====================================================
with st.sidebar:
    st.title("🚛 Master Planner")
    st.caption(f"Textilia Gbg {APP_VERSION}")

    kod = st.text_input("Chefskod", type="password")
    if kod == CHEFSKOD:
        st.session_state.chef_inloggad = True
        st.success("Inloggad")
    elif kod:
        st.error("Fel kod")

    st.divider()
    st.header("📂 Rutter")

    ny_rutt_namn = st.text_input("Skapa ny rutt", placeholder="Exempel: Rutt 5")
    if st.button("➕ Skapa rutt", use_container_width=True):
        namn = ny_rutt_namn.strip()
        if not namn:
            st.warning("Skriv ett ruttnamn först.")
        elif namn in st.session_state.rutt_katalog:
            st.warning("Den rutten finns redan.")
        else:
            st.session_state.rutt_katalog[namn] = []
            st.session_state.valda_rutt_id = namn
            st.rerun()

    all_rutter = list(st.session_state.rutt_katalog.keys())
    if all_rutter:
        if st.session_state.valda_rutt_id not in all_rutter:
            st.session_state.valda_rutt_id = all_rutter[0]

        st.session_state.valda_rutt_id = st.selectbox(
            "Välj rutt",
            all_rutter,
            index=all_rutter.index(st.session_state.valda_rutt_id),
        )

        if st.button("🗑️ Radera vald rutt", use_container_width=True):
            if len(all_rutter) == 1:
                st.warning("Du måste ha minst en rutt kvar.")
            else:
                del st.session_state.rutt_katalog[st.session_state.valda_rutt_id]
                st.session_state.valda_rutt_id = list(st.session_state.rutt_katalog.keys())[0]
                st.rerun()

    st.divider()
    st.header("💾 Backup")
    st.download_button(
        "📥 Spara backup",
        data=exportera_backup(),
        file_name=f"textilia_backup_{datetime.now().date()}.json",
        mime="application/json",
        use_container_width=True,
    )

    uploaded_file = st.file_uploader("📤 Ladda upp backup", type="json")
    if uploaded_file:
        try:
            importera_backup(uploaded_file)
            st.success("Backup laddad.")
            st.rerun()
        except Exception as e:
            st.error(f"Kunde inte läsa filen: {e}")

    st.divider()
    if st.button("🔴 Nollställ allt", use_container_width=True):
        st.session_state.rutt_katalog = {"Rutt 1": []}
        st.session_state.valda_rutt_id = "Rutt 1"
        st.rerun()

# =====================================================
# HUVUDRUBRIK
# =====================================================
st.title("🚛 Textilia Gbg - Master Planner")
st.caption(f"Planering, lastning, chaufförsvy, returflöde och dashboard. Senast uppdaterad: {svensk_datum_tid()}")

vald_rutt_id = st.session_state.valda_rutt_id
vald_rutt = hamta_rutt(vald_rutt_id)

total, klara, ut, returer = totaler_for_rutt(vald_rutt)

k1, k2, k3, k4 = st.columns(4)
k1.metric("Vald rutt", vald_rutt_id)
k2.metric("Klara stopp", f"{klara}/{total}")
k3.metric("Rena vagnar ut", ut)
k4.metric("Smutstvätt retur", returer)

if total:
    st.progress(klara / total)

# =====================================================
# TABS
# =====================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏗️ 1. Planera",
    "📦 2. Lastning",
    "🚚 3. Chaufför",
    "🖥️ 4. Dashboard",
    "⚙️ 5. Register",
])

# =====================================================
# FLIK 1: PLANERA
# =====================================================
with tab1:
    st.header(f"🏗️ Planera och ändra: {vald_rutt_id}")

    if not st.session_state.chef_inloggad:
        st.warning("Logga in med chefskod i sidomenyn för att kunna ändra planeringen.")
    else:
        with st.expander("➕ Lägg till flera adresser", expanded=not bool(vald_rutt)):
            mass_addr = st.text_area(
                "Klistra in adresser, en per rad",
                height=160,
                placeholder="Exempel:\nSahlgrenska sjukhuset, Göteborg\nÖstra sjukhuset, Göteborg\nMölndals sjukhus, Göteborg",
            )

            c1, c2, c3, c4 = st.columns(4)
            with c1:
                default_kund = st.text_input("Kund/avdelning", placeholder="Valfritt")
            with c2:
                default_info = st.text_input("Gemensam info", placeholder="Portkod, lastkaj...")
            with c3:
                default_vagnar = st.number_input("Vagnar ut", min_value=0, value=10)
            with c4:
                default_prio = st.selectbox("Prioritet", ["Normal", "Hög"])

            c5, c6 = st.columns(2)
            with c5:
                default_chauffor = st.selectbox("Chaufför", [""] + st.session_state.chaufforer)
            with c6:
                fordonsnamn = [f["Fordon"] for f in st.session_state.fordon]
                default_fordon = st.selectbox("Fordon", [""] + fordonsnamn)

            if st.button("➕ Lägg till i rutten", use_container_width=True):
                adresser = [rad.strip() for rad in mass_addr.split("\n") if rad.strip()]
                if not adresser:
                    st.warning("Skriv minst en adress.")
                else:
                    nuvarande = hamta_rutt(vald_rutt_id)
                    start_nr = max([int(s.get("Ordning", 0)) for s in nuvarande], default=0) + 1

                    for i, adress in enumerate(adresser):
                        stopp = tomt_stopp(start_nr + i)
                        stopp["Kund"] = default_kund
                        stopp["Adress"] = adress
                        stopp["Info"] = default_info
                        stopp["Vagnar Ut"] = int(default_vagnar)
                        stopp["Prioritet"] = default_prio
                        stopp["Chaufför"] = default_chauffor
                        stopp["Fordon"] = default_fordon
                        nuvarande.append(stopp)

                    st.session_state.rutt_katalog[vald_rutt_id] = sortera_rutt(nuvarande)
                    st.success("Adresserna har lagts till.")
                    st.rerun()

        st.divider()

        if vald_rutt:
            st.subheader("✏️ Redigera rutten direkt i tabellen")
            st.caption("Ändra ordning, kund, adress, info, antal vagnar, chaufför och status. Klicka sedan på spara.")

            df = pd.DataFrame(vald_rutt)
            kolumner = [
                "Ordning", "Kund", "Adress", "Info", "Vagnar Ut", "Vagnar In",
                "Prioritet", "Leveransfönster", "Chaufför", "Fordon", "Status", "Problemtext"
            ]

            edited_df = st.data_editor(
                df,
                column_order=kolumner,
                hide_index=True,
                num_rows="dynamic",
                use_container_width=True,
                disabled=["ID", "Tid", "Senast ändrad"],
                column_config={
                    "Status": st.column_config.SelectboxColumn("Status", options=STATUSAR),
                    "Prioritet": st.column_config.SelectboxColumn("Prioritet", options=["Normal", "Hög"]),
                    "Chaufför": st.column_config.SelectboxColumn("Chaufför", options=[""] + st.session_state.chaufforer),
                    "Fordon": st.column_config.SelectboxColumn("Fordon", options=[""] + [f["Fordon"] for f in st.session_state.fordon]),
                    "Vagnar Ut": st.column_config.NumberColumn("Vagnar Ut", min_value=0, step=1),
                    "Vagnar In": st.column_config.NumberColumn("Vagnar In", min_value=0, step=1),
                },
                key=f"editor_{vald_rutt_id}",
            )

            c_save, c_reset_status, c_export = st.columns(3)

            if c_save.button("💾 Spara ändringar", use_container_width=True):
                new_data = edited_df.to_dict("records")
                normaliserad = []
                for i, rad in enumerate(new_data):
                    stopp = normalisera_stopp(rad, i + 1)
                    stopp["Senast ändrad"] = svensk_datum_tid()
                    normaliserad.append(stopp)
                st.session_state.rutt_katalog[vald_rutt_id] = sortera_rutt(normaliserad)
                st.success("Ändringarna är sparade.")
                st.rerun()

            if c_reset_status.button("↩️ Nollställ status på denna rutt", use_container_width=True):
                for s in st.session_state.rutt_katalog[vald_rutt_id]:
                    s["Status"] = "Väntar"
                    s["Tid"] = ""
                    s["Vagnar In"] = 0
                    s["Problemtext"] = ""
                st.rerun()

            csv = pd.DataFrame(vald_rutt).to_csv(index=False).encode("utf-8-sig")
            c_export.download_button(
                "⬇️ Exportera rutt CSV",
                data=csv,
                file_name=f"{vald_rutt_id}.csv",
                mime="text/csv",
                use_container_width=True,
            )

            st.divider()
            st.subheader("⚠️ Kapacitetskontroll")
            df_rutt = pd.DataFrame(hamta_rutt(vald_rutt_id))
            if not df_rutt.empty and "Fordon" in df_rutt.columns:
                for fordon in df_rutt["Fordon"].dropna().unique():
                    if not fordon:
                        continue
                    planerad_last = int(df_rutt[df_rutt["Fordon"] == fordon]["Vagnar Ut"].sum())
                    cap = next((int(f["Kapacitet"]) for f in st.session_state.fordon if f["Fordon"] == fordon), 0)
                    if cap and planerad_last > cap:
                        st.error(f"{fordon}: {planerad_last}/{cap} vagnar. Över kapacitet.")
                    elif cap:
                        st.success(f"{fordon}: {planerad_last}/{cap} vagnar.")
                    else:
                        st.info(f"{fordon}: ingen kapacitet registrerad.")
        else:
            st.info("Den här rutten är tom. Lägg till adresser ovan.")

# =====================================================
# FLIK 2: LASTNING
# =====================================================
with tab2:
    st.header("📦 Lastningsordning")

    if not vald_rutt:
        st.info("Ingen rutt att lasta.")
    else:
        st.info("LIFO-princip: lasta sista stoppet först, så att första stoppet hamnar längst ut och är lättast att lossa.")
        lastlista = sorted(vald_rutt, key=lambda s: int(s.get("Ordning", 0)), reverse=True)
        df_last = pd.DataFrame(lastlista)
        df_last.insert(0, "Lasta nr", range(1, len(df_last) + 1))

        st.dataframe(
            df_last[["Lasta nr", "Ordning", "Kund", "Adress", "Vagnar Ut", "Fordon", "Chaufför", "Info"]],
            use_container_width=True,
            hide_index=True,
        )

        st.subheader("Sammanfattning per fordon")
        if "Fordon" in df_last.columns:
            samman = df_last.groupby("Fordon", dropna=False)["Vagnar Ut"].sum().reset_index()
            samman = samman.rename(columns={"Vagnar Ut": "Totalt antal vagnar"})
            st.dataframe(samman, use_container_width=True, hide_index=True)

# =====================================================
# FLIK 3: CHAUFFÖR
# =====================================================
with tab3:
    st.header("🚚 Chaufförsvy")

    alla_rutter = list(st.session_state.rutt_katalog.keys())
    if not alla_rutter:
        st.info("Inga rutter finns.")
    else:
        c_rutt = st.selectbox("Välj rutt att köra", alla_rutter, key="chauffor_rutt")
        rutt = hamta_rutt(c_rutt)

        if not rutt:
            st.info("Den valda rutten är tom.")
        else:
            visa_alla = st.checkbox("Visa även redan levererade stopp", value=False)
            stopp_att_visa = rutt if visa_alla else [s for s in rutt if s.get("Status") != "Levererad"]
            stopp_att_visa = sorted(stopp_att_visa, key=lambda s: int(s.get("Ordning", 0)))

            if not stopp_att_visa:
                st.success("🎉 Rutten är klar. Kör tillbaka till tvätteriet med returtvätten.")
            else:
                for i, stopp in enumerate(stopp_att_visa):
                    rubrik = f"STOPP {stopp['Ordning']}: {stopp.get('Kund') or stopp['Adress']} - {status_emoji(stopp.get('Status'))}"
                    with st.expander(rubrik, expanded=(i == 0)):
                        st.write(f"**Adress:** {stopp['Adress']}")
                        if stopp.get("Leveransfönster"):
                            st.write(f"**Leveransfönster:** {stopp['Leveransfönster']}")
                        if stopp.get("Info"):
                            st.warning(f"ℹ️ {stopp['Info']}")

                        c1, c2, c3 = st.columns(3)
                        c1.metric("Rena vagnar ut", stopp.get("Vagnar Ut", 0))
                        c2.metric("Smutstvätt in", stopp.get("Vagnar In", 0))
                        c3.metric("Tid", stopp.get("Tid", "") or "Ej klar")

                        st.link_button("🧭 Öppna i Google Maps", maps_lank(stopp["Adress"]), use_container_width=True)

                        vagnar_in = st.number_input(
                            "Hämtad smutstvätt, antal vagnar",
                            min_value=0,
                            value=int(stopp.get("Vagnar In", 0) or stopp.get("Vagnar Ut", 0)),
                            key=f"vin_{c_rutt}_{stopp['ID']}",
                        )

                        b1, b2, b3 = st.columns(3)
                        if b1.button("✅ Klarmarkera", key=f"klar_{c_rutt}_{stopp['ID']}", use_container_width=True):
                            stopp["Status"] = "Levererad"
                            stopp["Vagnar In"] = int(vagnar_in)
                            stopp["Tid"] = svensk_tid()
                            stopp["Senast ändrad"] = svensk_datum_tid()
                            st.rerun()

                        if b2.button("⚠️ Problem", key=f"prob_{c_rutt}_{stopp['ID']}", use_container_width=True):
                            stopp["Status"] = "Problem"
                            stopp["Tid"] = svensk_tid()
                            stopp["Senast ändrad"] = svensk_datum_tid()
                            st.rerun()

                        if b3.button("↩️ Ångra status", key=f"undo_{c_rutt}_{stopp['ID']}", use_container_width=True):
                            stopp["Status"] = "Väntar"
                            stopp["Tid"] = ""
                            stopp["Senast ändrad"] = svensk_datum_tid()
                            st.rerun()

                        if stopp.get("Status") == "Problem":
                            stopp["Problemtext"] = st.text_area(
                                "Beskriv problem",
                                value=stopp.get("Problemtext", ""),
                                key=f"ptxt_{c_rutt}_{stopp['ID']}",
                                placeholder="Exempel: Ingen på plats, fel antal vagnar, blockerad lastkaj...",
                            )

# =====================================================
# FLIK 4: DASHBOARD
# =====================================================
with tab4:
    st.header("🖥️ Realtidsöversikt")

    if not st.session_state.rutt_katalog:
        st.info("Inga rutter att visa.")
    else:
        oversikt = []
        for r_namn, stopp_lista in st.session_state.rutt_katalog.items():
            stopp_lista = sortera_rutt(stopp_lista)
            total, klara, ut, returer = totaler_for_rutt(stopp_lista)
            problem = len([s for s in stopp_lista if s.get("Status") == "Problem"])
            oversikt.append({
                "Rutt": r_namn,
                "Stopp": total,
                "Klara": klara,
                "Kvar": total - klara,
                "Problem": problem,
                "Rena vagnar ut": ut,
                "Smutstvätt retur": returer,
                "Klar %": round((klara / total) * 100, 1) if total else 0,
            })

        df_oversikt = pd.DataFrame(oversikt)
        st.dataframe(df_oversikt, use_container_width=True, hide_index=True)

        st.divider()
        st.subheader("Detaljer per rutt")

        for r_namn, stopp_lista in st.session_state.rutt_katalog.items():
            if not stopp_lista:
                continue
            df_dash = pd.DataFrame(sortera_rutt(stopp_lista))
            klar = len(df_dash[df_dash["Status"] == "Levererad"])
            total = len(df_dash)

            with st.expander(f"{r_namn} - {klar}/{total} klara", expanded=(r_namn == vald_rutt_id)):
                df_dash["Status"] = df_dash["Status"].apply(status_emoji)
                st.dataframe(
                    df_dash[["Ordning", "Kund", "Adress", "Status", "Tid", "Vagnar Ut", "Vagnar In", "Fordon", "Chaufför", "Info", "Problemtext"]],
                    use_container_width=True,
                    hide_index=True,
                )

# =====================================================
# FLIK 5: REGISTER
# =====================================================
with tab5:
    st.header("⚙️ Register för fordon och chaufförer")

    if not st.session_state.chef_inloggad:
        st.warning("Logga in med chefskod för att ändra register.")
    else:
        c1, c2 = st.columns(2)

        with c1:
            st.subheader("🚛 Fordon")
            df_fordon = pd.DataFrame(st.session_state.fordon)
            edited_fordon = st.data_editor(
                df_fordon,
                num_rows="dynamic",
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Typ": st.column_config.SelectboxColumn("Typ", options=FORDON_TYPER),
                    "Kapacitet": st.column_config.NumberColumn("Kapacitet", min_value=0, step=1),
                },
                key="fordon_editor",
            )
            if st.button("💾 Spara fordonsregister", use_container_width=True):
                st.session_state.fordon = edited_fordon.fillna("").to_dict("records")
                st.success("Fordonsregister sparat.")
                st.rerun()

        with c2:
            st.subheader("👤 Chaufförer")
            df_ch = pd.DataFrame({"Chaufför": st.session_state.chaufforer})
            edited_ch = st.data_editor(
                df_ch,
                num_rows="dynamic",
                use_container_width=True,
                hide_index=True,
                key="chauffor_editor",
            )
            if st.button("💾 Spara chaufförsregister", use_container_width=True):
                st.session_state.chaufforer = [
                    str(x).strip() for x in edited_ch["Chaufför"].dropna().tolist() if str(x).strip()
                ]
                st.success("Chaufförsregister sparat.")
                st.rerun()

# =====================================================
# FOOTER
# =====================================================
st.caption("Tips: använd Backup-knappen i sidomenyn innan du stänger appen, eftersom Streamlit session state inte är permanent lagring.")
