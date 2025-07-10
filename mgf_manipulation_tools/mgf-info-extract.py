#!/usr/bin/env python3
"""
MGF Keyword Extractor
Extracts specific keyword values from MGF files and saves them to a text file.
"""

import argparse
import os
import sys
from pathlib import Path


def extract_keyword_values(mgf_file, keyword, output_file=None, case_sensitive=False):
    """
    Extract values for a specific keyword from an MGF file.

    Args:
        mgf_file (str): Path to the MGF input file
        keyword (str): Keyword to search for (e.g., 'USI', 'TITLE', 'CHARGE')
        output_file (str): Path to output text file (optional)
        case_sensitive (bool): Whether to perform case-sensitive search

    Returns:
        list: List of extracted values
    """
    values = []

    try:
        with open(mgf_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()

                # Skip empty lines
                if not line:
                    continue

                # Check if line contains the keyword
                if case_sensitive:
                    if line.startswith(keyword + '='):
                        value = line[len(keyword) + 1:]
                        values.append(value)
                else:
                    if line.upper().startswith(keyword.upper() + '='):
                        value = line[len(keyword) + 1:]
                        values.append(value)

    except FileNotFoundError:
        print(f"Error: File '{mgf_file}' not found.")
        return []
    except Exception as e:
        print(f"Error reading file '{mgf_file}': {e}")
        return []

    # Write to output file if specified
    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                for value in values:
                    f.write(value + '\n')
            print(f"Extracted {len(values)} values and saved to '{output_file}'")
        except Exception as e:
            print(f"Error writing to output file '{output_file}': {e}")

    return values


def main():
    parser = argparse.ArgumentParser(
        description="Extract keyword values from MGF files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python mgf_extractor.py input.mgf USI
  python mgf_extractor.py input.mgf TITLE -o titles.txt
  python mgf_extractor.py input.mgf CHARGE -o charges.txt --case-sensitive
        """
    )

    parser.add_argument('mgf_file', help='Path to the MGF input file')
    parser.add_argument('keyword', help='Keyword to extract (e.g., USI, TITLE, CHARGE)')
    parser.add_argument('-o', '--output', help='Output text file path (optional)')
    parser.add_argument('--case-sensitive', action='store_true',
                        help='Perform case-sensitive keyword matching')

    args = parser.parse_args()

    # Validate input file
    if not os.path.exists(args.mgf_file):
        print(f"Error: Input file '{args.mgf_file}' does not exist.")
        sys.exit(1)

    # Generate output filename if not provided
    output_file = args.output
    if not output_file:
        mgf_path = Path(args.mgf_file)
        output_file = mgf_path.stem + f'_{args.keyword.lower()}_values.txt'

    # Extract values
    values = extract_keyword_values(
        args.mgf_file,
        args.keyword,
        output_file,
        args.case_sensitive
    )

    # Print results
    if values:
        print(f"\nFound {len(values)} values for keyword '{args.keyword}':")
        for i, value in enumerate(values[:10], 1):  # Show first 10 values
            print(f"  {i}: {value}")

        if len(values) > 10:
            print(f"  ... and {len(values) - 10} more values")
    else:
        print(f"No values found for keyword '{args.keyword}' in '{args.mgf_file}'")


if __name__ == "__main__":
    main()