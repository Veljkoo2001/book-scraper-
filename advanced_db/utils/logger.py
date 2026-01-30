import logging
import os
from datetime import datetime

def setup_logger(name="scraper", log_level=logging.INFO):
    """Podešava logger sa konzolnim i fajl outputom."""
    
    # Kreiraj logs folder ako ne postoji
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Generiši naziv fajla po datumu
    current_date = datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(logs_dir, f"scraper_{current_date}.log")
    
    # Konfiguriši logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Ukloni postojeće handlere da izbegnemo duplikate
    if logger.handlers:
        logger.handlers.clear()
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

# Kreiraj default logger za import
logger = setup_logger()

# Ako želiš da odmah koristiš logger u modulima:
# from utils.logger import logger
# logger.info("Poruka")