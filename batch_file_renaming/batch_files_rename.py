import os
import pandas as pd


# Function to rename files based on the DataFrame
def rename_files(dataframe, root:str):
    for index, row in dataframe.iterrows():
        root_norm = os.path.normpath(root)
        old_name = os.path.normpath(row['old_name'])
        new_name = os.path.normpath(row['new_name'])
        old_path = os.path.join(root_norm, old_name)
        new_path = os.path.join(root_norm, new_name)

        try:
            # Rename the file
            os.rename(old_path, new_path)
            print(f"Renamed: {old_path} -> {new_path}")
        except FileNotFoundError:
            print(f"File not found: {old_path}")
        except Exception as e:
            print(f"Error renaming {old_path} to {new_path}: {e}")


df = pd.DataFrame(data={'old_name': ['incorrect_name.txt', 'incorrect_2_name.txt'], 'new_name': ['correct_name.tsv', 'correct2_name.tsv']})
root_folder = 'path/to/folder'
rename_files(df, root_folder)