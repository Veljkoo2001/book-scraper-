# ============================================
# PRVI SKREJPER - Pravi HTTP zahtev
# ============================================

import requests 
print ("Saljem prvi HTTP zahtev...")
print("=" *50)

url = "http://books.toscrape.com/"

try: 
    print(f"Povezujem se na: {url}")
    response = requests.get(url)

    print(f"Staus kod: {response.status_code}")

    if response.status_code == 200:
        print("Zahtev je uspesan!")

        print(f"Duzina HTML-a: {len(response.text)} karaktera.")
        print(f"Prvih 200 karaktera: ")
        print("-" *40)
        print(response.text[:200])
        print("-" *40)

        with open ('prva_stranica.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("HTML je sacuvan u 'prva_stranica.html'")

    else:
        print(f"Greska! Status {response.status_code}")
except Exception as e:
    print(f"Doslo je do greske: {e}")
    print("Pronevri internet konekciju.")

print("=" *50)
print("Prvi HTML zahtev je zavrsen!")