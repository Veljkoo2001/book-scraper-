# ============================================
# PARSIRANJE HTML-a sa BeautifulSoup
# ============================================

import requests 
from bs4 import BeautifulSoup

print("Pocinje parsiranje HTML-a...")
print ("=" *50)

url = "http://books.toscrape.com/"

response = requests.get(url)
html_content = response.text

soup = BeautifulSoup(html_content, 'html.parser')

print(" - Osnovne informacije -")
print(f"    Naslov stranice: {soup.title.text}")
print(f"    Broj paragrafa: {len(soup.find_all('p'))}")
print(f"    Broj linkova: {len(soup.find_all('a'))}")
print(f"    Broj slika: {len(soup.find_all('img'))}")

print("\n Prvih 5 linkova:")
links = soup.find_all('a')[:5] #links - niz od 5 clanova (linkova)
for i, link in enumerate(links, 1):
    href = link.get('href', 'N/A')
    text = link.text.strip()[:30]
    print(f"    {i}. {text}... -> {href}")

books = soup.find_all('article', class_='product_pod')

if books: 
    print(f"Pronadjeno {len(books)} knjiga!")

    print ("\n Inforamacije o prve 3 knjige.")
    for i, book in enumerate(books[:3],1):
        title_tag = book.find('h3').find('a') #trazimo u h3 jer se obicno on koristi za naslove knjiga/artiakla
        title = title_tag.get('title', 'Nema naslova')

        price_tag = book.find('p', class_='price_color')
        price = price_tag.text if price_tag else print("Nema cene")

        print (f"\n {i}. {title}")
        print (f"        Cena: {price}")

        availbility = book.find('p', class_='instock availability')
        if availbility:
            print(f"        {availbility.text.strip()}")
else:
    print("Nije pronadjena knjiga. Doslo je do greske!")

print("=" *50)
print("Parsiranje zavrseno!")

categories = soup.find('ul', class_='nav nav-list').find('ul').find_all('a')
print ("Kategorije knjiga: ")
for c in categories:
    print(f"    {c.text.strip()}")


total = 0
count = 0

for book in books: 
    price_tag = book.find('p', class_='price_color')
    if price_tag:
        price_text = price_tag.text.replace('£','').replace('Â','') #brisemo £, odnosno zamen. za prazan string
                                                                    #iz nekog razloga sam morao da dodam Â ?????            
        try:
            price = float(price_text.strip())
            total += price
            count +=1
        except ValueError as e:
            print(f"Nemoguce konvertovati '{price_text}' u broj.") 
            continue
    else:
        print("Knjiga nema cenu.")

if count > 0:
    average = total / count
    print(f"    Prosecna cena: £{average:.2f}")
    print(f"    Ukupno obradjeno knjiga: {count}")

