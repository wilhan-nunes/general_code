import os
import requests
import numpy as np
import pandas as pd
import re


def massive_files(msvnumber:str):
    response = requests.get(f'https://explorer.gnps2.org/api/datasets/{msvnumber}/files')
    if response.status_code == 200:
        data = response.json()
        file_list = [item['filename'] for item in data]

        return file_list
    else:
        response.raise_for_status()

msvnumber = 'MSV000095567'
file_list = massive_files(msvnumber)


def extract_prefix(text):
    """
    Function to extract the prefix of the file name (the first two fields separated by underscore) that represents
    the plate number and coordinates. Ex: P1_G9 = Plate 1 row G column 9
    :param text:
    :return:
    """
    match = re.search(r'^([^_]+)_([^_]+)', text)
    if match:
        return f"{match.group(1)}_{match.group(2)}"
    return None

def generate_names(file_name:str):
    df = pd.read_csv(file_name, sep='\t')
    file_name_list = []
    for i, row in df.iterrows():
        plate_num = df.columns[0]
        counter = 1
        for column in df.columns[1:]:
            if not pd.isnull(row[column]):
                file_name_list.append(f'P{plate_num[-1]}_{row[plate_num]}{counter}_{row[column]}')
                counter += 1
            else:
                break

    return file_name_list

plate_maps = sorted([file for file in os.listdir('./platemap') if file.endswith('.tsv')])

complete_list = []
for file in plate_maps:
    complete_list.extend(generate_names(os.path.join('./platemap', file)))


df = pd.DataFrame()
df['correct_name'] = complete_list
#  correcting misspelling
df['correct_name'] = df['correct_name'].apply(lambda x: x.replace('BSPS', 'BPSP'))
df['prefix'] = df['correct_name'].apply(lambda x: extract_prefix(x.split('/')[-1]))

incorrect_df = pd.DataFrame()
incorrect_df['incorrect_name'] = file_list
incorrect_df['prefix'] = incorrect_df['incorrect_name'].apply(lambda x: extract_prefix(x.split('/')[-1]))

merged_df = pd.merge(incorrect_df, df, on='prefix', how='outer')
merged_df['full_correct_name'] = ''
for i, row in merged_df.iterrows():
    if not pd.isnull(row['correct_name']):
        file_extension = row['incorrect_name'].split('.')[-1]
        merged_df.at[i, 'full_correct_name'] = f'{row['incorrect_name'][:row['incorrect_name'].rfind('/')]}/{row['correct_name']}.{file_extension}'
    else:
        merged_df.at[i, 'full_correct_name'] = np.nan

renaming_df = merged_df[['incorrect_name', 'full_correct_name']][merged_df['incorrect_name'] != merged_df['full_correct_name']]

# removing the files that doesn't have a correspondence to the platemap
renaming_df = renaming_df.dropna(subset=['full_correct_name'])
renaming_df['full_correct_name'] = renaming_df['full_correct_name'].apply(lambda x: x.replace('BSPS', 'BPSP'))
renaming_df['full_correct_name'] = renaming_df['full_correct_name'].apply(lambda x: x.replace('raw/BPSP', 'raw/BSPS'))



# Function to rename files based on the DataFrame
def rename_files(dataframe):
    for index, row in dataframe.iterrows():
        incorrect_name = row['incorrect_name']
        full_correct_name = row['full_correct_name']

        try:
            # Rename the file
            os.rename(incorrect_name, full_correct_name)
            print(f"Renamed: {incorrect_name} -> {full_correct_name}")
        except FileNotFoundError:
            print(f"File not found: {incorrect_name}")
        except Exception as e:
            print(f"Error renaming {incorrect_name} to {full_correct_name}: {e}")

# rename_files(renaming_df)