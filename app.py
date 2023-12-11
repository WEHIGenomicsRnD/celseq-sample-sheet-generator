from flask import Flask, request, render_template, send_from_directory
from operations import merge_fcs_files, plate_to_samplesheet

import pandas as pd
import openpyxl
import fcsparser
import os

UPLOAD_FOLDER = 'uploads'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

MERGED_FCS_FILENAME = 'fcs_data.tsv'
SAMPLESHEET_FILENAME = 'samplesheet.tsv'

def render_index(fcs_files=None, xlsx_file=None, download_link=None, error=None):
    return render_template('index.html', fcs_files=fcs_files, xlsx_file=xlsx_file, download_link=download_link, error=error)

def handle_plate_to_samplesheet(xlsx_file):
    if not xlsx_file:
        return render_index(error='Please upload a spreadsheet')

    xlsx_filepath = os.path.join(app.config['UPLOAD_FOLDER'], xlsx_file.filename)
    xlsx_file.save(xlsx_filepath)
    samplesheet = plate_to_samplesheet(xlsx_filepath)

    # initiate download of csv file for user
    samplesheet_outpath = os.path.join(app.config['UPLOAD_FOLDER'], SAMPLESHEET_FILENAME)
    samplesheet.to_csv(samplesheet_outpath, index=False)
    return render_index(xlsx_file=xlsx_file, download_link=SAMPLESHEET_FILENAME) 

def handle_fcs_collate(fcs_files):
    if len(fcs_files) == 0:
        return render_index(error='Please upload at least one FACS file')
    
    for fcs_file in fcs_files:
        fcs_file.save(os.path.join(app.config['UPLOAD_FOLDER'], fcs_file.filename))

    # handle fcs merging
    fcs_data = merge_fcs_files(fcs_files, app.config['UPLOAD_FOLDER'])

    # initiate download of csv file for user
    fcs_data_output = os.path.join(app.config['UPLOAD_FOLDER'], MERGED_FCS_FILENAME)
    fcs_data.to_csv(fcs_data_output, index=False, sep='\t')
    return render_index(fcs_files=fcs_files, download_link=MERGED_FCS_FILENAME)

def handle_fcs_merge(xlsx_file):
    if not xlsx_file:
        return render_index(error='Please upload a spreadsheet')
    if not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], MERGED_FCS_FILENAME)):
        return render_index(error='Please collate your FACS data first!')
    # handle fcs_merge operation here

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        operation = request.form['operation']

        fcs_files = request.files.getlist('fcs_files')
        xlsx_file = request.files['xlsx_file']

        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        if operation == 'plate_to_samplesheet':
            return handle_plate_to_samplesheet(xlsx_file)
        elif operation == 'fcs_collate':
            return handle_fcs_collate(fcs_files)
        elif operation == 'fcs_merge':
            return handle_fcs_merge(xlsx_file)
    else:
        return render_index()

if __name__ == '__main__':
    app.run(debug=True)