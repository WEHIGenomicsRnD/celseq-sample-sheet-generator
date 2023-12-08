from flask import Flask, request, render_template, send_from_directory
import pandas as pd
import openpyxl
import fcsparser
import os

UPLOAD_FOLDER = 'uploads'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

FCS_DATA_FILENAME = 'fcs_data.csv'

def render_index(fcs_files=None, xlsx_file=None, download_link=None, error=None):
    return render_template('index.html', fcs_files=fcs_files, xlsx_file=xlsx_file, download_link=download_link, error=error)

def handle_plate_to_sheet(xlsx_file):
    if not xlsx_file:
        return render_index(error='Please upload a spreadsheet')
    # handle plate_to_sheet operation here

def handle_fcs_collate(fcs_files):
    if len(fcs_files) == 0:
        return render_index(error='Please upload at least one FACS file')
    
    for fcs_file in fcs_files:
        fcs_file.save(os.path.join(app.config['UPLOAD_FOLDER'], fcs_file.filename))

    # handle fcs merging
    fcs_data = pd.DataFrame()

    for fcs_file in fcs_files:
        fcs_savepath = os.path.join(app.config['UPLOAD_FOLDER'], fcs_file.filename)

        meta, data = fcsparser.parse(fcs_savepath, meta_data_only=False, reformat_meta=True)
        data = data.sort_values('Time')
        data['well_position'] = get_well_positions(meta)

        plate, sample = get_plate_and_sample_from_filepath(fcs_savepath)
        data['plate'] = plate
        data['sample'] = sample

        fcs_data = pd.concat([fcs_data, data])

    # initiate download of csv file for user
    fcs_data_output = os.path.join(app.config['UPLOAD_FOLDER'], 'fcs_data.csv')
    fcs_data.to_csv(fcs_data_output, index=False)
    return render_index(fcs_files=fcs_files, download_link='fcs_data.csv')

def handle_fcs_merge(xlsx_file):
    if not xlsx_file:
        return render_index(error='Please upload a spreadsheet')
    if not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], 'fcs_data.csv')):
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

        if operation == 'plate_to_sheet':
            return handle_plate_to_sheet(xlsx_file)
        elif operation == 'fcs_collate':
            return handle_fcs_collate(fcs_files)
        elif operation == 'fcs_merge':
            return handle_fcs_merge(xlsx_file)
    else:
        return render_index()

def get_well_positions(meta):
    '''
    Extract well positions (e.g., A1, A2 etc.) from FCS file metadata,
    ordered by sorting locations.   
    '''
    metalist = list(meta.keys())
    locnames = [item for item in metalist if item.startswith('INDEX SORTING LOCATIONS')]
    locnames = sorted(locnames, key=lambda s: int(s.split('_')[1]))

    wells = []
    for locname in locnames:
        loclist = meta[locname]
        locs = loclist.split(";")

        for loc in locs:
            if loc:
                x, y = loc.split(",")
                new_x = chr(int(x) + ord('A'))
                new_y = str(int(y) + 1)
                wells.append(new_x + new_y)

    return wells

def get_plate_and_sample_from_filepath(fcs_filepath):
    '''
    Extract plate and sample name from file names in format
    e.g., DDmonthYY_INX_samplename_platename.fcs where plate
    name starts with LCE.
    '''
    filename = os.path.basename(fcs_filepath)
    filename = os.path.splitext(filename)[0]

    # Extract the plate name
    plate_start_index = filename.find('LCE')
    if plate_start_index != -1:
        plate = filename[plate_start_index:]

    # Extract the sample name
    sample_start_index = filename.find('INX_')
    if sample_start_index != -1:
        sample_name = filename[sample_start_index + len('INX_'):(plate_start_index - 1)]

    return plate, sample_name

if __name__ == '__main__':
    app.run(debug=True)