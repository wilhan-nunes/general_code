import gc
import io
from typing import Any, List

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from spectrum_utils import plot as sup, spectrum as sus

USI_SERVER = "https://metabolomics-usi.ucsd.edu/"
matplotlib.use("svg")
plt.rcParams["svg.fonttype"] = "none"


def generate_figure(
        spectrum: sus.MsmsSpectrum, extension: str, **kwargs: Any
) -> io.BytesIO:
    """
    Generate a spectrum plot.

    Parameters
    ----------
    spectrum : sus.MsmsSpectrum
        The spectrum to be plotted.
    extension : str
        Image format.
    kwargs : Any
        Plotting settings.

    Returns
    -------
    io.BytesIO
        Bytes buffer containing the spectrum plot.
    """
    usi = spectrum.identifier

    fig, ax = plt.subplots(figsize=(kwargs["width"], kwargs["height"]))

    sup.spectrum(
        spectrum,
        # annotate_ions=kwargs["annotate_peaks"],
        annot_kws={"rotation": kwargs["annotation_rotation"], "clip_on": True},
        grid=kwargs["grid"],
        ax=ax,
    )

    ax.set_xlim(kwargs["mz_min"], kwargs["mz_max"])
    ax.set_ylim(0, kwargs["max_intensity"] / 100)

    if not kwargs["grid"]:
        ax.spines["right"].set_visible(False)
        ax.spines["top"].set_visible(False)
        ax.yaxis.set_ticks_position("left")
        ax.xaxis.set_ticks_position("bottom")

    title = ax.text(
        0.5,
        1.06,
        kwargs["usi1"],
        horizontalalignment="center",
        verticalalignment="bottom",
        fontsize="x-large",
        fontweight="bold",
        transform=ax.transAxes,
    )
    title.set_url(f"{USI_SERVER}spectrum/?usi1={usi}")
    subtitle = (
        f"Precursor $m$/$z$: "
        f'{spectrum.precursor_mz:.{kwargs["annotate_precision"]}f} '
        if spectrum.precursor_mz > 0
        else ""
    )
    subtitle += f"Charge: {spectrum.precursor_charge}"
    subtitle = ax.text(
        0.5,
        1.02,
        subtitle,
        horizontalalignment="center",
        verticalalignment="bottom",
        fontsize="large",
        transform=ax.transAxes,
    )
    subtitle.set_url(f"{USI_SERVER}spectrum/?usi1={usi}")

    buf = io.BytesIO()
    plt.savefig(buf, bbox_inches="tight", format=extension)
    buf.seek(0)
    fig.clear()
    plt.close(fig)
    gc.collect()

    return buf


def parse_tsv_to_spectrum(tsv_string, precursor_mz, precursor_charge, identifier, peaks_sep="\t"):
    """
    Parse a TSV string to create a sus.MsmsSpectrum object.

    Parameters
    ----------
    tsv_string : str
        The TSV string containing m/z and intensity values.
    precursor_mz : float
        The precursor m/z value.
    precursor_charge : int
        The precursor charge.

    Returns
    -------
    sus.MsmsSpectrum
        The spectrum object created from the TSV data.
    """
    # Parse the TSV string into a NumPy array
    lines = tsv_string.strip().split("\n")
    mz, intensity = [], []
    for line in lines[1:]:  # Skip the header
        mz_value, intensity_value = map(float, line.split(peaks_sep))
        mz.append(mz_value)
        intensity.append(intensity_value)

    # Create the MsmsSpectrum object
    spectrum = sus.MsmsSpectrum(identifier, precursor_mz, precursor_charge, np.array(mz), np.array(intensity))
    return spectrum
