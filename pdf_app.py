import asyncio
import folium
import tempfile
import os
from PIL import Image
from pyppeteer import launch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as reportImage
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import io
import streamlit as st
import requests

from reportlab.platypus import Image as reportImage
from PIL import Image

logos_url = "https://raw.githubusercontent.com/ankshah131/pdf_test_st/8bd1f0b647822f368111346c376a00e7122c61ff/logos.png"

lat = st.number_input("Latitude", value=36.7783, format="%.6f")
lon = st.number_input("Longitude", value=-119.4179, format="%.6f")

disclaimer_text= """
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

def create_map_snapshot(lat, lon, zoom=10):
    def safe_async_run(coro):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)

    with tempfile.TemporaryDirectory() as tmpdir:
        html_path = os.path.join(tmpdir, "map.html")
        screenshot_path = os.path.join(tmpdir, "map.png")

        # Create map and save as HTML
        m = folium.Map(location=[lat, lon], zoom_start=zoom)
        folium.Marker([lat, lon], popup="Location").add_to(m)
        m.save(html_path)

        # Safely run the screenshot
        safe_async_run(take_map_screenshot(html_path, screenshot_path))

        # Load screenshot into buffer
        image = Image.open(screenshot_path).convert("RGB")
        img_buffer = io.BytesIO()
        image.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        return img_buffer


def generate_pdf(disclaimer_text, logos_url, map_img_buffer=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=LETTER)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(disclaimer_text, styles["Normal"]))
    story.append(Spacer(1, 0.25 * inch))

    # Add logos image
    if logos_url:
        try:
            logos_img = Image.open(requests.get(logos_url, stream=True).raw).convert("RGB")
            logos_buf = io.BytesIO()
            logos_img.save(logos_buf, format="PNG")
            logos_buf.seek(0)
            story.append(reportImage(logos_buf, width=6 * inch, height=2 * inch))
            story.append(Spacer(1, 0.25 * inch))
        except Exception as e:
            st.error(f"Error loading logos: {e}")

    # Add map image
    if map_img_buffer:
        story.append(Paragraph("<b>Map Location:</b>", styles["Normal"]))
        story.append(reportImage(map_img_buffer, width=6 * inch, height=4 * inch))

    doc.build(story)
    buffer.seek(0)
    return buffer


# Streamlit UI
st.title("PDF Download with Embedded Hyperlinks")

if st.button("Generate PDF"):
    disclaimer_text = "<b>Disclaimer:</b> This is a test PDF with a dynamic map."
    map_buffer = create_map_snapshot(lat, lon)
    pdf_buffer = generate_pdf(disclaimer_text, logos_url, map_img_buffer=map_buffer)
    st.download_button("Download PDF", pdf_buffer, file_name="map_report.pdf", mime="application/pdf")
