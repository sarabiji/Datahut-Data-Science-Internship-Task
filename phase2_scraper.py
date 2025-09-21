from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import utils
import random

# def scrape_product_details_with_selenium(url):
#     """Visits a single product page using Selenium to scrape its details."""
    
#     print(f"   -> Scraping with browser: {url}")
#     # Use the same stealth options from Phase 1
#     options = webdriver.ChromeOptions()
#     options.add_argument("--headless")
#     options.add_argument("user-agent=" + random.choice(utils.USER_AGENTS))
#     options.add_argument('--disable-blink-features=AutomationControlled')
    
#     driver = webdriver.Chrome(options=options)
    
#     details = {'description': 'Not Found', 'sizes': 'Not Found'}

#     try:
#         driver.get(url)
#         # Give the page a moment to load all dynamic content
#         time.sleep(3) 
        
#         soup = BeautifulSoup(driver.page_source, 'html.parser')

#         # Scrape Description
#         desc_container = soup.select_one('div[data-test-id="pdp-product-description"]')
#         if desc_container:
#             desc_text_div = desc_container.select_one('div.tw-xwzea6')
#             if desc_text_div:
#                 details['description'] = desc_text_div.get_text(separator=' ', strip=True)

#         # Scrape Sizes
#         size_spans = soup.select('span[data-content="size-value"]')
#         if size_spans:
#             sizes = [s.get_text(strip=True) for s in size_spans]
#             details['sizes'] = tuple(sizes)
        
#         return url, details

#     except Exception as e:
#         print(f"   -> An error occurred for {url}: {e}")
#         return url, None
#     finally:
#         # Make sure to close the browser instance
#         driver.quit()


# def scrape_all_details_sequentially():
#     """PHASE 2 (Sequential): Scrapes and updates details one by one."""
#     print("\n--- PHASE 2: Scraping Product Details (Reliably) ---")
#     urls_to_scrape = utils.get_products_needing_details()
#     total = len(urls_to_scrape)
    
#     if total == 0:
#         print("No new product details to scrape. All data is up to date.")
#         return
        
#     print(f"Found {total} products needing details. Starting scrape...")
    
#     for i, url in enumerate(urls_to_scrape):
#         progress = f"[{i+1}/{total}]"
#         url, details = scrape_product_details_with_selenium(url)
#         if details:
#             utils.update_product_details_in_db(url, details)
#             print(f"{progress} Success: Details updated.")
#         else:
#             print(f"{progress} Failed: Could not get details.")

#     print("\n--- PHASE 2 Complete ---")

# # phase2_scraper.py
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from bs4 import BeautifulSoup
# import time
# import utils
# import random

def scrape_all_details_sequentially():
    """
    PHASE 2 : Scrapes details for all products using a single,
    persistent browser session to improve speed.
    """
    print("\n--- PHASE 2: Scraping Product Details ---")
    urls_to_scrape = utils.get_products_needing_details()
    total = len(urls_to_scrape)

    if total == 0:
        print("No new product details to scrape. All data is up to date.")
        return
        
    print(f"Found {total} products needing details. Initializing browser...")

    # --- 1. Initialize Browser Once ---
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("user-agent=" + random.choice(utils.USER_AGENTS))
    options.add_argument('--disable-blink-features=AutomationControlled')
    driver = webdriver.Chrome(options=options)

    try:
        # --- 2. Loop Through All URLs ---
        for i, url in enumerate(urls_to_scrape):
            progress = f"[{i+1}/{total}]"
            details = {'description': 'Not Found', 'sizes': 'Not Found'}

            try:
                driver.get(url)
                time.sleep(2) 
                
                soup = BeautifulSoup(driver.page_source, 'html.parser')

                # Scrape Description
                desc_container = soup.select_one('div[data-test-id="pdp-product-description"]')
                if desc_container:
                    desc_text_div = desc_container.select_one('div.tw-xwzea6')
                    if desc_text_div:
                        details['description'] = desc_text_div.get_text(separator=' ', strip=True)

                # Scrape Sizes
                size_spans = soup.select('span[data-content="size-value"]')
                if size_spans:
                    sizes_list = [s.get_text(strip=True) for s in size_spans]
                    details['sizes'] = tuple(sizes_list)

                # Update the database
                utils.update_product_details_in_db(url, details)
                print(f"{progress} Success: Details updated for {url}")

            except Exception as e:
                print(f"{progress} Failed for {url}: {e}")
                
    finally:
        driver.quit()
        print("\nBrowser closed.")

    print("\n--- PHASE 2 Complete ---")

