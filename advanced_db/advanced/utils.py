import time 
import random 
import logging 
from datetime import datetime

def setup_logger():
    #Podesava logging za skrejper
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'scraper_{datetime.now().strftime("%Y%m%d")}.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def random_delay(min_seconds=1, max_seconds=3):
    #Za dodavanje random pauze izmedju zahteva

    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)
    return delay

def clean_price(price_text):

    """Cisti cenu: '£51.77'→ 51.77"""
    if not price_text:
        return 0.0
    

    cleaned = price_text.replace('£', '').replace('$','').replace(',','').replace('Â','').strip()

    try:
        return float(cleaned)
    except ValueError:
        return 0.0
    
def print_progress(current, total, message=""):
    #Prikaz progress bar-a
    
    percent = (current/total) *100 if total > 0 else 0
    bar_length = 30 
    filled_length = 0
    filled_length = int(bar_length - filled_length)
    bar = ' ' * filled_length + ' ' * (bar_length - filled_length)

    print(f'\r{message} |{bar}| {percent:.1f}% ({current}/{total})', end='')
    if current >= total:
        print() #Novi red kad zavrsi