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

def render_index(fcs_files=None, spreadsheet=None, download_link=None, error=None):
    return render_template('index.html', fcs_files=fcs_files, spreadsheet=spreadsheet, download_link=download_link, error=error)

def handle_plate_to_samplesheet(spreadsheet):
    if not spreadsheet:
        return render_index(error='Please upload a spreadsheet')

    spreadsheet_filepath = os.path.join(app.config['UPLOAD_FOLDER'], spreadsheet.filename)
    spreadsheet.save(spreadsheet_filepath)
    samplesheet = plate_to_samplesheet(spreadsheet_filepath)

    # initiate download of csv file for user
    samplesheet_outpath = os.path.join(app.config['UPLOAD_FOLDER'], SAMPLESHEET_FILENAME)
    samplesheet.to_csv(samplesheet_outpath, index=False, sep='\t')
    return render_index(spreadsheet=spreadsheet, download_link=SAMPLESHEET_FILENAME) 

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

def handle_fcs_merge(spreadsheet):
    fcs_file = os.path.join(app.config['UPLOAD_FOLDER'], COLLATED_FCS_FILENAME)
    if not spreadsheet:
        return render_index(error='Please upload a spreadsheet')
    if not os.path.exists(fcs_file):
        return render_index(error='Please collate your FACS data first!')
    
    spreadsheet_filepath = os.path.join(app.config['UPLOAD_FOLDER'], spreadsheet.filename)
    spreadsheet.save(spreadsheet_filepath)
    merged = merge_fcs_data_with_samplesheet(spreadsheet_filepath, fcs_file)

    merged_outpath = os.path.join(app.config['UPLOAD_FOLDER'], MERGED_FILENAME)
    merged.to_csv(merged_outpath, index=False, sep='\t')
    return render_index(spreadsheet=spreadsheet, download_link=MERGED_FILENAME)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        operation = request.form['operation']

        fcs_files = request.files.getlist('fcs_files')
        spreadsheet = request.files['spreadsheet']

        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        if operation == 'plate_to_samplesheet':
            return handle_plate_to_samplesheet(spreadsheet)
        elif operation == 'fcs_collate':
            return handle_fcs_collate(fcs_files)
        elif operation == 'fcs_merge':
            return handle_fcs_merge(spreadsheet)
    else:
        return render_index()

if __name__ == '__main__':
    app.run(debug=True)