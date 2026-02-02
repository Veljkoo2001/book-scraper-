# web/app.py - Advanced Book Scraper Dashboard
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sqlite3
import json
import os
import sys
import traceback
from datetime import datetime

# ===================== SETUP PATHS =====================
# Dodaj parent folder u Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# ===================== IMPORT SCRAPER =====================
ScraperClass = None
try:
    # Prvo pokušaj da importuješ ceo modul
    import scrapers.selenium_scraper as scraper_module
    
    # Pronađi sve klase u modulu
    import inspect
    classes_found = []
    for name, obj in inspect.getmembers(scraper_module):
        if inspect.isclass(obj) and obj.__module__ == 'scrapers.selenium_scraper':
            classes_found.append((name, obj))
            print(f"Found class: {name}")
    
    if classes_found:
        # Uzmi prvu klasu (verovatno glavni scraper)
        ScraperClass = classes_found[0][1]
        print(f" Using scraper class: {classes_found[0][0]}")
    else:
        print(" No scraper classes found in scraper.scraper")
        
except ImportError as e:
    print(f" Could not import scraper module: {e}")
    ScraperClass = None
except Exception as e:
    print(f" Error finding scraper class: {e}")
    ScraperClass = None

# ===================== IMPORT DATABASE =====================
try:
    from database.db_handler import DatabaseHandler
    print(" DatabaseManager imported successfully")
except ImportError as e:
    print(f" Could not import DatabaseManager: {e}")
    # Fallback klasa ako baza ne postoji
    class DatabaseManager:
        def __init__(self, db_path):
            self.db_path = db_path
            self.conn = None
            print(f"Mock DB created at: {db_path}")
        
        def save_books(self, books):
            print(f"📚 Mock: Would save {len(books)} books")
            # Zapravo sačuvaj u SQLite
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Kreiraj tabelu ako ne postoji
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS books (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        price REAL,
                        rating INTEGER,
                        availability TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Dodaj knjige
                for book in books:
                    cursor.execute('''
                        INSERT INTO books (title, price, rating, availability)
                        VALUES (?, ?, ?, ?)
                    ''', (
                        book.get('title', 'Unknown'),
                        book.get('price', 0),
                        book.get('rating', 0),
                        book.get('availability', 'Unknown')
                    ))
                
                conn.commit()
                conn.close()
                return True
            except Exception as e:
                print(f"Error saving to DB: {e}")
                return False
        
        def get_all_books(self):
            try:
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM books ORDER BY id DESC")
                books = [dict(row) for row in cursor.fetchall()]
                conn.close()
                return books
            except:
                return []
        
        def export_to_csv(self, path):
            try:
                import csv
                books = self.get_all_books()
                if not books:
                    return False
                
                with open(path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=books[0].keys())
                    writer.writeheader()
                    writer.writerows(books)
                
                return True
            except Exception as e:
                print(f"Export error: {e}")
                return False

# ===================== CREATE FASTAPI APP =====================
app = FastAPI(
    title="Advanced Book Scraper Dashboard",
    description="Real-time web scraping dashboard for books",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="web/static"), name="static")
templates = Jinja2Templates(directory="web/templates")

# Create database instance
db_path = "data/books.db"
os.makedirs(os.path.dirname(db_path), exist_ok=True)
db = DatabaseHandler(db_path)

