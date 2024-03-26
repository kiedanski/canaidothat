import urllib.request
import os
import csv
import json
from jinja2 import Environment, FileSystemLoader, select_autoescape

SHEET_URL = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRRJBT6BewhEneccXKdgp2EK6SXDFxv4dJ8XRDbAVrUAV1B2xGiEiI3okoSwvkU09pNwx8oc8MvKWkv/pub?gid=696886356&single=true&output=csv'

SAVE_PATH = 'data.json'

def download_sheet_as_json():

    try:
        with urllib.request.urlopen(SHEET_URL) as response, open(SAVE_PATH, 'w') as out_file:
            data = response.read().decode("utf-8")  # Read the data from the URL
            print(data)
            data = [dict(r) for r in csv.DictReader(data.split("\n"))]
            print(data)
            json.dump(data, out_file)


            # out_file.write(data)  # Write the data to a local file
        print(f'File downloaded')
    except Exception as e:
        print(f'Error downloading the file: {e}')

if os.path.exists(SAVE_PATH):
    with open(SAVE_PATH, "r") as fh: data = json.load(fh)
else:
    download_sheet_as_json()




# Set up Jinja2 environment
env = Environment(
    loader=FileSystemLoader('.'),
    autoescape=select_autoescape(['html', 'xml'])
)

# Load the template
template = env.get_template('base.html')

# Render the template with data
html_output = template.render(cards=data)

# Save the rendered HTML to a file
with open('index.html', 'w') as f:
    f.write(html_output)

print("Site generated successfully.")

