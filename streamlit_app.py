# protfolio report
import streamlit as st
import pandas as pd
from io import BytesIO
from fpdf import FPDF

st.set_page_config(page_title="📄 Covered Call Portfolio-Report", layout="centered")
st.title("📄 Portfolio-Reporting: Covered Call Strategien")

st.markdown("Lade Deine Covered Call-Daten hoch (CSV-Format):")
uploaded_file = st.file_uploader("📤 Datei hochladen", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success("✅ Datei geladen")
    st.dataframe(df)

    # PDF Generator
    class PDF(FPDF):
        def header(self):
            self.set_font("Arial", "B", 12)
            self.cell(0, 10, "Covered Call Report", ln=True, align="C")

        def chapter_title(self, title):
            self.set_font("Arial", "B", 11)
            self.ln(5)
            self.cell(0, 10, title, ln=True)

        def chapter_body(self, text):
            self.set_font("Arial", "", 10)
            self.multi_cell(0, 10, text)
            self.ln()

    def create_pdf(dataframe):
        pdf = PDF()
        pdf.add_page()
        pdf.chapter_title("Übersicht")
        summary = f"Anzahl Trades: {len(dataframe)}\nDurchschnittliche Prämie: {dataframe['Prämie'].mean():.2f}\n"
        pdf.chapter_body(summary)

        pdf.chapter_title("Detaildaten")
        for idx, row in dataframe.iterrows():
            line = f"{row['Datum']} – {row['Aktie']} – Strike: {row['Strike']} – Prämie: {row['Prämie']} – Laufzeit: {row['Laufzeit']} Tage"
            pdf.chapter_body(line)

        return pdf.output(dest='S').encode('latin1')

    if st.button("📄 PDF-Report erstellen"):
        pdf_bytes = create_pdf(df)
        st.download_button("📥 PDF herunterladen", data=pdf_bytes, file_name="covered_call_report.pdf", mime="application/pdf")
