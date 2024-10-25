
# Compound MS Quantification

This Python script calculates the concentration of compounds in samples by applying compound-specific quadratic equations to measured MS peak area ratios.

## Function Overview

### `calculate_conc`

This function calculates compound concentrations by:
1. Reading in the sample peak area ratios ([ratio_template.tsv](./input/ratio_template.tsv)).
2. Parsing compound-specific quadratic equations ([equations_template.tsv](./input/equations_template.tsv)).
3. Solving each equation for each compound/sample ratio using quadratic root calculations.
4. Saving the calculated roots (concentrations) for each compound and sample.

### Parameters:
- **ratios_tsv** (str): Path to the TSV file containing peak area ratios for each sample.
- **equations_tsv** (str): Path to the TSV file containing the quadratic equation for each compound.
- **output** (str): File path to save the output TSV file with calculated concentrations.
- **both_roots** (True): If you want both roots in the result TSV. If False, return only the positive (or the greater if
both are negative)

## Input Files

1. **equations_template.tsv**: A TSV file containing compound names and their quadratic equations in the form:

   ```
   Compound         Equation
   Histamine-C2:0   y = ax^2 + bx + c
   ```

   - **Compound**: Name of the compound.
   - **Equation**: The quadratic equation (y = ax^2 + bx + c), where `y` is the area ratios and `x` is the concentration.


2. **ratio_template.tsv**: A TSV file with sample data for measured concentration ratios.

   - **filename**: Identifier of the sample.
   - Columns for each compound (e.g., Cadaverine-C2:0, Histamine-C3:0, etc.) representing concentration ratios.

## How It Works

1. **Load Data**: Reads both TSV files into DataFrames.
2. **Extract Coefficients**: Parses each compound's equation from `equations_template.tsv` to get the coefficients \( a \), \( b \), and \( c \).
3. **Calculate Roots**:
   - Iterates through each sample in `ratio_template.tsv`.
   - For each compound's measured ratio (`y`), calculates the roots \( x_1 \) and \( x_2 \) using the `solve_quadratic` function.
   - If real solutions are found, stores them as `x1` and `x2`; otherwise, assigns "None".
4. **Save Output**: Writes the calculated concentrations to `output` as a TSV file.

## Example Usage

Change the paths to the desired files in the `main()` function and run the code.

```python
def main():
   # Define file paths
   ratios_tsv = 'ratio_template.tsv'
   equations_tsv = 'equations_template.tsv'
   output_path = 'calculated_concentrations.tsv'
   
   # Run the concentration calculation
   calculate_conc(ratios_tsv, equations_tsv, output_path)
```

### Expected Output

The output TSV file contains:
- `filename`: Sample identifier.
- Compound-specific columns, each with two calculated values (`x1` and `x2`) for the roots of each compound equation, representing calculated concentrations.

## Dependencies
- `pandas`: Used for reading and writing TSV files.
- `math`: For calculating square roots in quadratic equations.

