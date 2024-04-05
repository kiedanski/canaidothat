import shutil
import datetime
import re
# import markdown
import bleach
import urllib.request
import os
import csv
import json
from jinja2 import Environment, FileSystemLoader, select_autoescape
from urllib.parse import urlparse, parse_qs
import mistune
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import html


SHEET_URL = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRRJBT6BewhEneccXKdgp2EK6SXDFxv4dJ8XRDbAVrUAV1B2xGiEiI3okoSwvkU09pNwx8oc8MvKWkv/pub?gid=696886356&single=true&output=csv'
FAQ_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRRJBT6BewhEneccXKdgp2EK6SXDFxv4dJ8XRDbAVrUAV1B2xGiEiI3okoSwvkU09pNwx8oc8MvKWkv/pub?gid=2108387313&single=true&output=csv"

SAVE_PATH_DATA = 'data.json'
SAVE_PATH_FAQ = "faq.json"


# shutil.rmtree("static/", ignore_errors=True)
os.makedirs("static", exist_ok=True)
os.makedirs("static/img", exist_ok=True)

shutil.copy("libs/htmx.org@1.9.11", "static/")
shutil.copy("libs/tailwind.min.css", "static/")

class HighlightRenderer(mistune.HTMLRenderer):
    def block_code(self, code, info=None):
        if info:
            lexer = get_lexer_by_name(info, stripall=True)
            formatter = html.HtmlFormatter()
            return highlight(code, lexer, formatter)
        return '<pre><code>' + mistune.escape(code) + '</code></pre>'


last_updated = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

import re

def add_pre_tags_around_code_regex(html_str):
    """
    Wraps <pre> tags around <code> tags in the given HTML string using regex.

    Args:
    - html_str (str): The input HTML string.

    Returns:
    - str: The modified HTML string with <pre> tags wrapped around <code> tags.
    """
    # Define a regex pattern to match <code>...</code> blocks
    pattern = r'(<code>.*?</code>)'
    
    # Define a function to be applied to each match
    def wrap_with_pre(match):
        return '<pre>' + match.group(1) + '</pre>'
    
    # Use re.sub() to apply the wrap_with_pre function to each match
    modified_html = re.sub(pattern, wrap_with_pre, html_str, flags=re.DOTALL)
    
    return modified_html




def make_url_safe_remove_unsafe(s):
    s_lower = s.lower()
    s_hyphens = s_lower.replace(' ', '-')
    s_safe = re.sub(r'[^a-z0-9-]', '', s_hyphens)
    return s_safe

# Test the function with a sample string

def download_sheet_as_json(URL, SAVE_PATH):

    try:
        with urllib.request.urlopen(URL) as response, open(SAVE_PATH, 'w') as out_file:
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
    card_json["id"] = make_url_safe_remove_unsafe(card_json["title"]) + f"-{card_json['id']}"
    id_ = card_json["id"]

    card_json["front"] = card_json["prompt"].strip()
    card_json["has_image"] = False


    markdown_render = mistune.create_markdown(renderer=HighlightRenderer())

    has_image = False
    for key in ["front", "prompt", "answer", "analysis"]:
        text = card_json[key]
        # html = markdown.markdown(text)
        html = markdown_render(text).replace("\\n", "<br>")

        safe_answer = bleach.clean(html, tags=['p', 'strong', 'em', 'ul', 'li', 'h1', 'h2', 'h3', 'pre', 'code', 'br'], strip=True)
        safe_answer = add_pre_tags_around_code_regex(safe_answer)

        if "@img1" in text:
            has_image = True

        if key == "front":
            if "@img1" in safe_answer:
                card_json["has_image"] = True
            safe_answer = safe_answer.replace("@img1", "").replace("<br>", "")
        else:
            safe_answer = safe_answer.replace("@img1", f"<img style='width:600px' src='img/{id_}_1.jpg'>")

        safe_answer = safe_answer.replace("<br><br>", "<br>")
        card_json[key] = safe_answer

    if has_image:
        card_json["image"] = f"img/{id_}_1.jpg"

    return card_json

data = []
download_images = False
if os.path.exists(SAVE_PATH_DATA):
    print("Skipping download")
    with open(SAVE_PATH_DATA, "r") as fh: data = json.load(fh)
else:
    data = download_sheet_as_json(SHEET_URL, SAVE_PATH_DATA)
    download_images = True

if os.path.exists(SAVE_PATH_FAQ):
    print("Skipping download")
    with open(SAVE_PATH_FAQ, "r") as fh: faq = json.load(fh)
else:
    faq = download_sheet_as_json(FAQ_URL, SAVE_PATH_FAQ)

data = list(filter(lambda x: x["id"] != "", data))

for i, card in enumerate(data):
    card_id = card["id"]
    card = card_to_html(card)
    data[i] = card

if download_images:
    for card in data:
        img1 = card.get("img1", None)
        id_ = card.get("id", None)
        if img1 and id_:
            download_file_from_google_drive(img1, f"static/img/{id_}_1.jpg")



# Set up Jinja2 environment
env = Environment(
    loader=FileSystemLoader('templates/'),
    autoescape=select_autoescape(['html', 'xml'])
)

# Load the template
template = env.get_template('main.html')

# Render the template with data
html_output = template.render(cards=data, last_updated=last_updated, subpage_title="Will AI", main_image=None)


# Save the rendered HTML to a file
with open('static/index.html', 'w') as f:
    f.write(html_output)

print("Site generated successfully.")

print(faq)
faq_html = env.get_template("faq.html").render(faq_data=faq, last_updated=last_updated)
with open("static/faq.html", "w") as f: f.write(faq_html)



card_template = env.get_template("card.html")
for card in data:
    card_id = card["id"]
    card_output = card_template.render(card=card, last_updated=last_updated, subpage_title=card["title"], main_image=card.get("image", None), domain="https://willaidothis.com")
    with open(f"static/{card_id}.html", "w") as f:
        f.write(card_output)
