from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import streamlit as st
import io

def generate_pdf():
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=LETTER)
    styles = getSampleStyleSheet()
    story = []

    text = """
    <b>DISCLAIMERS:</b><br/><br/>
    This map tool presents results of modeling for Reclamation Applied Science project R19AP00278 <i>Quantifying Environmental Water Requirements for Groundwater Dependent Ecosystems for Resilient Water Management</i>. 
    See <a href="https://www.conservationgateway.org/ConservationByGeography/NorthAmerica/UnitedStates/nevada/water/Pages/Quantifying-water-requirements-for-GDEs.aspx" color="blue">this link</a> to find out more about the project. 
    The paper describing the methods for the modeling is still in preparation but an overview is available on the 
    <a href="https://www.conservationgateway.org/ConservationByGeography/NorthAmerica/UnitedStates/nevada/water/Documents/ModelingUpdate_Watersmart_Workshop3_forpdf.pdf" color="blue">Nevada TNC website (here)</a>.<br/><br/>

    This dataset does not prove or make any claim about the nature and/or extent of groundwater levels or groundwater-dependent ecosystems (GDEs) for any mapped location...<br/><br/>
    """

    # Use ReportLab's Paragraph to parse basic HTML and hyperlinks
    story.append(Paragraph(text, styles["Normal"]))
    story.append(Spacer(1, 0.25 * inch))

    doc.build(story)
    buffer.seek(0)
    return buffer

# Streamlit UI
st.title("PDF Download with Embedded Hyperlinks")

if st.button("Download PDF"):
    pdf_buffer = generate_pdf()
    st.download_button("Click to Download", pdf_buffer, file_name="disclaimer_report.pdf", mime="application/pdf")
