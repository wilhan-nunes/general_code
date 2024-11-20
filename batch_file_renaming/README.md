
# Batch File Renaming Script

This Python script provides functionality to rename files within a specified directory based on a mapping defined in a pandas DataFrame.

## Features

- Renames files in a given folder based on old and new names defined in the DataFrame.
- Logs the renaming actions in the console.
- Handles exceptions for missing files and other errors.

## Requirements

- Python 3.6 or newer
- pandas library

## Setup

1. Clone this repository or copy the script to your local machine.
2. Install the required library using pip:

```bash
pip install pandas
```

3. Define the DataFrame (`df`) with the following structure:
   - `old_name`: Names of files to rename.
   - `new_name`: Corresponding new names for the files.
   - Obs: You can also create a csv file with these two columns and load it with `df = pd.read_csv()`

4. Specify the root folder path containing the files to rename in the `root_folder` variable.

## Usage

1. Update the  `df` DataFrame (or load from csv) with your file names.
   - The df will be:
```commandline
>>> df
               old_name           new_name
0    incorrect_name.txt   correct_name.tsv
1  incorrect_2_name.txt  correct2_name.tsv
```
2. Set the `root_folder` variable to the folder containing the files.
3. Run the script:

```bash
python rename_files_script.py
```

## Example

```python
df = pd.DataFrame(data={
    'old_name': ['incorrect_name.txt', 'incorrect_2_name.txt'],
    'new_name': ['correct_name.tsv', 'correct2_name.tsv']
})
root_folder = 'path/to/folder'
rename_files(df, root_folder)
```


## Notes

- Ensure you have write permissions for the target folder.
- The script will log skipped files and errors in the console.
