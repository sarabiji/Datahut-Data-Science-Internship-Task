 # Datahut-Data-Science-Internship-Task

## Puma Women's Footwear Scraper

### Objective
The goal of this project was to scrape product data for all items in the Women's Footwear category on the Indian Puma website. The final output is a clean, structured CSV file containing key product attributes for analysis.

---

### Scraping Approach

The scraper was built using Python and several key libraries:
* **Selenium**: To control a web browser for scraping the main product grid, which loads its content dynamically using JavaScript and an "infinite scroll" mechanism.
* **BeautifulSoup**: To parse the HTML content from both the main grid and the individual product pages.
* **SQLite**: To provide a robust, incremental storage solution. Data was saved to the database one by one to prevent data loss during long scraping sessions and to handle duplicates automatically.
* **Requests**: For the second phase of scraping, where it was faster to fetch the HTML of individual product pages directly.
* **Pandas**: To export the final, clean data from the SQLite database into a CSV file.

The process was divided into two main phases:
1.  **Phase 1**: A Selenium-driven browser automatically scrolled to the bottom of the main category page to load all products. The basic information (name, URL, price) for each product was scraped and saved to the database.
2.  **Phase 2**: The script then scraped the details (description, sizes, ratings) by visiting each product URL saved in the database. To significantly speed up this process, this phase was implemented with **multithreading**, allowing multiple pages to be scraped concurrently.

---

## How to Run

1.  **Prerequisites**: Install the required Python libraries from your terminal.

    ```bash
           pip install -r requirements.txt             
    ```

2.  **WebDriver**: Download the appropriate `ChromeDriver` for your version of Google Chrome and ensure it is accessible in your system's PATH.

3.  **Configure**: Open the `phase1_scraper.py` file and update the `headers` dictionary with fresh values for `x-pum-app-id` and `x-pum-app-key` from your browser if you encounter errors.

4.  **Execute**: Run the main script from your terminal to start the entire process.

    ```bash
    python scraper.py
    ```

    The script will first run Phase 1 to gather all the basic product data, and then automatically proceed to Phase 2 to scrape the details. The final, complete dataset will be saved as `puma_complete_dataset.csv`.

-----

### Challenges Faced & How They Were Handled

* **Challenge**: **Dynamic Content & Infinite Scroll**
    * The initial `requests`-based script failed because the product grid is loaded with JavaScript.
    * **Solution**: Switched to **Selenium** to automate a real browser, allowing the script to wait for all dynamic content to load before scraping. A "patient" scrolling loop was implemented to handle the infinite scroll reliably.

* **Challenge**: **Anti-Scraping Measures**
    * During development, the site's API returned `500 Internal Server Error` responses to block the script.
    * **Solution**: We used the browser's developer tools to inspect the network requests made by a real browser. We found and replicated specific **request headers** (like `x-pum-app-id` and `x-pum-app-key`) in our script, which made the requests appear legitimate and bypassed the block.

* **Challenge**: **Performance**
    * Scraping hundreds of individual product pages one by one was extremely time-consuming.
    * **Solution**: The detail-scraping phase was re-written to be **multithreaded** using Python's `ThreadPoolExecutor`. This allowed the script to scrape up to 10 pages simultaneously, dramatically reducing the total runtime.

* **Challenge**: **Stale Data**
    * The script was not updating the database with the new data because the `Description` column was already filled with "Not Found".
    * **Solution**: The database query was updated to look for products where the description is either missing OR still has the "Not Found" placeholder.

* **Challenge**: **Changing HTML Structure**
    * The website's HTML structure changed, and the CSS selectors we were using to find the data were no longer valid.
    * **Solution**: The product page was inspected and the new selectors for the description and sizes were found and updated in the script.

---

### Limitations

* The scraper's success is dependent on the current HTML structure and class names of the Puma website, which are subject to change.
* The `x-pum-` headers used to bypass anti-scraping measures might be temporary or session-based and could require updating for future runs.
* The ratings and reviews are not available for all products.
