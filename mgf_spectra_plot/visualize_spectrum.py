import streamlit as st

from draw import *
from utils import access_scan, draw_spectrum, calculate_dynamic_kwargs

# Streamlit app title
st.title("MS Spectra Viewer")

# input mgf file
with st.sidebar:
    mgf_path = st.text_input(
        "Enter a local MGF file path"
    )
    scan_number = st.text_input("Scan number")

mgf_string = open(mgf_path, "r").read()

scan_content = access_scan(mgf_string, scan_number)

precursor_mz = float(scan_content["precmz"])
if scan_content["charge"] is not None:
    precursor_charge = int(scan_content["charge"])
else:
    precursor_charge = 1
peaks = scan_content["peaks"]
usi = f"scan:{scan_number}"

spectrum = parse_tsv_to_spectrum(peaks, precursor_mz, precursor_charge, usi, " ")

# Calculate dynamic kwargs
mz_min, mz_max, max_intensity = calculate_dynamic_kwargs(peaks, peaks_sep=" ")

kwargs = {
    "width": 10,
    "height": 6,
    "annotation_rotation": 90,
    "grid": True,
    "mz_min": mz_min,
    "mz_max": mz_max,
    "max_intensity": max_intensity,
    "usi1": usi,
    "annotate_precision": 2,
}

svg_content = draw_spectrum(spectrum, kwargs)

# Display the SVG in Streamlit
st.image(svg_content, use_container_width=True)