# ===================== ROUTES =====================

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page with charts and controls"""
    try:
        books = db.get_all_books()
        
        # Calculate statistics
        prices = [float(book.get("price", 0)) for book in books if book.get("price")]
        ratings = [int(book.get("rating", 0)) for book in books if book.get("rating")]
        
        stats = {
            "total_books": len(books),
            "avg_price": round(sum(prices) / len(prices), 2) if prices else 0,
            "avg_rating": round(sum(ratings) / len(ratings), 2) if ratings else 0,
            "books_by_rating": {},
        }
        
        # Group by rating
        for book in books:
            rating = book.get("rating", 0)
            stats["books_by_rating"][rating] = stats["books_by_rating"].get(rating, 0) + 1
        
        return templates.TemplateResponse("index.html", {
            "request": request,
            "books": books[:20],  # Show only first 20
            "stats": stats,
            "total_count": len(books),
            "scraper_available": ScraperClass is not None
        })
    except Exception as e:
        print(f"Dashboard error: {e}")
        return templates.TemplateResponse("index.html", {
            "request": request,
            "books": [],
            "stats": {"total_books": 0, "avg_price": 0, "avg_rating": 0, "books_by_rating": {}},
            "total_count": 0,
            "error": str(e)
        })

@app.get("/api/books", response_class=JSONResponse)
async def get_books(limit: int = 50, offset: int = 0, search: str = None, rating: int = None):
    """API to get books with filtering and pagination"""
    try:
        books = db.get_all_books()
        
        # Apply filters
        if search:
            books = [b for b in books if search.lower() in b.get("title", "").lower()]
        
        if rating is not None:
            books = [b for b in books if b.get("rating", 0) == rating]
        
        # Apply pagination
        total = len(books)
        paginated_books = books[offset:offset + limit]
        
        return {
            "success": True,
            "books": paginated_books,
            "total": total,
            "page": (offset // limit) + 1 if limit > 0 else 1,
            "pages": (total + limit - 1) // limit if limit > 0 else 1
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "books": []
        }

@app.post("/api/scrape", response_class=JSONResponse)
async def scrape_books(url: str = Form(...), pages: int = Form(1)):
    """API endpoint to start scraping"""
    if ScraperClass is None:
        return {
            "success": False,
            "message": "Scraper not available. Check scrapers/selenium_scraper.py"
        }
    
    print(f" Starting scrape: URL={url}, pages={pages}")
    
    try:
        # Create scraper instance
        scraper = ScraperClass(headless=True)
        print(f" Created scraper instance: {type(scraper).__name__}")
        
        # List available methods
        available_methods = [m for m in dir(scraper) if not m.startswith('_')]
        print(f" Available methods: {available_methods}")
        
        # Try to find and call scrape method
        books = []
        
        # Method 1: Direct attribute check
        if hasattr(scraper, 'scrape_books') and callable(scraper.scrape_books):
            print(" Using scrape_books() method")
            books = scraper.scrape_books(url, max_pages=pages)
        
        # Method 2: Try scrape() method
        elif hasattr(scraper, 'scrape') and callable(scraper.scrape):
            print(" Using scrape() method")
            books = scraper.scrape(url, max_pages=pages)
        
        # Method 3: Try get_books() method
        elif hasattr(scraper, 'get_books') and callable(scraper.get_books):
            print(" Using get_books() method")
            books = scraper.get_books(url, pages)
        
        # Method 4: Manual scraping if driver exists
        elif hasattr(scraper, 'driver'):
            print(" Manual scraping needed")
            # This would require custom implementation
            return {
                "success": False,
                "message": "Manual scraping not implemented. Add scrape method to your scraper class."
            }
        
        else:
            return {
                "success": False,
                "message": f"No scrape method found. Available: {available_methods}"
            }
        
        print(f" Scraped {len(books)} books")
        
        # Save to database
        if books and len(books) > 0:
            success = db.save_books(books)
            if not success:
                print(" Failed to save books to database")
        else:
            print(" No books scraped")
        
        # Cleanup
        try:
            if hasattr(scraper, 'close') and callable(scraper.close):
                scraper.close()
                print(" Scraper closed")
            elif hasattr(scraper, 'driver') and hasattr(scraper.driver, 'quit'):
                scraper.driver.quit()
                print(" Driver quit")
        except Exception as cleanup_error:
            print(f" Cleanup error: {cleanup_error}")
        
        return {
            "success": True,
            "message": f"Successfully scraped {len(books)} books",
            "count": len(books),
            "books_sample": books[:3] if books else []
        }
        
    except Exception as e:
        error_details = traceback.format_exc()
        print(f" Scraping error: {e}")
        print(error_details)
        
        return {
            "success": False,
            "message": f"Error during scraping: {str(e)}",
            "details": error_details[:500]  # First 500 chars
        }

@app.get("/api/stats", response_class=JSONResponse)
async def get_stats():
    """API for statistics - FIXED VERSION"""
    try:
        books = db.get_all_books()
        
        if not books:
            return {
                "success": True,
                "total_books": 0,
                "message": "No books in database",
                # ✅ Dodaj prazne podatke za dashboard
                "average_price": 0,
                "average_rating": 0,
                "books_by_rating": {
                    "1_star": 0, "2_star": 0, "3_star": 0, 
                    "4_star": 0, "5_star": 0
                }
            }
        
        prices = [float(b.get("price", 0)) for b in books if b.get("price") is not None]
        ratings = [int(b.get("rating", 0)) for b in books if b.get("rating") is not None]
        
        # ✅ Price distribution - KORISTI OVO ZA GRAFIKON
        price_dist = {
            "0-5": len([p for p in prices if 0 <= p < 5]),
            "5-10": len([p for p in prices if 5 <= p < 10]),
            "10-15": len([p for p in prices if 10 <= p < 15]),
            "15-20": len([p for p in prices if 15 <= p < 20]),
            "20+": len([p for p in prices if p >= 20])
        }
        
        # ✅ FIXED: Rating distribution - KORISTI KLJUČEVE KOJE DASHBOARD OČEKUE
        rating_dist = {
            "1_star": len([r for r in ratings if r == 1]),
            "2_star": len([r for r in ratings if r == 2]),
            "3_star": len([r for r in ratings if r == 3]),
            "4_star": len([r for r in ratings if r == 4]),
            "5_star": len([r for r in ratings if r == 5])
        }
        
        return {
            "success": True,
            "total_books": len(books),
            "average_price": round(sum(prices) / len(prices), 2) if prices else 0,
            "average_rating": round(sum(ratings) / len(ratings), 2) if ratings else 0,
            "min_price": min(prices) if prices else 0,
            "max_price": max(prices) if prices else 0,
            "price_distribution": price_dist,  # Za priceChart
            "books_by_rating": rating_dist,    # ✅ OVO JE KLJUČNO - dashboard očekuje books_by_rating
            "last_update": books[0].get("timestamp") if books else None
        }
    except Exception as e:
        print(f"❌ Error in /api/stats: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/export/{format}", response_class=JSONResponse)
async def export_books(format: str = "csv"):
    """API to export data"""
    try:
        if format == "csv":
            filepath = "data/books_export.csv"
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            success = db.export_to_csv(filepath)
            
            if success and os.path.exists(filepath):
                return {
                    "success": True,
                    "message": "CSV exported successfully",
                    "file": filepath,
                    "size": os.path.getsize(filepath)
                }
        
        return {
            "success": False,
            "message": f"Export format '{format}' not supported"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Export error: {str(e)}"
        }

@app.get("/api/health", response_class=JSONResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "scraper_available": ScraperClass is not None,
        "database": os.path.exists(db_path),
        "books_count": len(db.get_all_books())
    }

# ===================== ERROR HANDLERS =====================

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors"""
    return JSONResponse(
        status_code=404,
        content={"success": False, "error": "Endpoint not found"}
    )

@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    """Handle 500 errors"""
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": "Internal server error"}
    )

# ===================== MAIN =====================
if __name__ == "__main__":
    import uvicorn
    print(" Starting Book Scraper Dashboard...")
    print(" Dashboard: http://localhost:8000")
    print(" API Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)