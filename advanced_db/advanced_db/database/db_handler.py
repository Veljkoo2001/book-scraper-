import sqlite3
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseHandler:
    def __init__(self, db_path="database/books.db"):
        # Kreiraj apsolutnu putanju
        self.db_path = os.path.abspath(db_path)
        self._ensure_db_dir()
        self.init_db()

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

    def insert_book(self, title, author=None, price=None, url=None, **kwargs):
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