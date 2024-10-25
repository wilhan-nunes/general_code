import math
import pandas as pd


def solve_quadratic(a, b, c, y, return_both=True):
    # Rearrange the equation to ax^2 + bx + (c - y) = 0
    if y == 0:
        return 0, 0
    else:
        c = c - y

    # Calculate the discriminant
    discriminant = b ** 2 - 4 * a * c

    # Check if the discriminant is non-negative (real solutions exist)
    if discriminant >= 0:
        # Calculate the two possible solutions
        x1 = (-b + math.sqrt(discriminant)) / (2 * a)
        x2 = (-b - math.sqrt(discriminant)) / (2 * a)
        if return_both:
            return x1, x2
        else:
            # Return the positive solution, if it exists
            if x1 >= 0:
                return x1
            elif x2 >= 0:
                return x2
            else:
                return f'Both negative, greater= {max(x1, x2)}'
    else:
        # If the discriminant is negative, there are no real solutions
        return None


def calculate_conc(ratios_tsv: str, equations_tsv: str, output: str, both_roots=True) -> pd.DataFrame:
    """
    Calculate the concentration, given the quadratic equation, and some other data.
    :param ratios_tsv: TSV with the peak area ratios for the samples
    :param equations_tsv: TSV with each standard name and respective quadratic equation
    :param output: file path to save the output TSV
    :param both_roots: If you want to return both roots. If False, returns only the positive one (or if both negative, the greater)
    :return: pd.Dataframe
    """
    global index
    results_df = pd.DataFrame()
    ratios_df = pd.read_csv(ratios_tsv, sep='\t')
    equations_df = pd.read_csv(equations_tsv, sep='\t')
    for i, compound, equation in equations_df.reset_index().values:
        a, b, c = equation.split()[2][:-2], equation.split()[4][:-1], equation.split()[6]
        for index in range(len(ratios_df)):
            y = ratios_df[compound][index]
            result = solve_quadratic(float(a), float(b), float(c), float(y), return_both=both_roots)
            if result:
                x1, x2 = result
            else:
                x1, x2 = ('None', 'None')
            results_df.at[index, 'filename'] = ratios_df.iloc[index]['filename']
            results_df.at[index, compound + '_x1'] = str(x1)
            results_df.at[index, compound + '_x2'] = str(x2)
    results_df.to_csv(output, sep='\t', index=False)
    return results_df


def main():
    # Defining parameters
    equations_tsv = './input/equations_template.tsv'
    ratios_tsv = './input/ratio_template.tsv'
    output = 'quantification_results.tsv'

    # Calling function
    calculate_conc(ratios_tsv, equations_tsv, output, both_roots=True)


if __name__ == '__main__':
    main()
