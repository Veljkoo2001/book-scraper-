import sys
import os

# Dodaj parent folder u Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_handler import DatabaseHandler

print("Testiranje baze podataka...")
print(f"Radni direktorijum: {os.getcwd()}")

db = DatabaseHandler()
print(f"Putanja do baze: {db.db_path}")

# Test ubacivanja
result = db.insert_book(
    title="Test knjiga",
    author="Test autor", 
    price=29.99,
    url="http://example.com/test1"
)
print(f"Rezultat ubacivanja: {result} redova dodato")

# Pročitaj sve
books = db.get_all_books()
print(f"Ukupno knjiga u bazi: {len(books)}")
for book in books:
    print(f"  - {book['title']}")