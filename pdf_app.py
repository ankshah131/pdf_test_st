import requests 
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import streamlit as st
import io

from reportlab.platypus import Image as reportImage
from PIL import Image

PATH_LOGOS = "https://raw.githubusercontent.com/ankshah131/pdf_test_st/8bd1f0b647822f368111346c376a00e7122c61ff/logos.png"

def generate_pdf(image_url):
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

    <b>REFERENCES:</b><br/><br/>

    Abatzoglou JT. 2013. Development of gridded surface meteorological data for ecological applications and modelling. Int. J. Climatol. 33: 121–131. 
    Available at <a href="http://onlinelibrary.wiley.com/doi/10.1002/joc.3413/full" color="blue">http://onlinelibrary.wiley.com/doi/10.1002/joc.3413/full</a><br/><br/>
    
    Fang, H., Baret, F., Plummer, S., & Schaepman-Strub, G. (2019). An overview of global leaf area index (LAI): Methods, products, validation, and applications. Reviews of Geophysics, 57, 739–799. 
    Available at <a href="https://doi.org/10.1029/2018RG000608" color="blue">https://doi.org/10.1029/2018RG000608</a><br/><br/>
    
    Food and Agriculture Organization. 2006. Soil Texture. 
    Available at <a href="https://www.fao.org/fishery/static/FAO_Training/FAO_Training/General/x6706e/x6706e06.htm" color="blue">https://www.fao.org/fishery/static/FAO_Training/FAO_Training/General/x6706e/x6706e06.htm</a><br/><br/>
    
    Nevada Division of Water Planning. 1999. Nevada State Water Plan. Carson City: Department of Conservation and Natural Resources, Nevada Division of Water Planning. 
    Available at <a href="https://water.nv.gov/library/water-planning-reports" color="blue">https://water.nv.gov/library/water-planning-reports</a><br/><br/>
    
    The Nature Conservancy. 2021. Plant Rooting Depth Database. 
    Available at <a href="https://www.groundwaterresourcehub.org/where-we-work/california/plant-rooting-depth-database/" color="blue">https://www.groundwaterresourcehub.org/where-we-work/california/plant-rooting-depth-database/</a><br/><br/>
    
    Walkinshaw M, O’Geen AT, Beaudette DE. 2020. Soil Properties. California Soil Resource Lab. 
    Available at <a href="https://casoilresource.lawr.ucdavis.edu/soil-properties/" color="blue">https://casoilresource.lawr.ucdavis.edu/soil-properties/</a>
    """

    # Use ReportLab's Paragraph to parse basic HTML and hyperlinks
    story.append(Paragraph(text, styles["Normal"]))
    story.append(Spacer(1, 0.25 * inch))

        # Add image from URL (optional)
    if image_url:
        try:
            img_response = requests.get(image_url)
            img_response.raise_for_status()

            # Open with PIL and convert to RGB
            pil_img = Image.open(io.BytesIO(img_response.content)).convert("RGB")

            # Save to byte array in PNG format
            img_byte_arr = io.BytesIO()
            pil_img.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)

            # Create ReportLab Image and append to story
            rl_img = reportImage(img_byte_arr, width=7*inch, height=3*inch)
            story.append(rl_img)
        except Exception as e:
            st.error(f"[ERROR] Failed to load image from URL: {e}")

    doc.build(story)
    buffer.seek(0)
    return buffer

# Streamlit UI
st.title("PDF Download with Embedded Hyperlinks")

if st.button("Download PDF"):
    pdf_buffer = generate_pdf(PATH_LOGOS)
    st.download_button("Click to Download", pdf_buffer, file_name="disclaimer_report.pdf", mime="application/pdf")
