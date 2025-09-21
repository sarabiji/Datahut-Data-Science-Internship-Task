from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import utils # Import shared utilities

URL = "https://in.puma.com/in/en/womens/womens-shoes"

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
     max_patience = 7 # We will try 7 times before giving up so as to get to the end of the page

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

        utils.save_product_to_db(product_info)
     print("--- PHASE 1 Complete ---")
