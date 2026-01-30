import sqlite3
import logging
import os
import csv
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseHandler:
    def __init__(self, db_path="database/books.db"):
        # Kreiraj apsolutnu putanju
        self.db_path = os.path.abspath(db_path)
        self._ensure_db_dir()
        self.init_db()
        self._add_missing_columns()  # ← DODAJ OVO!

    def _ensure_db_dir(self):
        """Osigurava da folder za bazu postoji."""
        db_dir = os.path.dirname(self.db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            logger.info(f"Kreiran folder: {db_dir}")

    def init_db(self):
        """Kreira tabelu ako ne postoji."""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT,
            price REAL,
            url TEXT UNIQUE,
            rating INTEGER DEFAULT 0,          # ← DODAJ OVO!
            availability TEXT DEFAULT 'Unknown', # ← DODAJ OVO!
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(create_table_sql)
            conn.commit()
            conn.close()
            logger.info(f"Tabela 'books' je spremna u: {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Greška pri kreiranju tabele: {e}")

    def insert_book(self, title, author=None, price=None, url=None, rating=None, availablity=None, **kwargs):
        """Ubacuje knjigu u bazu sa fleksibilnim unosom."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Proveri koje kolone postoje
            cursor.execute("PRAGMA table_info(books)")
            columns_info = cursor.fetchall()
            existing_columns = {col[1]: col[2] for col in columns_info}
            
            # Pripremi podatke za unos
            columns = []
            values = []
            
            if 'title' in existing_columns:
                columns.append('title')
                values.append(title)
            
            if 'author' in existing_columns and author:
                columns.append('author')
                values.append(author)
            elif 'author' in existing_columns:
                columns.append('author')
                values.append(None)
            
            if 'price' in existing_columns and price is not None:
                columns.append('price')
                values.append(float(price))
            elif 'price' in existing_columns:
                columns.append('price')
                values.append(None)
            
            if 'url' in existing_columns and url:
                columns.append('url')
                values.append(url)
            elif 'url' in existing_columns:
                columns.append('url')
                values.append(None)
            
            if 'rating' in existing_columns:
                columns.append('rating')
                try:
                    values.append(int(rating) if rating is not None else 0)
                except:
                    values.append(0)
            
            if 'availability' in existing_columns:
                columns.append('availability')
                values.append(availablity if availablity else 'Unknown')
                
            # Dodaj dodatne kolone iz kwargs
            for key, value in kwargs.items():
                if key in existing_columns:
                    columns.append(key)
                    values.append(value)
            
            # Kreiraj SQL za unos
            if columns:
                placeholders = ', '.join(['?'] * len(values))
                column_names = ', '.join(columns)
                
                insert_sql = f"INSERT OR IGNORE INTO books ({column_names}) VALUES ({placeholders})"
                
                cursor.execute(insert_sql, values)
                conn.commit()
                inserted = cursor.rowcount
            else:
                inserted = 0
            
            conn.close()
            
            if inserted > 0:
                logger.debug(f"Dodata knjiga: {title[:50]}...")
            return inserted
            
        except sqlite3.Error as e:
            logger.error(f"Greška pri unosu knjige: {e}")
            return 0
    def get_all_books(self):
        """Vraća sve knjige iz baze."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM books")
            results = cursor.fetchall()
            conn.close()
            return results
        except sqlite3.Error as e:
            logger.error(f"Greška pri čitanju iz baze: {e}")
            return []
    def recreate_table(self):
        """Kreira novu tabelu sa ispravnom shemom (BRiŠE POSTOJEĆE PODATKE!)."""
        confirm = input("Ovo će obrisati sve postojeće podatke! Da li ste sigurni? (da/ne): ")
        if confirm.lower() != 'da':
            print("Prekinuto.")
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Obriši staru tabelu
            cursor.execute("DROP TABLE IF EXISTS books")
            
            # Kreiraj novu tabelu
            create_table_sql = """
            CREATE TABLE books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT,
                price REAL,
                url TEXT UNIQUE,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            cursor.execute(create_table_sql)
            conn.commit()
            conn.close()
            
            logger.info("Tabela 'books' je kreirana ispravno.")
            print("Tabela je uspešno kreirana!")
            
        except sqlite3.Error as e:
            logger.error(f"Greška pri kreiranju tabele: {e}")
    def save_books(self, books):
        """
        Save multiple books to database (kompatibilno sa main.py)
        
        Args:
            books (list): Lista knjiga (dict)
            
        Returns:
            int: Broj uspešno sačuvanih knjiga
        """
        saved_count = 0
        for book in books:
            # Koristi postojeći insert_book metod
            inserted = self.insert_book(
                title=book.get('title'),
                price=book.get('price'),
                author=book.get('author', ''),
                url=book.get('url', ''),
                rating=book.get('rating'),
                availability=book.get('availability')
            )
            if inserted > 0:
                saved_count += 1
        
        logger.info(f"Sačuvano {saved_count} knjiga u bazu")
        return saved_count
    
    def export_to_csv(self, filename="books_export.csv"):
        """
        Eksportuj sve knjige u CSV fajl
        
        Args:
            filename (str): Ime CSV fajla
            
        Returns:
            bool: True ako je uspešno, False ako nije
        """
        try:
            # Dobavi sve knjige
            books = self.get_all_books()
            
            if not books:
                logger.warning("Nema knjiga za eksport")
                return False
            
            # Konvertuj sqlite3.Row u dict (ako je potrebno)
            if isinstance(books[0], sqlite3.Row):
                books = [dict(book) for book in books]
            
            # Pripremi fieldnames (sve ključeve iz prvog rečnika)
            fieldnames = []
            if books:
                fieldnames = list(books[0].keys())
            
            # Napiši CSV
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(books)
            
            logger.info(f"Eksportovano {len(books)} knjiga u {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Greška pri CSV eksportu: {e}")
            return False
    
    def export_to_json(self, filename="books_export.json"):
        """
        Eksportuj sve knjige u JSON fajl
        
        Args:
            filename (str): Ime JSON fajla
            
        Returns:
            bool: True ako je uspešno, False ako nije
        """
        try:
            # Dobavi sve knjige
            books = self.get_all_books()
            
            if not books:
                logger.warning("Nema knjiga za eksport")
                return False
            
            # Konvertuj sqlite3.Row u dict
            if isinstance(books[0], sqlite3.Row):
                books = [dict(book) for book in books]
            
            # Funkcija za serijalizaciju datetime objekata
            def default_serializer(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                raise TypeError(f"Tip {type(obj)} nije serijalizabilan")
            
            # Napiši JSON
            with open(filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(books, jsonfile, indent=2, default=default_serializer)
            
            logger.info(f"Eksportovano {len(books)} knjiga u {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Greška pri JSON eksportu: {e}")
            return False
    
    def get_stats(self):
        """
        Vrati statistiku baze podataka
        
        Returns:
            dict: Statistika baze
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            stats = {}
            
            # Ukupno knjiga
            cursor.execute("SELECT COUNT(*) FROM books")
            stats['total_books'] = cursor.fetchone()[0]
            
            # Prosečna cena
            cursor.execute("SELECT AVG(price) FROM books WHERE price IS NOT NULL")
            avg_result = cursor.fetchone()[0]
            stats['avg_price'] = float(avg_result) if avg_result else 0.0
            
            # Minimum i maksimum cena
            cursor.execute("SELECT MIN(price), MAX(price) FROM books")
            min_max = cursor.fetchone()
            stats['min_price'] = float(min_max[0]) if min_max[0] else 0.0
            stats['max_price'] = float(min_max[1]) if min_max[1] else 0.0
            
            # Broj knjiga po dostupnosti
            cursor.execute("""
                SELECT availability, COUNT(*) 
                FROM books 
                WHERE availability IS NOT NULL 
                GROUP BY availability
            """)
            stats['by_availability'] = dict(cursor.fetchall())
            
            conn.close()
            
            logger.info(f"Statistika: {stats['total_books']} knjiga, avg cena: {stats['avg_price']:.2f}")
            return stats
            
        except sqlite3.Error as e:
            logger.error(f"Greška pri dobavljanju statistike: {e}")
            return {}
    
    def _add_missing_columns(self):
        """Dodaj nedostajuće kolone (rating, availability) ako treba."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Proveri koje kolone postoje
            cursor.execute("PRAGMA table_info(books)")
            existing_columns = [col[1] for col in cursor.fetchall()]
            
            # Dodaj rating ako ne postoji
            if 'rating' not in existing_columns:
                cursor.execute("ALTER TABLE books ADD COLUMN rating INTEGER DEFAULT 0")
                print("➕ Added 'rating' column")
            
            # Dodaj availability ako ne postoji
            if 'availability' not in existing_columns:
                cursor.execute("ALTER TABLE books ADD COLUMN availability TEXT DEFAULT 'Unknown'")
                print("➕ Added 'availability' column")
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"⚠️ Could not add columns: {e}")