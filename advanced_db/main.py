# main.py - POPRAVLJENA VERZIJA BEZ EMOJI (Windows compatible)
import argparse
import logging
import sys
import os
import time
from bs4 import BeautifulSoup

# Dodaj root folder u Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from scrapers.selenium_scraper import SeleniumScraper
except ImportError as e:
    print(f"ERROR: Cannot import SeleniumScraper: {e}")
    print("Check if scrapers/selenium_scraper.py exists")
    sys.exit(1)

try:
    from database.db_handler import DatabaseHandler
except ImportError as e:
    print(f"ERROR: Cannot import DatabaseHandler: {e}")
    print("Check if database/db_handler.py exists with DatabaseHandler class")
    sys.exit(1)

# ============================================================================
# PODEŠAVANJE LOGGING-A ZA WINDOWS (bez emoji)
# ============================================================================

# Kreiraj logs folder ako ne postoji
os.makedirs('logs', exist_ok=True)

# Konfiguriši logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/scraper.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)  # Koristi stdout umesto stderr za bolje encoding
    ]
)

# Postavi encoding za console handler
for handler in logging.getLogger().handlers:
    if isinstance(handler, logging.StreamHandler):
        handler.stream.reconfigure(encoding='utf-8', errors='replace')  # errors='replace' za Windows

logger = logging.getLogger(__name__)

# ============================================================================
# POMOĆNE FUNKCIJE
# ============================================================================

def parse_price(price_text):
    """Parsiraj cenu iz teksta u float."""
    import re
    try:
        cleaned = re.sub(r'[^\d.]', '', price_text)
        return float(cleaned) if cleaned else 0.0
    except:
        return 0.0

def parse_rating(rating_text):
    """Parsiraj rejting u broj (1-5)."""
    rating_map = {
        'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5,
        'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
        'Zero': 0, 'zero': 0
    }
    return rating_map.get(rating_text, 0)

def extract_books_from_html(html_content):
    """Ekstraktuj knjige iz HTML sadržaja."""
    soup = BeautifulSoup(html_content, 'html.parser')
    books = []
    
    book_elements = soup.select('.product_pod')
    
    for book in book_elements:
        try:
            # Naslov
            title_elem = book.select_one('h3 a')
            title = title_elem['title'] if title_elem and 'title' in title_elem.attrs else 'Unknown'
            
            # Cena
            price_elem = book.select_one('.price_color')
            price_text = price_elem.text if price_elem else '£0.00'
            price = parse_price(price_text)
            
            # Rejting
            rating_elem = book.select_one('p.star-rating')
            if rating_elem and 'class' in rating_elem.attrs:
                classes = rating_elem['class']
                rating_class = [c for c in classes if c != 'star-rating']
                rating_text = rating_class[0] if rating_class else 'Zero'
            else:
                rating_text = 'Zero'
            
            rating = parse_rating(rating_text)
            
            # Dostupnost
            availability_elem = book.select_one('.availability')
            availability = availability_elem.text.strip() if availability_elem else 'Unknown'
            
            # URL
            book_url = None
            if title_elem and 'href' in title_elem.attrs:
                book_url = title_elem['href']
                if book_url.startswith('../'):
                    book_url = 'https://books.toscrape.com/catalogue/' + book_url[3:]
            
            books.append({
                'title': title,
                'price': price,
                'price_text': price_text,
                'rating': rating,
                'rating_text': rating_text,
                'availability': availability,
                'url': book_url
            })
            
        except Exception as e:
            logger.warning(f"Greska pri parsiranju knjige: {e}")
            continue
    
    return books

# ============================================================================
# GLAVNA FUNKCIJA
# ============================================================================

