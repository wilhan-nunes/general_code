import pymzml
import os
import numpy as np
import pandas as pd

directory = './_files/input_tsv'
tsv_list = [file for file in os.listdir(directory) if file.endswith('.tsv')]
for file_name in tsv_list:
    df = pd.read_csv(os.path.join(directory, file_name), sep='\t')
    df['area_under_curve'] = ''
    df['peak_rt'] = ''
    df['peak_intensity'] = ''

    for i, row in df.iterrows():
        prec_mz = row['Prec_mz']
        mzml_file = row['Filename']
        mzml_file_path = os.path.join(directory, file_name[:-4], mzml_file)
        # Load the mzML file

        run = pymzml.run.Reader(mzml_file_path)

        # Define the m/z target and tolerance
        target_mz = prec_mz  # The m/z of the ion you are interested in
        ppm_tolerance = 10  # Example: 10 ppm tolerance
        mz_tolerance = target_mz * (ppm_tolerance / 1e6)
        mz_min = target_mz - mz_tolerance
        mz_max = target_mz + mz_tolerance

        # Initialize a list to store XIC data (retention time vs intensity)
        xic_data = []

        # Loop over each spectrum in the mzML file
        for spectrum in run:
            if spectrum.ms_level == 1:  # Only extract from MS1 spectra
                # Get the retention time in minutes (or seconds depending on your data)
                rt = spectrum.scan_time_in_minutes()

                # Extract intensities for the m/z range within the tolerance
                intensities = spectrum.i[
                    (spectrum.mz >= mz_min) & (spectrum.mz <= mz_max)
                    ]

                # Sum the intensities in the m/z window to get total intensity for that scan
                total_intensity = sum(intensities)

                # Append the retention time and intensity to the XIC data
                xic_data.append((rt, total_intensity))

        # for rt, intensity in xic_data:
        #     print(f"RT: {rt:.2f} min, Intensity: {intensity:.2f}")

        # # Unzip XIC data into retention times and intensities
        rt_values, intensity_values = zip(*xic_data)
        auc = np.trapezoid(intensity_values, rt_values)
        peak = max(xic_data, key=lambda x: x[1])
        peak_retention_time = peak[0]
        peak_intensity = peak[1]

        df.at[i, 'area_under_curve'] = auc
        df.at[i, 'peak_rt'] = peak_retention_time
        df.at[i, 'peak_intensity'] = peak_intensity

    # saving the results
    df.to_csv(os.path.join(directory,'area_results', file_name+'_xic_results.tsv'), sep='\t', index=False)