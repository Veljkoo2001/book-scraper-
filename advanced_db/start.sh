# start.sh - Advanced Book Scraper Dashboard Launcher

echo "==========================================="
echo "🚀  Advanced Book Scraper Dashboard"
echo "==========================================="

# Proveri da li smo u root folderu
if [ ! -f "main.py" ] && [ ! -d "web" ]; then
    echo "❌ Error: Run this script from project root folder!"
    echo "   Current folder: $(pwd)"
    exit 1
fi

# Kreiraj potrebne foldere
echo "📁 Creating necessary directories..."
mkdir -p data
mkdir -p logs
mkdir -p web/static/css
mkdir -p web/static/js

# Proveri da li postoji virtuelno okruzenje
if [ -d "venv" ]; then
    echo "🐍 Activating virtual environment..."
    source venv/bin/activate
else
    echo "ℹ️ No virtual environment found. Using system Python."
    echo "   Recommended: python -m venv venv && source venv/bin/activate"
fi

# Proveri/instaliraj zavisnosti
echo "📦 Checking dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt 2>/dev/null || echo "⚠️ Could not install all packages"
else
    echo "⚠️ requirements.txt not found!"
    echo "   Creating basic requirements..."
    echo "fastapi>=0.104.0" > requirements.txt
    echo "uvicorn[standard]>=0.24.0" >> requirements.txt
    echo "jinja2>=3.1.0" >> requirements.txt
    echo "selenium>=4.15.0" >> requirements.txt
    echo "python-dotenv>=1.0.0" >> requirements.txt
    pip install fastapi uvicorn jinja2 selenium python-dotenv
fi

# Dodatni paketi za dashboard
echo "➕ Installing dashboard dependencies..."
pip install python-multipart 2>/dev/null || echo "⚠️ Could not install python-multipart"

# Proveri da li ima podataka u bazi
if [ ! -f "data/scraped_data.db" ] || [ ! -s "data/scraped_data.db" ]; then
    echo "📚 No data found. Scraping sample books..."
    
    # Proveri da li scraper radi
    if python -c "import sys; sys.path.append('.'); from scraper.scraper import *; print('✅ Scraper OK')" 2>/dev/null; then
        echo "🔄 Scraping books.toscrape.com (2 pages)..."
        python main.py --url "https://books.toscrape.com" --pages 2 --output csv
        
        if [ $? -eq 0 ]; then
            echo "✅ Successfully scraped sample data!"
        else
            echo "⚠️ Could not scrape automatically. You can scrape manually from the dashboard."
        fi
    else
        echo "⚠️ Could not import scraper. Manual scraping required."
    fi
else
    echo "✅ Database found with existing data."
fi

# Proveri port
PORT=8000
echo "🔍 Checking if port $PORT is available..."
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️ Port $PORT is in use!"
    echo "   Trying port 8001..."
    PORT=8001
fi

# Prikaži informacije
echo ""
echo "==========================================="
echo "🌐 DASHBOARD READY!"
echo "==========================================="
echo ""
echo "📊 Open in your browser:"
echo "   Dashboard:  http://localhost:$PORT"
echo "   API Docs:   http://localhost:$PORT/docs"
echo "   API Test:   http://localhost:$PORT/api/books"
echo ""
echo "🎛️ Dashboard Features:"
echo "   • Real-time scraping control"
echo "   • Interactive charts"
echo "   • Search & filter books"
echo "   • Export to CSV"
echo "   • Book details modal"
echo ""
echo "⚡ To start scraping from dashboard:"
echo "   1. Open http://localhost:$PORT"
echo "   2. Enter URL: https://books.toscrape.com"
echo "   3. Click 'Start Scraping'"
echo ""
echo "==========================================="
echo "🖥️  Starting FastAPI server..."
echo "   Press Ctrl+C to stop"
echo "==========================================="
echo ""

# Pokreni server
uvicorn web.app:app --reload --host 0.0.0.0 --port $PORT