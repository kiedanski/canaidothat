import datetime
import markdown
import bleach
import urllib.request
import os
import csv
import json
from jinja2 import Environment, FileSystemLoader, select_autoescape
from urllib.parse import urlparse, parse_qs


SHEET_URL = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRRJBT6BewhEneccXKdgp2EK6SXDFxv4dJ8XRDbAVrUAV1B2xGiEiI3okoSwvkU09pNwx8oc8MvKWkv/pub?gid=696886356&single=true&output=csv'

SAVE_PATH = 'data.json'

os.makedirs("static", exist_ok=True)
os.makedirs("static/img", exist_ok=True)

last_updated = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

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
        return data
    except Exception as e:
        print(f'Error downloading the file: {e}')

def download_file_from_google_drive(url, destination):
    # Parse the URL
    parse_result = urlparse(url)
    query_components = parse_qs(parse_result.query)
    
    # Extract the file ID
    file_id = query_components.get("id")[0] if "id" in query_components else None
    
    if file_id is None:
        print("File ID could not be extracted.")
        return
    
    # Construct the URL for direct access
    direct_url = f"https://drive.google.com/uc?export=download&id={file_id}"
    
    # Use urllib to download the file
    urllib.request.urlretrieve(direct_url, destination)
    
    print(f"File has been downloaded to: {destination}")

def card_to_html(card_json):
    id_ = card_json["id"]

    card_json["front"] = card_json["prompt"].strip()
    card_json["has_image"] = False

    for key in ["front", "prompt", "answer", "analysis"]:
        text = card_json[key]
        html = markdown.markdown(text).replace("\\n", "<br>")
        safe_answer = bleach.clean(html, tags=['p', 'strong', 'em', 'ul', 'li', 'h1', 'h2', 'h3', 'pre', 'code', 'br'], strip=True)

        if key == "front":
            if "@img1" in safe_answer:
                card_json["has_image"] = True
            safe_answer = safe_answer.replace("@img1", "")
        else:
            safe_answer = safe_answer.replace("@img1", f"<img style='width:600px' src='img/{id_}_1.jpg'>")

        safe_answer = safe_answer.replace("<br><br>", "<br>")
        card_json[key] = safe_answer

    return card_json

data = []
if os.path.exists(SAVE_PATH):
    print("Skipping download")
    with open(SAVE_PATH, "r") as fh: data = json.load(fh)
else:
    data = download_sheet_as_json()
    for card in data:
        img1 = card.get("img1", None)
        id_ = card.get("id", None)
        if img1 and id_:
            download_file_from_google_drive(img1, f"static/img/{id_}_1.jpg")

data = list(filter(lambda x: x["id"] != "", data))

for i, card in enumerate(data):
    card_id = card["id"]
    card = card_to_html(card)
    data[i] = card




# Set up Jinja2 environment
env = Environment(
    loader=FileSystemLoader('.'),
    autoescape=select_autoescape(['html', 'xml'])
)

# Load the template
template = env.get_template('base.html')

# Render the template with data
html_output = template.render(cards=data, last_updated=last_updated)


# Save the rendered HTML to a file
with open('static/index.html', 'w') as f:
    f.write(html_output)

print("Site generated successfully.")




card_template = env.get_template("card.html")
for card in data:
    card_id = card["id"]
    card_output = card_template.render(card=card)
    with open(f"static/{card_id}.html", "w") as f:
        f.write(card_output)
