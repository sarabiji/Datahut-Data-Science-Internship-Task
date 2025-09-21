import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def analyze_puma_data(input_file="final_dataset.csv"):
    """
    Analyzes and visualizes the scraped Puma product data.
    """
    df = pd.read_csv(input_file)

    # --- 1. Data Cleaning and Preparation ---
    print("--- Cleaning Data ---")
    
    # Clean price columns by removing currency symbols and commas, then convert to numbers
    for col in ['Full Price', 'Discounted Price']:
        # Ensure the column is treated as a string before using .str accessor
        df[col] = df[col].astype(str).str.replace('₹', '', regex=False).str.replace(',', '', regex=False)
        # Coerce errors will turn non-numeric values into NaN (Not a Number)
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Drop rows where prices are missing after cleaning, as they can't be analyzed
    df.dropna(subset=['Full Price', 'Discounted Price'], inplace=True)

    # Calculate Discount Percentage, handling cases where Full Price is 0 or NaN
    df['DiscountPercentage'] = 100 * (df['Full Price'] - df['Discounted Price']) / df['Full Price']
    # Fill any resulting NaN/inf values from division by zero with 0
    df['DiscountPercentage'] = df['DiscountPercentage'].replace([np.inf, -np.inf], np.nan).fillna(0)
    
    print("Data cleaning complete.\n")
    
    # --- 2. Data Analysis ---
    print("--- Descriptive Statistics ---")
    print(df[['Full Price', 'Discounted Price', 'DiscountPercentage']].describe())
    print("\n" + "="*50 + "\n")

    # --- 3. Visualization ---
    sns.set_style("whitegrid")
    plt.figure(figsize=(14, 10))
    plt.suptitle("Puma Women's Footwear Analysis", fontsize=18, y=2)

    # Plot 1: Distribution of Sale Prices
    plt.subplot(2, 2, 1)
    sns.histplot(df['Discounted Price'], bins=40, kde=True, color='skyblue')
    plt.title('Distribution of Product Sale Prices')
    plt.xlabel('Sale Price (₹)')
    plt.ylabel('Frequency')

    # Plot 2: Distribution of Discount Percentages
    plt.subplot(2, 2, 2)
    # Filter for products that actually have a discount for a more meaningful plot
    sns.histplot(df[df['DiscountPercentage'] > 0]['DiscountPercentage'], bins=40, kde=True, color='salmon')
    plt.title('Distribution of Discounts')
    plt.xlabel('Discount Percentage (%)')
    plt.ylabel('Frequency')

    # Plot 3: Price Distribution (Box Plot)
    plt.subplot(2, 2, 3)
    sns.boxplot(x=df['Discounted Price'], palette='pastel')
    plt.title('Overall Price Distribution')
    plt.xlabel('Sale Price (₹)')

    # # Plot 4: Placeholder for future analysis (e.g., by category)
    # plt.subplot(2, 2, 4)
    # plt.text(0.5, 0.5, 'Further analysis could go here,\n e.g., Price by Product Category', 
    #          ha='center', va='center', fontsize=12)
    # plt.title('Future Analysis')
    # plt.axis('off') # Hide axes for placeholder

    plt.tight_layout(rect=[0, 0, 1, 0.98])
    plt.savefig("puma_analysis_visuals.png")
    print("Visualizations saved to puma_analysis_visuals.png")
    plt.show()
    exit()

if __name__ == "__main__":
    analyze_puma_data()