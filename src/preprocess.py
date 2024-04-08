# preprocess.py

from typing import List
import bleach
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import html
from src.downloader import download_file_from_google_drive
import mistune
import re


def remove_image_tags(html_string):
    # This pattern matches any <img> tag
    pattern = r'<img[^>]+>'
    # Replace all occurrences of the image tag with an empty string
    cleaned_string = re.sub(pattern, '', html_string)
    return cleaned_string

class HighlightRenderer(mistune.HTMLRenderer):
    def block_code(self, code, info=None):
        if info:
            lexer = get_lexer_by_name(info, stripall=True)
            formatter = html.HtmlFormatter()
            return highlight(code, lexer, formatter)
        return '<pre><code>' + mistune.escape(code) + '</code></pre>'

def make_url_safe_remove_unsafe(s):
    s_lower = s.lower()
    s_hyphens = s_lower.replace(' ', '-')
    s_safe = re.sub(r'[^a-z0-9-]', '', s_hyphens)
    return s_safe

def add_pre_tags_around_code_regex(html_str):
    pattern = r'(<code>.*?</code>)'
    def wrap_with_pre(match):
        return '<pre>' + match.group(1) + '</pre>'
    modified_html = re.sub(pattern, wrap_with_pre, html_str, flags=re.DOTALL)
    return modified_html

def updated_id(title: str, id_num: str) -> str:

    print("####", title, id_num)

    new_id = make_url_safe_remove_unsafe(title) + f"-{id_num}"
    new_id = new_id.replace("--", "-")
    return new_id

def download_images(card):
    """
    Id neeed to be updated beforehand.
    """

    for key, value in card.items():
        if key.startswith("img") and value:

            img_num = key.split("img")[-1]
            img_url = f"img/{card['id']}_{img_num}.jpg"

            # print(key, value, img_url)
            download_file_from_google_drive(value, "static/" + img_url)

            card[key] = img_url


def replace_image_placeholder(field, card):

    text = card[field]
    for i in range(1, 10):
        img_url = card.get(f"img{i}", None)
        if img_url is not None:
            # print(text, i, img_url)
            tag = f"<img src='{img_url}'>"
            text = text.replace(f"@img{i}", tag)

            card[field] = text

    return card


FIELDS_WITH_IMAGES = ["prompt", "answer", "analysis"]
ALLOWED_TAGS = ['div', 'p','a', 'strong', 'em', 'ul', 'li', 'h1', 'h2', 'h3', 'pre', 'code', 'br', 'img']

def card_to_html(card_json):

    renderer = HighlightRenderer(escape=False)
    markdown_renderer = mistune.Markdown(renderer=renderer)

    card_json["id"] = updated_id(card_json["title"], card_json["id"] )

    download_images(card_json)

    for field in FIELDS_WITH_IMAGES:
        card_json = replace_image_placeholder(field, card_json)


    card_json["front"] = remove_image_tags(card_json["prompt"].strip())

    for key in ["about", "front", "prompt", "answer", "analysis"]:
        text = card_json[key]
        html = markdown_renderer(text) 
        # safe_html = bleach.clean(html, tags=ALLOWED_TAGS, strip=True)

        # card_json[key] = safe_html
        card_json[key] = html

    

    return card_json

def preprocess_data(data) -> List:
    print(data)
    return [card_to_html(card) for card in data if card["id"]]