def scrape_books():
    parser = argparse.ArgumentParser(description='Advanced Book Scraper')
    parser.add_argument('--url', required=True, help='URL to scrape')
    parser.add_argument('--pages', type=int, default=1, help='Number of pages to scrape')
    parser.add_argument('--output', choices=['csv', 'json', 'both'], default='csv', 
                       help='Output format')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    parser.add_argument('--delay', type=float, default=2.0, help='Delay between pages')
    
    args = parser.parse_args()
    
    scraper = None
    try:
        # ✅ KORISTI SIMPLE ASCII ZNAKOVBE ZA WINDOWS
        logger.info("=" * 60)
        logger.info("POCETAK SKREJPOVANJA")
        logger.info("=" * 60)
        logger.info(f"URL: {args.url}")
        logger.info(f"Broj stranica: {args.pages}")
        logger.info(f"Headless mode: {args.headless}")
        logger.info(f"Output format: {args.output}")
        
        # 1. Inicijalizuj scraper
        logger.info("Inicijalizacija SeleniumScraper...")
        scraper = SeleniumScraper(headless=args.headless)
        
        # 2. Inicijalizuj bazu
        logger.info("Inicijalizacija baze podataka...")
        db = DatabaseHandler()
        logger.info("Baza podataka spremna")
        
        # 3. Skrejpuj stranice
        all_books = []
        
        for page_num in range(1, args.pages + 1):
            logger.info(f"[{page_num}/{args.pages}] Skrejpujem stranicu...")
            
            # Formiraj URL za stranicu
            if page_num == 1:
                page_url = args.url
            else:
                page_url = f"{args.url.rstrip('/')}/catalogue/page-{page_num}.html"
            
            logger.debug(f"URL: {page_url}")
            
            # Koristi scrape_page metod
            books = scraper.scrape_books(page_url)
            # Ekstraktuj knjige
            ###########################books = extract_books_from_html(html)
            all_books.extend(books)
            
            logger.info(f"Stranica {page_num}: pronadjeno {len(books)} knjiga")
            
            # Pauza između stranica
            if page_num < args.pages:
                logger.debug(f"Pauza {args.delay}s pre sledece stranice...")
                time.sleep(args.delay)
        
        # 4. Rezultati
        logger.info("=" * 50)
        logger.info(f"UKUPNO PRONADJENO KNJIGA: {len(all_books)}")
        
        if not all_books:
            logger.warning("Nije pronadjena ni jedna knjiga!")
            return
        
        # 5. Sačuvaj u bazu
        saved_count = db.save_books(books)
        
        total_in_db = len(db.get_all_books())
        logger.info(f"Sačuvano {saved_count} novih knjiga, ukupno u bazi: {total_in_db} knjiga")
        
        # 6. Eksportuj u fajlove
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        # Kreiraj data/exports folder ako ne postoji
        exports_dir = os.path.join('data', 'exports')
        os.makedirs(exports_dir, exist_ok=True)
        
        success = True
        
        if args.output in ['csv', 'both']:
            csv_file = os.path.join(exports_dir, f'books_{timestamp}.csv')
            if db.export_to_csv(csv_file):
                logger.info(f"CSV eksportovan: {csv_file}")
            else:
                logger.error("Greska pri CSV eksportu")
                success = False
        
        if args.output in ['json', 'both']:
            json_file = os.path.join(exports_dir, f'books_{timestamp}.json')
            if db.export_to_json(json_file):
                logger.info(f"JSON eksportovan: {json_file}")
            else:
                logger.error("Greska pri JSON eksportu")
                success = False
        
        # 7. Prikaži statistiku
        if all_books:
            logger.info("-" * 50)
            logger.info("STATISTIKA:")
            
            avg_price = sum(b['price'] for b in all_books) / len(all_books)
            logger.info(f"  Prosecna cena: £{avg_price:.2f}")
            
            # Broj knjiga po rejtingu
            rating_counts = {}
            for book in all_books:
                rating = book['rating']
                rating_counts[rating] = rating_counts.get(rating, 0) + 1
            
            for rating in sorted(rating_counts.keys()):
                count = rating_counts[rating]
                stars = "★" * rating + "☆" * (5 - rating)
                logger.info(f"  Rejting {rating} ({stars}): {count} knjiga")
        
        logger.info("=" * 50)
        if success:
            logger.info("SKREJPOVANJE USPESNO ZAVRSENO!")
        else:
            logger.warning("Skrejpovanje zavrseno sa greskama")
        
    except Exception as e:
        logger.error(f"KRITICNA GRESKA: {e}", exc_info=True)
        raise
        
    finally:
        # Uvek zatvori scraper
        if scraper:
            logger.info("Zatvaram Selenium driver...")
            scraper.close()

# ============================================================================
# POKRETAČ
# ============================================================================

if __name__ == "__main__":
    # Kreiraj potrebne foldere
    for folder in ['data/exports', 'logs']:
        os.makedirs(folder, exist_ok=True)
    
    scrape_books()