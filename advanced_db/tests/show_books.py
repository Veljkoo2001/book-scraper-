from database.db_handler import DatabaseHandler

db = DatabaseHandler()
books = db.get_all_books()

print("📚 SKREJPOVANE KNJIGE 📚")
print("=" * 50)

for i, book in enumerate(books, 1):
    # Konvertuj u dict ako treba
    if hasattr(book, 'keys'):
        book = dict(book)
    
    print(f"\n{i}. {book.get('title', 'Bez naslova')}")
    
    price = book.get('price')
    if price:
        print(f"   💰 Cena: £{price}")
    
    author = book.get('author')
    if author:
        print(f"   ✍️  Autor: {author}")
    
    url = book.get('url')
    if url:
        print(f"   🔗 URL: {url[:50]}...")

print(f"\n{'='*50}")
print(f"🎉 UKUPNO: {len(books)} knjiga u bazi!")