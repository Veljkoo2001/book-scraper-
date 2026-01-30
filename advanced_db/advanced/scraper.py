import requests 
from bs4 import BeautifulSoup
import os
import csv
import json
import pandas as pd
from config import BASE_URL, MAX_PAGES, DELAY_SECONDS, OUTPUT_FOLDER
from utils import setup_logger, random_delay, clean_price, print_progress
from datetime import datetime

logger = setup_logger()

class BookScraper:
    def __init__(self):
        self.base_url = BASE_URL
        self.all_books = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def get_page_url(self, page_num):
        #Generise url za odredjene stranice
        if page_num == 1:
            return f"{self.base_url}index.html"
        else:
            return f"{self.base_url}catalogue/page-{page_num}.html"
        
    def scrape_single_page(self, page_num):
        #Skrejpuje jednu stranicu
        url = self.get_page_url(page_num)
        logger.info(f"Skrejpuje stranicu {page_num}: {url}")


        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status() #za proveru http gresaka

            soup = BeautifulSoup(response.text, 'html.parser')
            books = soup.find_all('article', class_='product_pod')

            page_books = []
            for book in books:
                book_data = self.extract_book_data(book, page_num)
                if book_data:
                    page_books.append(book_data)

            logger.info(f"Stranica {page_num}: pronadjeno {len(page_books)} knjiga")
            return page_books
        
        except Exception as e:
            logger.error(f"Greska na stranici {page_num}: {e}")
            return[]
        
    def extract_book_data(self, book_element, page_num):
        #Izvaja podatke o knjizi
        try:
            #Naslov
            title_tag = book_element.find('h3').find('a')
            title = title_tag.get('title', '').strip()

            #Cena
            price_tag = book_element.find('p', class_='price_color')
            price_text = price_tag.text if price_tag else ''
            price = clean_price(price_text)

            #Dostupnost
            stock_tag = book_element.find('p', class_="instock availability")
            in_stock = stock_tag.text.strip() if stock_tag else 'N/A'

            #Ocena 
            rating_tag = book_element.find('p', class_='star-rating')
            rating = rating_tag.get('class')[1] if rating_tag else 'N/A'

            #Link
            book_url = title_tag.get('href','')
            full_url = f"{self.base_url}catalogue/{book_url}"

            return{
                'title': title,
                'price': price,
                'currency': '£',
                'in_stock': in_stock,
                'rating': rating,
                'url': full_url,
                'page': page_num,
                'scraped_at': datetime.now().isoformat()
            }

        except Exception as e:
            logger.warning(f"Greska pri ekstrakciji knjige: {e}")
            return None


    def scrape_all_pages(self, max_pages=MAX_PAGES):
        #Skrejpuje sve stranice
        logger.info(f"Pocinje skrejpanje {max_pages} stranica.")
        all_books = []

        for page_num in range(1, max_pages+1):
            print_progress(page_num, max_pages, "Skrejpanje stranica")

            page_books = self.scrape_single_page(page_num)
            all_books.extend(page_books)

            if page_num < max_pages:
                delay = random_delay(1, 3)
                logger.debug(f"Pauza: {delay: .1f} sekundi")

        logger.info(f"Zavrseno! Ukupno knjiga: {len(all_books)}")
        self.all_books = all_books
        return all_books    

    def show_statistics(self):
        """Prikazuje statistike skrejpovanih podataka"""
        if not self.all_books:
            print('Nema podatak za statistiku.')
            return
        
        total_books = len(self.all_books)
        total_price = sum(book['price'] for book in self.all_books)
        avg_price = total_price / total_books if total_books > 0 else 0

        #Najskuplja i najjeftinija knjiga
        most_expensive = max(self.all_books, key=lambda x: x['price'])
        cheapest = min(self.all_books, key=lambda x: x['price'])

        print("\n" + "="*50)
        print("-- STATISTIKa --")
        print("="*50)
        print(f"Ukupno knjiga: {total_books}")
        print(f"Prosečna cena: £{avg_price:.2f}")
        print(f"Ukupna vrednost: £{total_price:.2f}")
        print(f"\n Najskuplja knjiga:")
        print(f"   {most_expensive['title'][:50]}...")
        print(f"   Cena: £{most_expensive['price']}")
        print(f"\n Najjeftinija knjiga:")
        print(f"   {cheapest['title'][:50]}...")
        print(f"   Cena: £{cheapest['price']}")
        print("="*50)

class DataSaver:
    @staticmethod
    def save_to_csv(books, filename="books.csv"):
        """Cuva podatke u CSV formatu"""
        if not books:
            logger.warning("Nema podatak za cuvanje.")
            return
        
        #Kreiramo folder ako ne postoji
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)

        filepath = os.path.join(OUTPUT_FOLDER, filename)

        #Kolone
        fieldnames = ['title', 'price', 'currency', 'in_stock', 'rating', 'url', 'page', 'scraped_at']

        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(books)


        logger.info(f"Podaci sacuvani u CSV: {filepath}")
        return filepath
    
    @staticmethod
    def save_to_json(books, filename="books.json"):
        "Cuva podatke u JSON formatu"
        if not books: 
            logger.warning("Nema podataka za cuvanje.")
            return

        os.makedirs(OUTPUT_FOLDER, exist_ok=True)
        filepath = os.path.join(OUTPUT_FOLDER, filename) 

        with open(filepath, 'w', encoding='utf-8') as jsonfile:
            json.dump(books, jsonfile, indent=2, ensure_ascii=False)
        

        logger.info("Podaci sacuvani u JSON: {filepath}")
        return filepath
    
    @staticmethod
    def save_to_excel(books, filename="books.xlsx"):
        "Cuva podatke u Excelu"
        try:
            os.makedirs(OUTPUT_FOLDER, exist_ok=True)
            filepath = os.path.join(OUTPUT_FOLDER, filename)

            df = pd.DataFrame(books)
            df.to_excel(filepath, index=False)

            logger.info("Podaci sacuvani: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Greska pri cuvanju: {e}")
            return None
        
    @staticmethod
    def save_all_formats(books):
        "Cuva podatke u sve 3 forme"
        if not books:
            print("Nema podataka za cuvanje!")
            return {'csv': None, 'json': None, 'excel': None}  # Vrati prazan recnik

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        files = {
            'csv': DataSaver.save_to_csv(books, f"books_{timestamp}.csv"),
            'json': DataSaver.save_to_json(books, f"books_{timestamp}.json"),
            'excel': DataSaver.save_to_excel(books, f"books_{timestamp}.xlsx")
        }

        return files


if __name__ == "__main__":
    print(" Testiram paginaciju...")
    
    scraper = BookScraper()
    
    print("\nSkrejpovanje knjige: ")
    all_books = scraper.scrape_all_pages(max_pages=3)

    scraper.show_statistics()

    print("\n Prvih 5 knjiga: ")
    for i, book in enumerate(all_books[:5], 1):
        print(f"{i}. {book['title'][:40]} ... - £{book['price']} - Strana {book['page']}")
   
    print("\nCuvam podatke...")
    
    saved_files = DataSaver.save_all_formats(all_books)
    
    print("\n ZAVRSENO! \nSvi fajlovi su sacuvani.")
    

    for format_name, filepath in saved_files.items():
        if filepath:
            print(f"  • {format_name.upper()}: {filepath}")
    
    
    print("\n Svi zadaci završeni! Možeš otvoriti CSV fajl u Excel-u.")

