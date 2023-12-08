# CELSeq sample sheet generator

This application is designed to:

- Take plate designs and convert them to a row-wise spreadsheet showing sample ID for each well position.
- Extract well metadata from FACS files and convert this to a well position naming scheme (e.g., A1, A2 etc.)
- Take a row-wise sample spreadsheet and integrate FACS data into it, merging by plate, sample ID and well position.

## Project Structure

- `app.py`: This is the main Python script that runs the Flask application.
- `fcs_data.csv`: This is a CSV file that stores the processed FCS data.
- `prototypes/`: This directory contains Jupyter notebooks used for prototyping the data processing scripts.
- `static/`: This directory contains static files for the Flask application.
- `templates/`: This directory contains HTML templates for the Flask application.
- `uploads/`: This directory is where the uploaded FCS files are stored.

## How to Run

1. Ensure you have Python and Flask installed on your machine.
2. Run the `app.py` script to start the Flask application.
3. Navigate to the application in your web browser to upload and process FCS files.

## Features

- **Plate Layout to Spreadsheet**: Users can generate a sample spreadsheet from a colour-coded plate design.
- **Collate FCS Data**: The application can collate data from multiple FCS files into a single CSV file.
- **Merge FCS Data**: The application can merge FCS data with a spreadsheet.

Please refer to the code and comments in `app.py` for more details on how these features are implemented.