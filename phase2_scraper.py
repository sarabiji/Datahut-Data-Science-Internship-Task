import requests
from bs4 import BeautifulSoup
import json
import time
import random
from concurrent.futures import ThreadPoolExecutor
import utils 

MAX_WORKERS = 10 # Number of pages to scrape at the same time (multithreading)

def scrape_product_details(url):
    """Visits a single product page (URL) to scrape its details."""
    
    # (The top part with delays, headers, etc. remains the same)
    time.sleep(random.uniform(1.5, 4.0))
    headers = {'User-Agent': random.choice(utils.USER_AGENTS)}

    try:
        response = requests.get(url, headers=headers, timeout=20)
        if response.status_code != 200:
            print(f"   -> Blocked or Page Not Found. Status Code: {response.status_code} for {url}")
            return url, None

        soup = BeautifulSoup(response.content, 'html.parser')
        details = {'description': 'Not Found', 'sizes': 'Not Found', 'rating': 'N/A', 'review_count': 0}

        desc_container = soup.select_one('div[data-test-id="pdp-product-description"]')
        if desc_container:
            # Find the text container inside the main description div
            desc_text_div = desc_container.select_one('div.tw-xwzea6')
            if desc_text_div:
                details['description'] = desc_text_div.get_text(separator=' ', strip=True)
        
        size_spans = soup.select('span[data-content="size-value"]')
        if size_spans:
            sizes = [s.get_text(strip=True) for s in size_spans]
            details['sizes'] = ", ".join(sizes)
        

        script_tag = soup.find('script', type='application/ld+json')
        if script_tag and script_tag.string:
            data = json.loads(script_tag.string)
            if 'aggregateRating' in data:
                details['rating'] = data['aggregateRating'].get('ratingValue', 'N/A')
                details['review_count'] = data['aggregateRating'].get('reviewCount', 0)
        
        return url, details

    except Exception as e:
        print(f"   -> An unexpected error occurred for {url}: {e}")
        return url, None

def scrape_and_update_all_details_fast():
    """PHASE 2 (Multithreaded): Scrapes and updates details concurrently."""
    print("\n--- PHASE 2: Scraping Product Details (Multithreaded) ---")
    urls_to_scrape = utils.get_products_needing_details()
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
            print(f"Processing result {i+1}/{total}")
            url, details = result
            if details:
                utils.update_product_details_in_db(url, details)
                print(f"[{i+1}/{total}] Success: Updated details for {url}")
            else:
                print(f"[{i+1}/{total}] Failed: Could not get details for {url}")

    print("\n--- PHASE 2 Complete ---")

