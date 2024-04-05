# main.py

from src.downloader import download_all
from src.renderer import setup_static_dirs, render_html
from src.preprocess import preprocess_data
import logging

logging.basicConfig(level=logging.INFO)

def main():
    setup_static_dirs()
    data, faq = download_all()

    processed_data = preprocess_data(data)

    
    # Render main and FAQ pages
    render_html('main.html', {'cards': processed_data}, 'static/index.html')
    render_html('faq.html', {'faq_data': faq}, 'static/faq.html')

    # Render individual cards, if needed
    for card in processed_data:
        render_html('card.html', {'card': card}, f"static/{card['id']}.html")

if __name__ == "__main__":
    main()

