# renderer.py
import logging

from jinja2 import Environment, FileSystemLoader, select_autoescape
import shutil
import os
from .config import LAST_UPDATED

env = Environment(
    loader=FileSystemLoader('templates/'),
    autoescape=select_autoescape(['html', 'xml'])
)

def setup_static_dirs():
    paths = ["static", "static/img", "data"]
    for path in paths:
        os.makedirs(path, exist_ok=True)
    shutil.copy("libs/htmx.org@1.9.11", "static/")
    shutil.copy("libs/tailwind.min.css", "static/")

def render_html(template_name, context, output_path):
    template = env.get_template(template_name)
    context['last_updated'] = LAST_UPDATED
    output = template.render(context)
    with open(output_path, 'w') as f:
        f.write(output)
    logging.info(f"Rendered HTML for {template_name} saved to {output_path}.")

