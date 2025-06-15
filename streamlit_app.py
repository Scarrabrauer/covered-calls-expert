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

url = f"https://www.onvista.de/derivate/{isin}"
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
