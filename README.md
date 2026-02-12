📚 Book Scraper – Python Web Scraping Project

This project is a Python-based web scraping application designed to automatically collect book data from the website BooksToScrape.com, which is commonly used for practicing web scraping techniques. The scraper extracts structured information about books and saves it into a CSV file for further analysis or processing.

The goal of this project is to demonstrate practical skills in web scraping, HTML parsing, data extraction, and basic data persistence, using clean and readable Python code.

🔍 What the Program Does

The application sends HTTP requests to the target website, retrieves HTML content, and parses it to extract relevant book data. For each book, the scraper collects:

📖 Book title

💰 Price

⭐ Rating

📦 Availability status

The extracted data is then cleaned, structured, and exported into a CSV file, making it easy to analyze, visualize, or import into other systems.

⚙️ How It Works (Program Logic)

1. HTTP Requests
The program uses the requests library to send GET requests to the target website and retrieve the raw HTML content.

2. HTML Parsing
Using BeautifulSoup, the HTML is parsed and traversed to locate specific elements that contain book information.

3. Data Extraction
Relevant fields such as title, price, rating, and availability are extracted from the DOM structure and stored in Python data structures.

4. Data Processing
The extracted data is normalized and formatted to ensure consistency (e.g. removing unnecessary characters, trimming text).

5. Data Export
All collected data is saved into a CSV file, allowing easy access for further processing or storage.

🛠 Technologies Used

Python – core programming language

Requests – handling HTTP requests

BeautifulSoup (bs4) – HTML parsing and data extraction

CSV module – exporting scraped data

Virtual Environment (venv) – dependency isolation

🎯 Purpose of the Project

This project was built to:

Practice real-world web scraping techniques,

Understand how websites are structured in HTML,

Learn how to extract and transform unstructured data,

Design a modular and extensible scraping architecture that can be adapted to other websites,

Showcase backend-oriented Python skills in a portfolio,

🚀 Possible Improvements & Future Enhancements

Add pagination support to scrape multiple pages automatically

Store data in a database (SQLite / PostgreSQL) instead of CSV

Implement error handling and logging

Add rate limiting to make scraping more polite

Build a CLI interface for flexible execution

Create a simple web UI to display scraped data

🖥 Installation

1. Clone the repository:
   git clone https://github.com/yourusername/book-scraper.git

2. Navigate into the project folder:
   cd book-scraper

3. Create and activate virtual environment:
   python -m venv venv
   venv\Scripts\activate  (Windows)

4. Install dependencies:
   pip install -r requirements.txt

▶️ Usage

Run the script:

python scraper.py

📊 Example Output (CSV)

Title, Price, Rating, Availability

"A Light in the Attic", £51.77, 3, In stock

"Tipping the Velvet", £53.74, 1, In stock

