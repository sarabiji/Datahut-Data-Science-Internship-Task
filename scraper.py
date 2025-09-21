# main.py
import utils
import phase1_scraper
import phase2_scraper

if __name__ == '__main__':
    # 1. Set up the database
    utils.setup_database()
    
    # 2. Run Phase 1 to get all basic product info and URLs
    phase1_scraper.scrape_all_product_basics(phase1_scraper.URL)
    
    # 3. Run Phase 2 to get the details for each product
    phase2_scraper.scrape_all_details_sequentially()

    # 4. Clean the scraped data and export the final dataset
    utils.clean_data_and_export_to_csv()
    
    print("\nScraping process finished!")