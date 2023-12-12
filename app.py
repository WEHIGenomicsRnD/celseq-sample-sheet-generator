from flask import Flask, request, render_template, send_from_directory
from operations import collate_fcs_files, plate_to_samplesheet, merge_fcs_data_with_samplesheet

import pandas as pd
import os

UPLOAD_FOLDER = 'uploads'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

COLLATED_FCS_FILENAME = 'fcs_data.tsv'
SAMPLESHEET_FILENAME = 'samplesheet.tsv'
MERGED_FILENAME = 'merged.tsv'

def render_index(fcs_files=None, plate_spreadsheet=None, sample_sheet=None, download_link=None, error=None):
    return render_template('index.html',
                           fcs_files=fcs_files,
                           plate_spreadsheet=plate_spreadsheet,
                           sample_sheet=sample_sheet,
                           download_link=download_link,
                           error=error)

def handle_plate_to_samplesheet(plate_spreadsheet):
    if not plate_spreadsheet:
        return render_index(error='Please upload a plate spreadsheet')

    plate_spreadsheet_filepath = os.path.join(app.config['UPLOAD_FOLDER'], plate_spreadsheet.filename)
    plate_spreadsheet.save(plate_spreadsheet_filepath)
    samplesheet = plate_to_samplesheet(plate_spreadsheet_filepath)

    # initiate download of csv file for user
    samplesheet_outpath = os.path.join(app.config['UPLOAD_FOLDER'], SAMPLESHEET_FILENAME)
    samplesheet.to_csv(samplesheet_outpath, index=False, sep='\t')
    return render_index(plate_spreadsheet=plate_spreadsheet, download_link=SAMPLESHEET_FILENAME) 

def handle_fcs_collate(fcs_files):
    if len(fcs_files) == 0:
        return render_index(error='Please upload at least one FACS file')
    
    for fcs_file in fcs_files:
        fcs_file.save(os.path.join(app.config['UPLOAD_FOLDER'], fcs_file.filename))

    fcs_data = collate_fcs_files(fcs_files, app.config['UPLOAD_FOLDER'])

    # initiate download of csv file for user
    fcs_data_output = os.path.join(app.config['UPLOAD_FOLDER'], COLLATED_FCS_FILENAME)
    fcs_data.to_csv(fcs_data_output, index=False, sep='\t')
    return render_index(fcs_files=fcs_files, download_link=COLLATED_FCS_FILENAME)

def handle_fcs_merge(sample_sheet):
    fcs_file = os.path.join(app.config['UPLOAD_FOLDER'], COLLATED_FCS_FILENAME)
    sample_sheet_filepath = os.path.join(app.config['UPLOAD_FOLDER'], SAMPLESHEET_FILENAME)

    if not sample_sheet and not os.path.exists(sample_sheet_filepath):
        return render_index(error='Please upload a sample sheet')
    if not os.path.exists(fcs_file):
        return render_index(error='Please collate your FACS data first!')
    
    if sample_sheet:
        sample_sheet.save(sample_sheet_filepath)
        sample_sheet_filepath = os.path.join(app.config['UPLOAD_FOLDER'], sample_sheet.filename)

    merged = merge_fcs_data_with_samplesheet(sample_sheet_filepath, fcs_file)

    merged_outpath = os.path.join(app.config['UPLOAD_FOLDER'], MERGED_FILENAME)
    merged.to_csv(merged_outpath, index=False, sep='\t')
    return render_index(sample_sheet=sample_sheet, download_link=MERGED_FILENAME)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        operation = request.form['operation']

        fcs_files = request.files.getlist('fcs_files')
        plate_spreadsheet = request.files['plate_spreadsheet']
        sample_sheet = request.files['sample_sheet']

        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        if operation == 'plate_to_samplesheet':
            return handle_plate_to_samplesheet(plate_spreadsheet)
        elif operation == 'fcs_collate':
            return handle_fcs_collate(fcs_files)
        elif operation == 'fcs_merge':
            return handle_fcs_merge(sample_sheet)
    else:
        return render_index()

if __name__ == '__main__':
    app.run(debug=True)