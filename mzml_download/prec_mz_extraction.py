import requests
import pandas as pd
import time


def usi_request(usi: str, max_attempts=3, verbose=True):
    attempts = 0
    success = False
    while attempts < max_attempts:  # Try up to 3 times
        if verbose:
            print(f'Requesting {usi} (Attempt {attempts + 1})')
        response = requests.get('https://metabolomics-usi.gnps2.org/json/?usi1=' + str(usi).strip())
        if response.status_code == 200:
            print(f'Attempt {attempts + 1} successful for {usi}.')
            success = True
            return response
            # break  # Exit the retry loop if successful
        else:
            if verbose:
                print(f'Attempt {attempts + 1} failed for {usi}.')
                print(f'status code: {response.status_code}.')
            attempts += 1
            # sleeps for 1 second
            time.sleep(1)

    if not success:  # If all attempts fail, break the outer loops
        if verbose:
            print(f'{usi} failed after 3 attempts. Please verify if it is valid.')
        response.raise_for_status()


def retrieve_prec_mz(csv_path: str, save_to: str):
    df = pd.read_csv(csv_path)
    df['prec_mz'] = ''
    for i, row in df.iterrows():
        response = usi_request(f'mzspec:GNPS:GNPS-LIBRARY:accession:{row['USI']}')
        df.at[i, 'prec_mz'] = response.json()['precursor_mz']

    df.to_csv(save_to, sep='\t', index=False)


def main():
    csv_path = './Julius_USI.csv'
    save_to = './Julius_USI_precmz.tsv'
    retrieve_prec_mz(csv_path, save_to)


if __name__ == '__main__':
    main()
