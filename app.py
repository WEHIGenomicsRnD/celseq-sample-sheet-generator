from flask import Flask, request, render_template, send_from_directory
from operations import collate_fcs_files, plate_to_samplesheet, merge_fcs_data_with_samplesheet
from werkzeug.utils import secure_filename

import pandas as pd
import os

UPLOAD_FOLDER = 'uploads'
COLLATED_FCS_FILENAME = 'fcs_data.tsv'
SAMPLESHEET_FILENAME = 'samplesheet.tsv'
MERGED_FILENAME = 'merged.tsv'

uploaded_sample_sheet = None

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def render_index(fcs_files=None, plate_spreadsheet=None, sample_sheet=None, error=None):

    collated_fcs_file, samplesheet_file, merged_file = None, None, None
    collated_fcs_path = os.path.join(app.config['UPLOAD_FOLDER'], COLLATED_FCS_FILENAME)
    merged_path = os.path.join(app.config['UPLOAD_FOLDER'], MERGED_FILENAME)
    if uploaded_sample_sheet:
        samplesheet_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_sample_sheet)
    else:
        samplesheet_path = os.path.join(app.config['UPLOAD_FOLDER'], SAMPLESHEET_FILENAME)

    if os.path.exists(collated_fcs_path):
        collated_fcs_file = COLLATED_FCS_FILENAME
    if os.path.exists(samplesheet_path):
        samplesheet_file = SAMPLESHEET_FILENAME
    if os.path.exists(merged_path):
        merged_file = MERGED_FILENAME

    return render_template('index.html',
                           fcs_files=fcs_files,
                           plate_spreadsheet=plate_spreadsheet,
                           sample_sheet=sample_sheet,
                           collated_fcs_file=collated_fcs_file,
                           samplesheet_file=samplesheet_file,
                           merged_file=merged_file,
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
    return render_index(plate_spreadsheet=plate_spreadsheet) 

def handle_fcs_collate(fcs_files):
    if len(fcs_files) == 0:
        return render_index(error='Please upload at least one FACS file')
    
    for fcs_file in fcs_files:
        fcs_file.save(os.path.join(app.config['UPLOAD_FOLDER'], fcs_file.filename))

    fcs_data = collate_fcs_files(fcs_files, app.config['UPLOAD_FOLDER'])

    # initiate download of csv file for user
    fcs_data_output = os.path.join(app.config['UPLOAD_FOLDER'], COLLATED_FCS_FILENAME)
    fcs_data.to_csv(fcs_data_output, index=False, sep='\t')
    return render_index(fcs_files=fcs_files)

def handle_fcs_merge(sample_sheet):
    fcs_file = os.path.join(app.config['UPLOAD_FOLDER'], COLLATED_FCS_FILENAME)
    sample_sheet_filepath = os.path.join(app.config['UPLOAD_FOLDER'], SAMPLESHEET_FILENAME)

    if not sample_sheet and not os.path.exists(sample_sheet_filepath):
        return render_index(error='Please upload a sample sheet')
    if not os.path.exists(fcs_file):
        return render_index(error='Please collate your FACS data first!')
    
    if sample_sheet:
        uploaded_sample_sheet = secure_filename(sample_sheet.filename)
        sample_sheet_filepath = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_sample_sheet)
        sample_sheet.save(sample_sheet_filepath)

    merged = merge_fcs_data_with_samplesheet(sample_sheet_filepath, fcs_file)

    merged_outpath = os.path.join(app.config['UPLOAD_FOLDER'], MERGED_FILENAME)
    merged.to_csv(merged_outpath, index=False, sep='\t')
    return render_index(sample_sheet=sample_sheet)

@app.route('/delete_file', methods=['POST'])
def delete_file():
    filename = request.form.get('filename')
    if filename:
        filename = secure_filename(filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            os.remove(file_path)
    return render_index()

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    filename = secure_filename(filename)
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