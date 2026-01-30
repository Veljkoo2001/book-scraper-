# test_insert.py
from database.db_handler import DatabaseHandler
import logging

logging.basicConfig(level=logging.DEBUG)

print("=== TEST insert_book ===")

db = DatabaseHandler()

# Test 1: Jednostavna knjiga
print("\n1. Test sa jednostavnom knjigom:")
result1 = db.insert_book(
    title="TEST KNJIGA 1 - UNIKATNI NASLOV",
    price=29.99,
    rating=4,
    availability="In stock",
    url="http://test-unique-url-1.com"
)
print(f"   Rezultat: {result1}")

# Test 2: Knjiga bez URL (možda problem sa UNIQUE)
print("\n2. Test bez URL-a:")
result2 = db.insert_book(
    title="TEST KNJIGA 2 - BEZ URL",
    price=19.99,
    rating=3,
    availability="Out of stock"
    # Bez URL parametra!
)
print(f"   Rezultat: {result2}")

# Test 3: Proveri šta je u bazi
print("\n3. Provera baze:")
books = db.get_all_books()
print(f"   Ukupno knjiga u bazi: {len(books)}")
for i, book in enumerate(books[:3]):
    print(f"   {i+1}. {book['title'][:40]}...")