#!/bin/python3

import argparse
import pandas as pd
from pathlib import Path
from operations import (
    plate_to_samplesheet,
    collate_fcs_files,
    merge_data_with_samplesheet,
    load_excel_samplesheet
)

def create_temp_folder():
    """Create a temporary folder if it doesn't exist."""
    temp_file_path = Path('temp')
    temp_file_path.mkdir(parents=True, exist_ok=True)
    return temp_file_path

def process_files(plate_layout_path, fcs_files, template_sheet_path, primer_index_path, output_file):
    """
    Process files according to the GMM testing operations.

    Parameters:
    - plate_layout_path: Path to the plate layout file.
    - fcs_file: Path to the FCS file.
    - template_sheet_path: Path to the template sheet file.
    - primer_index_path: Path to the primer index file.
    - output_file: Path and name of the output file, including desired extension.
    """
    # TODO: Need to refactor, the logic is getting too convoluted
    # Determine output format based on file extension
    output_format = output_file.split('.')[-1]

    plate_layout_provided = plate_layout_path is not None and \
        plate_layout_path != ""
    fcs_files_provided = fcs_files is not None and fcs_files != ""
    template_sheet_provided = template_sheet_path is not None and \
        template_sheet_path != ""
    primer_index_provided = primer_index_path is not None and \
        primer_index_path != ""

    if not plate_layout_provided and not fcs_files_provided and \
       not template_sheet_provided and not primer_index_provided:
        raise ValueError(
            """No input files provided. Please provide at
            least one input file."""
        )

    sample_sheet_df = pd.DataFrame()
    if plate_layout_provided:
        # Operation 1: Create Sample Sheet from Plate Layout
        sample_sheet_df = plate_to_samplesheet(Path(plate_layout_path))
        sample_sheet_output_path = 'temp/op1_plate_layout_to_spreadsheet.tsv'
        sample_sheet_df.to_csv(sample_sheet_output_path, sep='\t', index=False)
    elif not template_sheet_provided and not primer_index_provided:
        sample_sheet_output_path = None
    elif template_sheet_provided:
        sample_sheet_output_path = template_sheet_path
    else:
        sample_sheet_output_path = primer_index_path

    collated_fcs_output_path = None
    if fcs_files_provided:
        # Operation 2: Combine FCS Files into One Document
        collated_fcs_df = collate_fcs_files(fcs_files.split(' '), "")
        collated_fcs_output_path = 'temp/op2_collate_fcs_files.tsv'
        collated_fcs_df.to_csv(collated_fcs_output_path, sep='\t', index=False)

    if template_sheet_provided:
        # Operation 3: Merge All Data into Comprehensive File
        merged_df = merge_data_with_samplesheet(spreadsheet_filepath=sample_sheet_output_path,
                                                fcs_file=collated_fcs_output_path,
                                                template_sheet_filepath=Path(template_sheet_path))
        if primer_index_provided:
            # Operation 4 (Optional): Add Primer Index to Comprehensive File
            primer_index_df = load_excel_samplesheet(primer_index_path)

            # TODO: generalise this code as we are also checking the template sheet
            # Make sure we have a sample column
            sample_cols = ['Sample', 'Sample name', 'Sample type']
            if not any(col in primer_index_df.columns for col in sample_cols):
                raise ValueError("Sample column not found in primer index sheet.")

            # Coerce sample column to string
            sample_col = next(col for col in sample_cols if col in primer_index_df.columns)
            primer_index_df[sample_col] = primer_index_df[sample_col].fillna('').astype(str)

            # primer_index_df.rename({'Plate#': 'plate', 'Well position': 'well_position', 'Sample name': 'sample'}, axis=1, inplace=True)
            merged_df = pd.merge(merged_df, primer_index_df, on=['Plate#', 'Well position', 'Sample name'], how='left', suffixes=('', '_primer'))
    elif primer_index_provided:
        merged_df = merge_data_with_samplesheet(spreadsheet_filepath=sample_sheet_output_path,
                                                fcs_file=collated_fcs_output_path,
                                                template_sheet_filepath=None)
    elif fcs_files_provided and not plate_layout_provided:
        # need to sort FCS DF by sample then well position
        merged_df = collated_fcs_df.drop_duplicates(subset=['Plate#', 'Well position'], keep='first')
    else:
        merged_df = sample_sheet_df

    # Drop columns with empty values that start with a single character followed by a period or 'unnamed'
    cols_to_drop = [col for col in merged_df.columns if (col.startswith(('X.', 'Y.')) or col.startswith('unnamed')) and merged_df[col].isna().all()]
    merged_df.drop(columns=cols_to_drop, inplace=True)
    
    # Output file processing
    if 'csv' in output_file or 'tsv' in output_format:
        sep = ',' if 'csv' in output_file else '\t'
        # print(sep)
        merged_df.to_csv(output_file, sep=sep, index=False)
    elif 'xlsx' in output_format:
        merged_df.to_excel(output_file, index=False)

def main():
    """Main function to parse arguments and call processing functions."""
    parser = argparse.ArgumentParser(description='Process GMM testing files.')
    parser.add_argument('-pl', '--plate-layout', required=False, help='Path to plate layout file')
    parser.add_argument('-fcs', '--fcs-files', required=False, help='Path to FCS file')
    parser.add_argument('-ts', '--template-sheet', required=False, help='Path to template sheet file')
    parser.add_argument('-pi', '--primer-index', required=False, help='Path to primer index file')
    parser.add_argument('-o', '--output-file', required=True, help='Full path and file name for the output, including extension (.csv, .tsv, .xlsx)')
    
    args = parser.parse_args()
    create_temp_folder()

    process_files(plate_layout_path=args.plate_layout, 
                  fcs_files=args.fcs_files, 
                  template_sheet_path=args.template_sheet, 
                  primer_index_path=args.primer_index, 
                  output_file=args.output_file)

if __name__ == "__main__":
    main()
