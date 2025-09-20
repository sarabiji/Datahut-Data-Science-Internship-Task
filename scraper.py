# main.py
import utils
import phase1_scraper
import phase2_scraper

if __name__ == '__main__':
    # 1. Set up the database
    utils.setup_database()
    
    # 2. Run Phase 1 to get all basic product info and URLs
    phase1_scraper.scrape_all_product_basics()
    
    # 3. Run Phase 2 to get the details for each product
    phase2_scraper.scrape_and_update_all_details_fast()
    
    # 4. Export the final, complete dataset to a CSV file
    utils.export_db_to_csv()
    
    print("\nScraping process finished!")