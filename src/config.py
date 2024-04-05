from datetime import datetime

# URLs
SHEET_URL = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRRJBT6BewhEneccXKdgp2EK6SXDFxv4dJ8XRDbAVrUAV1B2xGiEiI3okoSwvkU09pNwx8oc8MvKWkv/pub?gid=696886356&single=true&output=csv'
FAQ_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRRJBT6BewhEneccXKdgp2EK6SXDFxv4dJ8XRDbAVrUAV1B2xGiEiI3okoSwvkU09pNwx8oc8MvKWkv/pub?gid=2108387313&single=true&output=csv"

# Save paths
SAVE_PATH_DATA = 'data/data.json'
SAVE_PATH_FAQ = "data/faq.json"

# Last updated time
LAST_UPDATED = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

