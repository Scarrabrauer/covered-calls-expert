
import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

# Manuelle Dividendendatenbank
dividenden = {
    "DE0005557508": 0.90,  # Telekom
    "DE0008404005": 11.40,  # Allianz
    "DE0005190003": 6.00,   # BMW
    "DE000BASF111": 2.25,   # BASF
    "DE0007164600": 2.20    # SAP
}

st.set_page_config(page_title="Covered Call Screener DE", layout="wide")
st.title("📊 Covered Call Screener – Deutsche Aktien (Onvista Webscraper)")

# Auswahl mehrerer Aktien
isin_auswahl = {
    "Deutsche Telekom AG (DTEGn.DE)": "DE0005557508",
    "Allianz SE (ALV.DE)": "DE0008404005",
    "BMW AG (BMW.DE)": "DE0005190003",
    "BASF SE (BAS.DE)": "DE000BASF111",
    "SAP SE (SAP.DE)": "DE0007164600"
}

auswahl = st.selectbox("Wähle eine Aktie", options=list(isin_auswahl.keys()))
isin = isin_auswahl[auswahl]

st.markdown(f"**ISIN:** {isin}")
div = dividenden.get(isin, "Unbekannt")
st.markdown(f"**Dividende:** {div} € (pro Aktie, indikativ)")

url = f"https://www.onvista.de/derivate/snapshot/suchergebnis/?basiswert={isin}"
st.markdown(f"[🔗 Onvista-Link]({url})")

try:
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table")

    df = pd.read_html(str(table))[0]
    st.success("✅ Optionsdaten erfolgreich geladen!")

    # Filter
    col1, col2 = st.columns(2)
    with col1:
        strike_max = st.slider("📉 Max. Strikepreis anzeigen", 0, 500, 250)
    with col2:
        laufzeit = st.text_input("📅 Laufzeitfilter (z. B. 'Jul 2025')", "")

    # Filter anwenden
    filtered_df = df.copy()
    filtered_df = filtered_df[~filtered_df[df.columns[1]].astype(str).str.contains(str(strike_max)) == False]

    if laufzeit:
        filtered_df = filtered_df[filtered_df[df.columns[0]].astype(str).str.contains(laufzeit)]

    st.subheader("📋 Gefilterte Optionen")
    st.dataframe(filtered_df)

    # CSV Export
    st.download_button("📥 Tabelle als CSV herunterladen", filtered_df.to_csv(index=False), file_name=f"covered_calls_{isin}.csv", mime="text/csv")

except Exception as e:
    st.error(f"Fehler beim Laden: {e}")


# US-Aktien hinzufügen
us_aktien = {
    "Apple Inc. (AAPL)": ("US0378331005", 0.96),
    "Microsoft Corp. (MSFT)": ("US5949181045", 2.72),
    "Verizon Communications (VZ)": ("US92343V1044", 2.61),
    "AT&T Inc. (T)": ("US00206R1023", 1.11),
    "Johnson & Johnson (JNJ)": ("US4781601046", 4.84),
    "Coca-Cola Co. (KO)": ("US1912161007", 1.84),
    "PepsiCo Inc. (PEP)": ("US7134481081", 4.60),
    "Exxon Mobil Corp. (XOM)": ("US30231G1022", 3.80),
    "Ford Motor Co. (F)": ("US3453708600", 0.60),
    "ConocoPhillips (COP)": ("US20825C1045", 2.24)
}

st.markdown("---")
st.subheader("📊 Optional: Covered Calls auf US-Aktien")

us_option = st.selectbox("Wähle eine US-Aktie", options=[""] + list(us_aktien.keys()))
if us_option:
    us_isin, us_div = us_aktien[us_option]
    st.markdown(f"**ISIN:** {us_isin}")
    st.markdown(f"**Dividende:** {us_div} USD (indikativ)")
    st.markdown("⚠️ Für US-Aktien stehen derzeit keine Optionsketten über Onvista zur Verfügung – Integration via Yahoo API möglich.")


import json

st.markdown("---")
st.subheader("📊 Yahoo Finance API – Optionsdaten für US-Aktien")

# RapidAPI-Key (aus Sicherheitsgründen muss dieser in Praxis geheim gehalten werden)
api_key = st.text_input("🔑 Dein RapidAPI-Key", type="password")

us_api_symbol = st.selectbox("Wähle Symbol (US-Aktie)", ["AAPL", "MSFT", "VZ", "T", "KO", "XOM", "F"])

if api_key and us_api_symbol:
    st.markdown(f"Abruf von Optionen für **{us_api_symbol}** via Yahoo Finance API")
    url = f"https://yh-finance.p.rapidapi.com/stock/v2/get-options?symbol={us_api_symbol}"

    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "yh-finance.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            dates = data.get("expirationDates", [])
            st.markdown(f"**Verfügbare Laufzeiten (UNIX):** {dates[:5]}")
        else:
            st.error(f"Fehler beim API-Abruf: {response.status_code}")
    except Exception as e:
        st.error(f"Fehler bei API-Verbindung: {e}")
