# scrapers/selenium_scraper.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException
import logging
import os

logger = logging.getLogger(__name__)

class SeleniumScraper:
    def __init__(self, headless=True):
        self.headless = headless
        self.driver = None
        self._setup_driver()
    
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