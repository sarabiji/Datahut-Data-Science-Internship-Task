# utils.py
import sqlite3
import pandas as pd

# --- Shared Constants ---
DB_NAME = 'puma_products.db'
CSV_FILENAME = "final_dataset.csv"

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
]

# --- Shared Database Functions ---
def setup_database():
    """Creates the database and the products table if they don't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            "Product URL" TEXT PRIMARY KEY, "Product Name" TEXT, "Image URL" TEXT,
            "Discounted Price" TEXT, "Full Price" TEXT, "Description" TEXT, 
            "Sizes" TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print("Database is set up.")

def save_product_to_db(product_data):
    """Saves or ignores a product with basic info into the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO products ("Product URL", "Product Name", "Image URL", "Discounted Price", "Full Price","Discount %") 
        VALUES (?, ?, ?, ?, ?)
    ''', (
        product_data.get('Product URL'),
        product_data.get('Product Name'),
        product_data.get('Image URL'),
        product_data.get('Discounted Price'),
        product_data.get('Full Price'),
        product_data.get('Discount %', '0%')
    ))
    conn.commit()
    conn.close()

def get_products_needing_details():
    """
    Gets all product URLs from the DB that are missing details
    (either NULL or the default 'Not Found' placeholder).
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT "Product URL" FROM products
        WHERE "Description" IS NULL OR "Description" = 'Not Found'
    ''')
    products = cursor.fetchall()
    conn.close()
    return [p[0] for p in products]

def update_product_details_in_db(url, details):
    """Updates a product row with the scraped description and sizes."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    sizes_as_string = str(details['sizes'])
    cursor.execute('''
        UPDATE products 
        SET "Description" = ?, "Sizes" = ?
        WHERE "Product URL" = ?
    ''', (details['description'], sizes_as_string, url))
    conn.commit()
    conn.close()

def clean_data_and_export_to_csv():
    """
    Reads data from the database, cleans it, and exports the final
    clean dataset to a CSV file.
    """
    print("\n--- Starting Data Cleaning and Preparation ---")
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM products", conn)
    conn.close()

    # Clean price columns
    for col in ['Full Price', 'Discounted Price']:
        df[col] = df[col].astype(str).str.replace('₹', '').str.replace(',', '', regex=False)
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Save the cleaned DataFrame to CSV
    df.to_csv(CSV_FILENAME, index=False)
    print(f"Successfully exported {len(df)} cleaned products to {CSV_FILENAME}")
