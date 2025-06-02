import streamlit as st

from draw import *
from utils import access_scan, draw_spectrum, calculate_dynamic_kwargs

# Streamlit app title
st.title("MGF Spectra Viewer")

# input mgf file
with st.sidebar:
    mgf_path = st.text_input(
        "Enter a local MGF file path", placeholder="path/to/your/file.mgf"
    )
    scan_number = st.text_input("Scan number", value="1")

if mgf_path and scan_number:

    mgf_string = open(mgf_path, "r").read()

    scan_content = access_scan(mgf_path, scan_number)

    precursor_mz = float(scan_content["precmz"])
    if scan_content["charge"] is not None:
        precursor_charge = int(scan_content["charge"])
    else:
        precursor_charge = 1
    peaks = scan_content["peaks"]
    usi = f"scan:{scan_number}"
    print(peaks)

    spectrum = parse_tsv_to_spectrum(peaks, precursor_mz, precursor_charge, usi, "\t")

    # Calculate dynamic kwargs
    _mz_min, _mz_max, _max_intensity = calculate_dynamic_kwargs(peaks, peaks_sep="\t")

    with st.sidebar:
        st.write("Drawing Controls")
        title = st.text_input("Title", placeholder='Optional: Title for the spectrum', value='')
        mz_min = st.number_input("m/z min", value=_mz_min, step=0.1, format="%.2f")
        mz_max = st.number_input("m/z max", value=_mz_max, step=0.1, format="%.2f")
        max_intensity = st.number_input("Max intensity (%)", value=_max_intensity, step=1.0, format="%.0f")
        annotate_precision = st.number_input("Annotate precision", value=4, min_value=0, max_value=10, step=1)
        annotation_rotation = st.number_input("Annotation rotation", value=90, min_value=0, max_value=360, step=1)

    kwargs = {
        "width": 10,
        "height": 6,
        "annotation_rotation": annotation_rotation,
        "grid": True,
        "mz_min": mz_min,
        "mz_max": mz_max,
        "max_intensity": max_intensity,
        "usi1": f"{title} ({usi})" if title else usi,
        "annotate_precision": annotate_precision,
    }

    svg_content = draw_spectrum(spectrum, kwargs)

    # Display the SVG in Streamlit
    st.image(svg_content, use_container_width=True)
    #download svg image
    st.download_button(
        label="Download Spectrum SVG",
        data=svg_content,
        file_name=f"spectrum_{scan_number}.svg",
        mime="image/svg+xml",
    )

else:
    st.warning("Please enter a valid MGF file path and scan number.")