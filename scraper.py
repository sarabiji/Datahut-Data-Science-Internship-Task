import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
import time
import sqlite3
from concurrent.futures import ThreadPoolExecutor

DB_NAME = 'puma_products.db'
URL = "https://in.puma.com/in/en/womens/womens-shoes"
CSV_FILENAME = "puma_complete_dataset.csv"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/'}
MAX_WORKERS = 10 # Number of pages to scrape at the same time (multithreading)

# --Database functions and Scraping Logic--
def setup_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            "Product URL" TEXT PRIMARY KEY, "Product Name" TEXT, "Image URL" TEXT,
            "Discounted Price" TEXT, "Full Price" TEXT, "Description" TEXT, 
            "Sizes" TEXT, "Rating" TEXT, "Review Count" INTEGER
        )
    ''')
    conn.commit()
    conn.close()
    print("Database is set up.")

def save_product_to_db(product_data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO products ("Product URL", "Product Name", "Image URL", "Discounted Price", "Full Price") 
        VALUES (?, ?, ?, ?, ?)
    ''', (
        product_data.get('Product URL'),
        product_data.get('Product Name'),
        product_data.get('Image URL'),
        product_data.get('Discounted Price'),
        product_data.get('Full Price')
    ))
    conn.commit()
    conn.close()

def update_product_details_in_db(url, details):
    """Updates a product row with the scraped description, sizes, and ratings."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE products 
        SET "Description" = ?, "Sizes" = ?, "Rating" = ?, "Review Count" = ?
        WHERE "Product URL" = ?
    ''', (details['description'], details['sizes'], details['rating'], details['review_count'], url))
    conn.commit()
    conn.close()

def get_products_needing_details():
    """Gets all products from the DB that don't have a description yet."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT "Product URL" FROM products WHERE "Description" IS NULL')
    products = cursor.fetchall()
    conn.close()
    return [p[0] for p in products]

# --- Scraping Logic ---
def scrape_all_product_basics(url):
     """PHASE 1: Uses Selenium to get basic data for all products."""
     print("--- PHASE 1: Scraping Basic Product Info ---")
     # WebDriver Initialization (with STEALTH options
     options = webdriver.ChromeOptions()
     options.add_argument("--headless")
     options.add_argument("--start-maximized")
     options.add_argument('--no-sandbox')
    
     # Anti-detection measures
     options.add_argument('--disable-blink-features=AutomationControlled')
     options.add_experimental_option("excludeSwitches", ["enable-automation"])
     options.add_experimental_option('useAutomationExtension', False)

     driver = webdriver.Chrome(options=options)
     driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
     print("WebDriver initialized.")

     driver.get(url)
     time.sleep(5) 

     # --- "Patient" Infinite Scroll Logic ---
     patience_counter = 0
     max_patience = 3 # We will try 3 times before giving up so as to get to the end of the page

     while patience_counter < max_patience:
        # Get the current number of products
        product_cards = driver.find_elements(By.CSS_SELECTOR, 'li[data-test-id="product-list-item"]')
        current_product_count = len(product_cards)
        print(f"Currently have {current_product_count} products on the page.")

        # Scroll the last element into view
        if product_cards:
            last_product = product_cards[-1]
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", last_product)
            print("Scrolled to the last visible product.")
        
        time.sleep(3) # Wait for new products to load

        # Check if new products have been added
        new_product_count = len(driver.find_elements(By.CSS_SELECTOR, 'li[data-test-id="product-list-item"]'))
        
        if new_product_count > current_product_count:
            patience_counter = 0 # Reset patience because we found new products
        else:
            patience_counter += 1 # Increase patience counter
            print(f"No new products loaded. Patience level: {patience_counter}/{max_patience}")

        print("Reached the end of the page.")
    
     # --- Parse the fully loaded page and save data ---
     soup = BeautifulSoup(driver.page_source, "html.parser")
     driver.quit()

     all_product_cards = soup.find_all("li", attrs={"data-test-id": "product-list-item"})
     print(f"Found a total of {len(all_product_cards)} products. Saving to database...")

     for card in all_product_cards:
        
        product_info = {}
        
        url_tag = card.find("a", attrs={"data-test-id": "product-list-item-link"})
        product_url = "https://in.puma.com" + url_tag['href'] if url_tag else None
        
        if not product_url: continue
        
        name_tag = card.find("h3")
        sale_price_tag = card.find("span", attrs={"data-test-id": "sale-price"})
        full_price_tag = card.find("span", attrs={"data-test-id": "price"})
        
        product_info = {
            'Product URL': product_url,
            'Product Name': name_tag.text.strip() if name_tag else 'N/A',
            'Image URL': (card.find("img") or {}).get('src'),
            'Discounted Price': sale_price_tag.text.strip() if sale_price_tag else 'N/A',
            'Full Price': full_price_tag.text.strip() if full_price_tag else 'N/A'
        }

        save_product_to_db(product_info)
     print("--- PHASE 1 Complete ---")

def scrape_and_update_all_details_fast():
    """PHASE 2 (Multithreaded): Scrapes and updates details concurrently."""
    print("\n--- PHASE 2: Scraping Product Details (Multithreaded) ---")
    urls_to_scrape = get_products_needing_details()
    total = len(urls_to_scrape)
    
    if total == 0:
        print("No new product details to scrape. All data is up to date.")
        return
        
    print(f"Found {total} products needing details. Starting fast scrape...")
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # The executor.map function runs scrape_product_details on all URLs in parallel
        results = executor.map(scrape_product_details, urls_to_scrape)
        
        # Process results as they are completed
        for i, result in enumerate(results):
            url, details = result
            if details:
                update_product_details_in_db(url, details)
                print(f"[{i+1}/{total}] Success: Updated details for {url}")
            else:
                print(f"[{i+1}/{total}] Failed: Could not get details for {url}")

    print("\n--- PHASE 2 Complete ---")

def scrape_product_details(url):
    """Scrapes Description, Sizes, and Ratings from a single product page."""
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        details = {'description': 'Not Found', 'sizes': 'Not Found', 'rating': 'N/A', 'review_count': 0}

        desc_tag = soup.select_one('div.pdp-description-content')
        if desc_tag: details['description'] = desc_tag.get_text(strip=True)

        size_container = soup.select_one('div[data-test-id="size-selection-list"]')
        if size_container: details['sizes'] = ", ".join([s.get_text(strip=True) for s in size_container.find_all('button')])

        script_tag = soup.find('script', type='application/ld+json')
        if script_tag:
            data = json.loads(script_tag.string)
            if 'aggregateRating' in data:
                details['rating'] = data['aggregateRating'].get('ratingValue', 'N/A')
                details['review_count'] = data['aggregateRating'].get('reviewCount', 0)
        return url, details
    except Exception as e:
        print(f"  -> An error occurred for {url}: {e}")
        # On failure, return the URL and None
        return url, None

def export_db_to_csv(filename):
    """Exports the final data from the database to a CSV file."""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM products", conn)
    conn.close()
    df.to_csv(filename, index=False)
    print(f"\nSuccessfully exported {len(df)} products to {filename}")


# --- Main Execution ---
if __name__ == '__main__':
    setup_database()
    scrape_all_product_basics(URL) # Run this first to get all the URLs
    # scrape_and_update_all_details_fast()
    export_db_to_csv(CSV_FILENAME)