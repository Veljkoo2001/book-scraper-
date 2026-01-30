import sqlite3
import os

db_path = 'database/books.db'
print(f'Proveravam: {db_path}')
print(f'Fajl postoji: {os.path.exists(db_path)}')

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Proveri tabele
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f'Tabele u bazi: {tables}')
    
    # Proveri books tabelu
    if ('books',) in tables:
        cursor.execute('SELECT COUNT(*) FROM books')
        count = cursor.fetchone()[0]
        print(f'Broj knjiga: {count}')
        
        if count > 0:
            cursor.execute('SELECT title, price, rating FROM books LIMIT 3')
            books = cursor.fetchall()
            print('Prve 3 knjige:')
            for book in books:
                print(f'  - {book}')
    else:
        print('❌ Nema books tabele!')
    
    conn.close()
else:
    print('❌ Baza ne postoji!')