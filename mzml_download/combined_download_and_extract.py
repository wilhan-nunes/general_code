import warnings
import requests
import os
import pandas as pd
import numpy as np
import pymzml
from tqdm import tqdm

# Suppress warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# Function to download mzML files
def download_mzml(df: pd.DataFrame, save_to: str):
    if not os.path.exists(save_to):
        os.makedirs(save_to)
    error_log = os.path.join(save_to, 'error_log.txt')
    url = "https://massive.ucsd.edu/ProteoSAFe/DownloadResultFile"
    downloaded_files = set(os.listdir(save_to))  # Keep track of already downloaded files

    # Progress bar to track downloads
    with tqdm(total=len(df), desc="Downloading mzML files", unit="file") as pbar:
        for i, row in df.iterrows():
            usi = row['USI']
            file_name = row['Filename']  # The name of the mzML file to save

            # Skip the file if it's already downloaded
            if file_name in downloaded_files:
                pbar.update(1)  # Update progress bar even if the file is skipped
                print(f'{file_name} already downloaded. Skipping file.')
                continue

            # Create the download request
            mzml_file = '/'.join(usi.split(':')[1:3])  # Format the file path for the API
            payload = {"forceDownload": "true", "file": f"f.{mzml_file}"}

            # Perform the download
            response = requests.get(url, params=payload)
            if response.status_code == 200:
                file_path = os.path.join(save_to, file_name)
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                    print(f"File saved at {file_path}")
            else:
                with open(error_log, 'a') as log_file:
                    log_file.write(f'Error downloading {file_name}\n')
                print(f"Error downloading {file_name}.")

            pbar.update(1)  # Update progress bar for each file downloaded

# Function to extract ion chromatograms and calculate areas with a progress bar
def extract_ion_chromatograms(df: pd.DataFrame, mzml_dir: str, result_filename: str):
    with tqdm(total=len(df), desc="Extracting ion chromatograms", unit="file") as pbar:
        for i, row in df.iterrows():
            mzml_file = row['Filename']
            prec_mz = row['Prec_mz']
            mzml_file_path = os.path.join(mzml_dir, mzml_file)

            if not os.path.exists(mzml_file_path):
                print(f"File {mzml_file_path} not found. Skipping...")
                pbar.update(1)
                continue

            run = pymzml.run.Reader(mzml_file_path)
            target_mz = prec_mz
            ppm_tolerance = 10
            mz_tolerance = target_mz * (ppm_tolerance / 1e6)
            mz_min = target_mz - mz_tolerance
            mz_max = target_mz + mz_tolerance
            xic_data = []

            for spectrum in run:
                if spectrum.ms_level == 1:
                    rt = spectrum.scan_time_in_minutes()
                    intensities = spectrum.i[
                        (spectrum.mz >= mz_min) & (spectrum.mz <= mz_max)
                    ]
                    total_intensity = sum(intensities)
                    xic_data.append((rt, total_intensity))

            if xic_data:
                rt_values, intensity_values = zip(*xic_data)
                auc = np.trapezoid(intensity_values, rt_values)
                peak = max(xic_data, key=lambda x: x[1])
                peak_retention_time = peak[0]
                peak_intensity = peak[1]

                df.at[i, 'area_under_curve'] = auc
                df.at[i, 'peak_rt'] = peak_retention_time
                df.at[i, 'peak_intensity'] = peak_intensity
            else:
                df.at[i, 'area_under_curve'] = np.nan
                df.at[i, 'peak_rt'] = np.nan
                df.at[i, 'peak_intensity'] = np.nan

            pbar.update(1)  # Update progress bar for each file processed

    result_dir = os.path.join(mzml_dir, 'area_results')
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)
    df.to_csv(os.path.join(result_dir, result_filename), sep='\t', index=False)

# Main flow
def main():
    directory = './_files/input_tsv'
    tsv_list = [file for file in os.listdir(directory) if file.endswith('.tsv')]
    mzml_save_dir = './_files/mzml_files'
    
    for file_name in tsv_list:
        df = pd.read_csv(os.path.join(directory, file_name), sep='\t')

        # Step 1: Download mzML files to a single folder
        print(f"Downloading mzML files for {file_name}...")
        download_mzml(df, mzml_save_dir,)

        # Step 2: Extract ion chromatograms and calculate areas
        print(f"Extracting ion chromatograms and calculating areas for {file_name}...")
        results_file = f'{file_name[:-4]}_xic_results.tsv'
        extract_ion_chromatograms(df, mzml_save_dir, results_file)

if __name__ == '__main__':
    main()
