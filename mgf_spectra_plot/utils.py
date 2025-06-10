import requests

from draw import generate_figure
from spectrum_utils import spectrum as sus
from pyteomics import mgf


def download_spectra_json(usi: str) -> dict | None:
    download_url = f"https://metabolomics-usi.gnps2.org/json/?usi1={usi}"
    response = requests.get(download_url)
    if response.status_code == 200:
        json_content = response.json()
        return json_content
    else:
        print(f"Failed to download file: {response.status_code}")
        return None


def access_scan(mgf_path: str, scan_num: str) -> dict | None:
    """
    Access a scan number within an MGF file.
    :param mgf_path: path to the MGF file
    :param scan_num: Scan number to retrieve
    :return: a dict containing the spectrum information
    """
    mgf_contents = mgf.IndexedMGF(mgf_path, index_by_scans=True)
    try:
        spectrum = mgf_contents.get_spectrum(scan_num)
        result = dict(zip(spectrum["m/z array"], spectrum["intensity array"]))
        peaks_string = "\n".join([f"{mz}\t{inten}" for mz, inten in result.items()])
        precmz = spectrum["params"].get("pepmass")[0]
        charge = spectrum["params"].get("charge")[0]
        return {'precmz': precmz, 'charge': charge, 'peaks': peaks_string}

    except KeyError:
        print(f"Scan {scan_num} not found in the MGF file.")
        return None


def parse_usi(usi: str) -> dict:
    """
    :param usi: complete USI string ('mzspec:ZENODO-8338511:CCE_P1706_127_MSMS.mzXML')
    :return: dictionary with USI parts
    """
    usi_parts = usi.split(':')
    if len(usi_parts) != 5:
        raise ValueError(
            "Invalid USI format. Expected format: 'mzspec:ZENODO-DEPOSITION_ID:MGF_FILE_NAME:SCAN:SCAN_NUMBER'")

    return {
        'type': usi_parts[0],
        'zenodo_id': usi_parts[1],
        'file_name': usi_parts[2],
        'scan': usi_parts[4] if len(usi_parts) > 3 else None
    }


def sort_and_filter_by_intensity(peaks_string, max_peaks=None):
    if max_peaks is not None:
        lines = peaks_string.replace('mz\tintensity', '').strip().split('\n')
        pairs = [tuple(map(float, line.split('\t'))) for line in lines if line.strip()]

        # Create a dictionary to store the most intense peak for each rounded m/z
        peak_dict = {}
        for mz, intensity in pairs:
            mz_rounded = round(mz)
            if mz_rounded not in peak_dict or intensity > peak_dict[mz_rounded][1]:
                peak_dict[mz_rounded] = (mz, intensity)

        # Get the list of most intense peaks per rounded m/z and sort by intensity
        unique_peaks = list(peak_dict.values())
        sorted_peaks = sorted(unique_peaks, key=lambda x: x[1], reverse=True)[:max_peaks + 1]

        # Sort the final result by m/z
        sorted_by_mz = sorted(sorted_peaks, key=lambda x: x[0])
        filtered_peaks = '\n'.join(f"{mz}\t{intensity}" for mz, intensity in sorted_by_mz)
    else:
        filtered_peaks = peaks_string

    return filtered_peaks


def draw_spectrum(spectrum: sus.MsmsSpectrum, kwargs: dict):
    image_buffer = generate_figure(spectrum, extension="svg", **kwargs)
    # Save or display the SVG
    with open("spectrum_plot.svg", "wb") as f:
        f.write(image_buffer.getvalue())
    svg_file_path = "spectrum_plot.svg"
    with open(svg_file_path, "r") as f:
        svg_content = f.read()

    return svg_content


def calculate_dynamic_kwargs(peaks_string, margin_mz=50, margin_intensity=10, peaks_sep="\t"):
    lines = peaks_string.strip().split("\n")[1:]  # Skip the header
    mz_values = []
    intensity_values = []

    for line in lines:
        mz, intensity = map(float, line.split(peaks_sep))
        mz_values.append(mz)
        intensity_values.append(intensity)

    mz_min = max(0, min(mz_values) - margin_mz)
    mz_max = max(mz_values) + margin_mz
    max_intensity = (max(intensity_values) / max(intensity_values) * 100) + margin_intensity

    return mz_min, mz_max, max_intensity


if __name__ == '__main__':
    path = '/Users/wilhan/Downloads/specs_ms_cluster1.mgf'
    print(access_scan(path, "1"))