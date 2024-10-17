
# **Combined Download and XIC Extraction Script Documentation**

## **Overview**

This Python script automates the following tasks:
1. **Download `.mzML` files** from the UCSD MASSIVE repository based on a TSV file containing metadata.
2. **Calculate areas** under the Extracted Ion Chromatogram (XIC) curves for specified precursor m/z values.
3. **Save results** in a new TSV file for further analysis.

## **Folder Structure**

The script expects the following folder structure:

```plaintext
root_directory/
│
├── _files/
│   ├── input_tsv/                  # Folder containing input .tsv files
│   │   ├── your_input_file_1.tsv
│   │   └── your_input_file_2.tsv   # Multiple input .tsv files can be processed
│   │
│   ├── mzml_files/                 # Centralized folder where downloaded .mzML files are stored
│   │   ├── file1.mzML
│   │   └── file2.mzML              # All mzML files downloaded to a single folder
│   │
│   └── mzml_files/area_results/    # Folder for saving output files with XIC area calculations
│       ├── your_input_file_1_xic_results_1.tsv
│       └── your_input_file_2_xic_results_2.tsv
```

- **`_files/input_tsv/`**: Input TSV files should be placed here.
- **`_files/mzml_files/`**: This is where the downloaded `.mzML` files are saved. A separate folder is created for each input TSV file.
- **`_files/mzml_files/area_results/`**: Processed results, containing XIC area calculations, are saved here.

## **Input TSV File Format**

Each input TSV file must include the following columns:

- **`usi`**: The Universal Spectrum Identifier (USI) for downloading the `.mzML` file from the UCSD MASSIVE repository.
- **`filename`**: The name of the `.mzML` file to be saved locally.
- **`prec_mz`**: The precursor m/z value used to extract and process the XIC.

### **Example Input TSV File** (`input_file.tsv`):

```plaintext
usi                 filename        prec_mz
MSV000085123:xy     file1.mzML      500.23
MSV000085123:xy     file2.mzML      600.45
MSV000085123:xy     file3.mzML      700.67
```

## **Output**

For each input TSV file, the script will generate a corresponding results file in the `area_results` folder. The results file contains the following columns:

- **`filename`**: The name of the processed `.mzML` file.
- **`prec_mz`**: The precursor m/z value used for XIC extraction.
- **`area_under_curve`**: The calculated area under the XIC curve (trapezoidal method).
- **`peak_rt`**: The retention time at which the peak intensity was observed.
- **`peak_intensity`**: The peak intensity value.

## **How to Run the Script**

1. Place your input TSV file(s) in the **`_files/input_tsv/`** folder.
2. Run the script. It will:
   - Download the `.mzML` files from UCSD MASSIVE.
   - Process the files and calculate the areas under the XIC curves.
   - Save the results in the **`area_results/`** folder as TSV files.

