import warnings
import requests
import os
import pandas as pd


warnings.simplefilter(action='ignore', category=FutureWarning)


def download_mzml(df: pd.DataFrame, save_to:str):

    if not os.path.exists(save_to):
        # If it doesn't exist, create it
        os.makedirs(save_to)
    error_log = os.path.join(save_to, 'error_log.txt')
    # Define the base URL
    url = "https://massive.ucsd.edu/ProteoSAFe/DownloadResultFile"
    # Downloaded files:
    downloaded_files = set(os.listdir(save_to))
    counter = 0
    for i, row in df.iterrows():
        usi = row['USI']
        # msv_number = row['MassIVE']
        file_name = row['Filename']

        # Define the query parameters in the payload dictionary
        mzml_file = '/'.join(usi.split(':')[1:3])
        payload = {
            "forceDownload": "true",  # Query parameter for forcing the download
            "file": f"f.{mzml_file}"  # Query parameter for specifying the file path
        }

        if file_name in downloaded_files:
            print(f'{file_name} already downloaded. Skipping file.')
            counter += 1
            continue

        response = requests.get(url, params=payload)

        if response.status_code == 200:
            file_path = os.path.join(directory_path, file_name)
            with open(file_path, 'wb') as f:
                f.write(response.content)
                downloaded_files.add(file_name)
                print(f"File saved at {file_path}")
        else:
            open(error_log, 'a').write(f'Error downloading {file_name}\n')
            print("Error downloading the file.")
        counter += 1
        print(f'file {counter} of {len(df)}')



directory = './_files/input_tsv'
tsv_list = [file for file in os.listdir(directory) if file.endswith('.tsv')]
for file_name in tsv_list:
    folder_to_save = os.path.join(directory, file_name.split('.tsv')[0])
    df = pd.read_csv(os.path.join(directory, file_name), sep='\t')
    download_mzml(df=df, save_to=folder_to_save)


