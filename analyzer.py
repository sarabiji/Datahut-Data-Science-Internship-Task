import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def analyze_puma_data(input_file="final_dataset.csv"):
    """
    Analyzes and visualizes the scraped Puma product data.
    """
    df = pd.read_csv(input_file)
    # --- 1. Descriptive Statistics ---
    print("--- Descriptive Statistics ---")
    print(df[['Full Price', 'Discounted Price', 'DiscountPercentage']].describe())
    print("\n" + "="*50 + "\n")

    # --- 2. Visualization ---
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