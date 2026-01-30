import logging
from scrapers.selenium_scraper import SeleniumScraper
from database.db_handler import DatabaseHandler
from utils.logger import logger

def scrape_books():
    """Glavna funkcija za skrejpovanje knjiga."""
    db = DatabaseHandler()
    scraper = SeleniumScraper(headless=True)
    
    url = "https://books.toscrape.com/"
    logger.info(f"Početak skrejpovanja: {url}")
    
    html = scraper.scrape_page(url, wait_for_element=".product_pod")
    
    if not html:
        logger.error("Nije dobijen HTML, prekidam.")
        return
    
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    
    books = soup.select(".product_pod")
    logger.info(f"Pronađeno {len(books)} knjiga.")
    
    for book in books:
        try:
            # Ekstraktuj podatke
            title = book.h3.a["title"]
            
            # Cena
            price_element = book.select_one(".price_color")
            price = price_element.text if price_element else "0"
            price_value = float(price.replace('£', '').replace('Â', '').strip())
            
            # Ocena
            rating_element = book.select_one("p.star-rating")
            rating = rating_element["class"][1] if rating_element else "Zero"
            
            # Dostupnost
            availability_element = book.select_one(".availability")
            availability = availability_element.text.strip() if availability_element else "Unknown"
            
            # URL
            book_url = f"http://books.toscrape.com/catalogue/{book.h3.a['href']}"
            
            # Ubaci u bazu sa postojećim kolonama
            db.insert_book(
                title=title,
                author="Nepoznat autor",  # Ovo će biti None ako kolona ne postoji
                price=price_value,
                url=book_url,
                currency="£",
                rating=rating,
                availability=availability,
                category="General",
                page_number=1
            )
            
            logger.debug(f"Dodata knjiga: {title[:50]}...")
            
        except Exception as e:
            logger.warning(f"Greška pri parsiranju knjige: {e}", exc_info=True)
    
    scraper.close_driver()
    
    # Proveri koliko je knjiga dodato
    all_books = db.get_all_books()
    logger.info(f"Skrejpovanje završeno. Ukupno knjiga u bazi: {len(all_books)}")

if __name__ == "__main__":
    try:
        scrape_books()
    except Exception as e:
        logger.error(f"Kritična greška u main.py: {e}", exc_info=True)