# docker/Dockerfile
FROM python:3.11-slim

# Instaliraj system dependencies za Chrome i Selenium
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update && apt-get install -y \
    google-chrome-stable \
    fonts-ipafont-gothic \
    fonts-wqy-zenhei \
    fonts-thai-tlwg \
    fonts-kacst \
    fonts-freefont-ttf \
    libxss1 \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Instaliraj ChromeDriver (pokušaj da pronađeš odgovarajuću verziju)
RUN CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+\.\d+') \
    && CHROME_MAJOR_VERSION=$(echo $CHROME_VERSION | cut -d'.' -f1) \
    && echo "Chrome version: $CHROME_VERSION" \
    && echo "Chrome major version: $CHROME_MAJOR_VERSION" \
    && CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_MAJOR_VERSION") \
    && echo "ChromeDriver version: $CHROMEDRIVER_VERSION" \
    && wget -q "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip" \
    && unzip chromedriver_linux64.zip \
    && mv chromedriver /usr/local/bin/ \
    && rm chromedriver_linux64.zip

# Kreiraj radni direktorijum
WORKDIR /app

# Kopiraj requirements prvo (za caching)
COPY requirements.txt .

# Instaliraj Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Kopiraj ceo projekat
COPY . .

# Kreiraj potrebne foldere
RUN mkdir -p logs data/exports

# Postavi environment varijable
ENV PYTHONPATH=/app
ENV CHROMEDRIVER_PATH=/usr/local/bin/chromedriver

# Default komanda
CMD ["python", "main.py"]

#Setovanje PATH za Chrome i Chromedriver
ENV PATH="/usr/local/bin:${PATH}"

#Proverava da li ChromeDriver/Chrome radi
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:9515 || exit 1

#Optimizuje instalaciju pip

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt
