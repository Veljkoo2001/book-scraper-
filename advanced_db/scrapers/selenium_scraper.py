# scrapers/selenium_scraper.py - KOMPLETAN KOD

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException
import logging
import os
import time

logger = logging.getLogger(__name__)

class SeleniumScraper:
    def __init__(self, headless=True):
        self.headless = headless
        self.driver = None
        self.options = webdriver.ChromeOptions()
        self._setup_driver()

        if headless:
            self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
    
    def _setup_driver(self):
        """Podešava Chrome driver za Docker ili lokalno."""
        chrome_options = Options()
        
        # Dodaj opcije
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        if self.headless:
            chrome_options.add_argument('--headless')
        
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        
        # Proveri da li smo u Docker kontejneru
        in_docker = os.path.exists('/.dockerenv')
        
        try:
            if in_docker:
                # U Dockeru - Chrome je već instaliran
                chrome_options.binary_location = '/usr/bin/google-chrome-stable'
                self.driver = webdriver.Chrome(
                    options=chrome_options,
                    service=Service('/usr/local/bin/chromedriver')
                )
            else:
                # Lokalno - koristi system Chrome
                self.driver = webdriver.Chrome(options=chrome_options)
            
            logger.info("Selenium driver uspešno pokrenut")
            
        except WebDriverException as e:
            logger.error(f"Greška pri pokretanju ChromeDriver: {e}")
            logger.info("Pokušavam sa fallback opcijama...")
            
            # Fallback: pokušaj sa remote driver
            try:
                from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
                from selenium.webdriver.remote.command import Command
                
                self.driver = RemoteWebDriver(
                    command_executor='http://localhost:4444/wd/hub',
                    options=chrome_options
                )
                logger.info("Koristim remote WebDriver")
            except:
                raise Exception("Nije moguće pokrenuti WebDriver. Proverite Chrome/ChromeDriver instalaciju.")
    
    def scrape_page(self, url, wait_for=None):
        """
        Skrejpuje HTML sajta
        
        Args:
            url (str): URL za skrejpovanje
            wait_for (str): CSS selector za čekanje (opciono)
            
        Returns:
            str: HTML sadržaj stranice
        """
        try:
            logger.info(f"Učitavam stranicu: {url}")
            self.driver.get(url)
            
            if wait_for:
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, wait_for))
                    )
                    logger.info(f"Element {wait_for} pronađen")
                except TimeoutException:
                    logger.warning(f"Element {wait_for} nije pronađen, nastavljam...")
            
            time.sleep(2)
            html = self.driver.page_source
            logger.info(f"Stranica učitana, veličina HTML-a: {len(html)} karaktera")
            return html
            
        except Exception as e:
            logger.error(f"Greška pri skrejpovanju stranice {url}: {e}")
            raise
    
    def scrape_books(self, url, max_pages=1):
        """
        Skrejpuje knjige sa books.toscrape.com
        
        Args:
            url (str): Osnovni URL
            max_pages (int): Broj stranica za skrejpovanje
            
        Returns:
            list: Lista knjiga (dict)
        """
        books = []
        
        try:
            for page in range(1, max_pages + 1):
                if page == 1:
                    page_url = url
                else:
                    page_url = f"{url}/catalogue/page-{page}.html"
                
                logger.info(f"Skrejpujem stranicu {page}/{max_pages}: {page_url}")
                self.driver.get(page_url)
                time.sleep(2)
                
                book_elements = self.driver.find_elements(By.CSS_SELECTOR, "article.product_pod")
                
                for book in book_elements:
                    try:
                        book_data = self._extract_book_data(book)
                        if book_data:
                            books.append(book_data)
                    except Exception as e:
                        logger.warning(f"Greška pri ekstrakciji knjige: {e}")
                        continue
                
                logger.info(f"Pronađeno {len(book_elements)} knjiga na stranici {page}")
                
        except Exception as e:
            logger.error(f"Greška pri skrejpovanju knjiga: {e}")
        
        return books
    
    # ZAMENI OVAJ DEO U scrapers/selenium_scraper.py:

    def _extract_book_data(self, book_element):
        """
        Ekstrahuje podatke o knjizi
        
        Args:
            book_element: Selenium WebElement
            
        Returns:
            dict: Podaci o knjizi
        """
        try:
            title_elem = book_element.find_element(By.CSS_SELECTOR, "h3 a")
            title = title_elem.get_attribute("title")
            
            price_elem = book_element.find_element(By.CSS_SELECTOR, "p.price_color")
            price_text = price_elem.text
            price = float(price_text.replace('£', ''))
            
            rating_elem = book_element.find_element(By.CSS_SELECTOR, "p.star-rating")
            rating_classes = rating_elem.get_attribute("class").split()
            
            rating_map = {
                "One": 1, "Two": 2, "Three": 3, 
                "Four": 4, "Five": 5
            }
            
            rating = 0
            for cls in rating_classes:
                if cls in rating_map:
                    rating = rating_map[cls]
                    break
            
            # ⚠️ OVO JE PROBLEM! Promeni selector! ⚠️
            # STARI: availability_elem = book_element.find_element(By.CSS_SELECTOR, "p.availability")
            # NOVI:
            try:
                # Prvo probaj sa instock.availability
                availability_elem = book_element.find_element(By.CSS_SELECTOR, "p.instock.availability")
                availability = availability_elem.text.strip()

                # Čisti tekst - ukloni višak
                if "In stock" in availability:
                    availability = "In stock"
                elif "Out of stock" in availability:
                    availability = "Out of stock"
                elif availability == "":
                    availability = "In stock"  # default
            except Exception as e:
                # Fallback
                try:
                    availability_elem = book_element.find_element(By.CSS_SELECTOR, "p.availability")
                    availability = availability_elem.text.strip()
                except:
                    availability = "Check availability"
            
            availability = availability_elem.text.strip()
            
            return {
                "title": title,
                "price": price,
                "rating": rating,
                "availability": availability,
                "url": title_elem.get_attribute("href")
            }
            
        except Exception as e:
            logger.warning(f"Greška pri ekstrakciji podataka knjige: {e}")
            return None
    
    def close(self):
        """Zatvori Selenium driver"""
        if self.driver:
            self.driver.quit()
            logger.info("Selenium driver zatvoren")