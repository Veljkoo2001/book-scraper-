# config/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

# Konfiguracija iz .env fajla ili default vrednosti
HEADLESS = os.getenv('HEADLESS', 'true').lower() == 'true'
MAX_PAGES = int(os.getenv('MAX_PAGES', 3))
DB_PATH = os.getenv('DB_PATH', 'data/database/books.db')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
EXPORT_FORMAT = os.getenv('EXPORT_FORMAT', 'csv')

# Chrome options
CHROME_OPTIONS = [
    '--headless' if HEADLESS else '',
    '--no-sandbox',
    '--disable-dev-shm-usage',
    '--disable-gpu',
    '--window-size=1920,1080',
    '--disable-blink-features=AutomationControlled',
]

# Website URLs
BASE_URLS = {
    'books': 'https://books.toscrape.com/',
    # Dodaj druge sajtove kasnije
}

# Request settings
REQUEST_DELAY = 2  # seconds
MAX_RETRIES = 3
TIMEOUT = 30