import requests

from draw import generate_figure
from spectrum_utils import spectrum as sus


def download_spectra_json(usi: str) -> dict | None:
    download_url = f"https://metabolomics-usi.gnps2.org/json/?usi1={usi}"
    response = requests.get(download_url)
    if response.status_code == 200:
        json_content = response.json()
        return json_content
    else:
        print(f"Failed to download file: {response.status_code}")
        return None


def access_scan(mgf_content: str, scan_number: str) -> dict | str:
    """
    :param mgf_content: MGF file content as a string
    :param scan_number: Scan number to access
    :return: Scan content as a string
    """
    lines = mgf_content.split('\n')

    in_scan = False
    precmz = None
    charge = None
    scan_lines = []

    for line in lines:
        if line.startswith('CHARGE='):
            charge = line.split('=')[1].strip()
        if line.startswith('PEPMASS='):
            precmz = line.split('=')[1].strip()
        if line == f'SCANS={scan_number}':
            in_scan = True
            scan_lines.append('mz\tintensity')
        elif in_scan:
            if line.startswith('END IONS'):
                break
            else:
                scan_lines.append(line)
    if scan_lines:
        return {'precmz': precmz, 'charge': charge, 'peaks': '\n'.join(scan_lines)}
    else:
        return f"Scan {scan_number} not found in the MGF file."


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
