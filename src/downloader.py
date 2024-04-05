# downloader.py

import urllib.request
import csv
import json
import os
import logging
from urllib.parse import urlparse, parse_qs
from src.config import SHEET_URL, FAQ_URL, SAVE_PATH_DATA, SAVE_PATH_FAQ

def read_or_download(url, save_path):
    if os.path.exists(save_path):
        logging.info(f"Loading existing data from {save_path}.")
    else:
        try:
            with urllib.request.urlopen(url) as response, open(save_path, 'w') as out_file:
                data = csv.DictReader(response.read().decode("utf-8").splitlines())
                json_data = list(data)
                json.dump(json_data, out_file)
                logging.info(f"Data downloaded and saved to {save_path}.")
        except Exception as e:
            logging.error(f"Error downloading the file from {url}: {e}")
            return []

    with open(save_path, 'r') as file:
        data = json.load(file)
        for i in range(len(data)):
            escaped_json = data[i]
            for key, value in escaped_json.items():
                escaped_json[key] = value.replace('\\n', '\n') 

            data[i] = escaped_json

        return data

def download_all():
    data = read_or_download(SHEET_URL, SAVE_PATH_DATA)
    faq = read_or_download(FAQ_URL, SAVE_PATH_FAQ)
    return data, faq

def download_file_from_google_drive(url, destination):
    # Parse the URL

    if os.path.exists(destination):
        logging.info("Image already exists")
        return
        
    parse_result = urlparse(url)
    query_components = parse_qs(parse_result.query)
    
    # Extract the file ID
    file_id = query_components.get("id")[0] if "id" in query_components else None
    
    if file_id is None:
        logging.error(f"Error extracting ID from {url}")
        return
    
    # Construct the URL for direct access
    direct_url = f"https://drive.google.com/uc?export=download&id={file_id}"
    
    # Use urllib to download the file
    urllib.request.urlretrieve(direct_url, destination)

    logging.info(f"Data downloaded and saved to {destination}.")
