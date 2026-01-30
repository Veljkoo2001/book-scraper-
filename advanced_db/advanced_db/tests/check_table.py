import sqlite3
import os

db_path = "database/books.db"
print(f"Provjera baze: {db_path}")

if not os.path.exists(db_path):
    print("Baza ne postoji!")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Proveri kolone u tabeli books
    cursor.execute("PRAGMA table_info(books)")
    columns = cursor.fetchall()
    
    print("\n=== TRENUTNE KOLONE ===")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    # Proveri podatke
    cursor.execute("SELECT * FROM books")
    rows = cursor.fetchall()
    
    print(f"\n=== PODACI ({len(rows)} redova) ===")
    for row in rows:
        print(f"  {row}")
    
    conn.close()