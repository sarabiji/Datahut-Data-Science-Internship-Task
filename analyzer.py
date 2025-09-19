import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# def analyze_and_visualize(input_file="puma.csv"):
    
#     df = pd.read_csv(input_file)

#     sns.set_style("whitegrid")
#     plt.figure(figsize=(12, 7))

#     print(df[['MRP', 'SalePrice', 'DiscountPercentage', 'Rating', 'NumberOfReviews']].describe())
#     print("\n" + "="*50 + "\n")

    
#     top_5_brands_by_count = df['Brand'].value_counts().head(5)
#     print(top_5_brands_by_count)
#     print("\n" + "="*50 + "\n")

#     top_5_brands_by_discount = df.groupby('Brand')['DiscountPercentage'].mean().sort_values(ascending=False).head(5)
#     print(top_5_brands_by_discount)
#     print("\n" + "="*50 + "\n")


#     # Histogram – Distribution of product prices (Sale Price)
#     plt.subplot(2, 2, 1)
#     sns.histplot(df['SalePrice'], bins=50, kde=True, color='skyblue')
#     plt.title('Distribution of Product Sale Prices')
#     plt.xlabel('Sale Price (Rs.)')
#     plt.ylabel('Frequency')
#     plt.xlim(0, df['SalePrice'].quantile(0.95)) # Trim outliers for better visualization

#     # Bar chart – Average discount percentage by top brands
#     plt.subplot(2, 2, 2)
#     avg_discount_brands = df.groupby('Brand')['DiscountPercentage'].mean().nlargest(10).sort_values()
#     avg_discount_brands.plot(kind='barh', color='salmon')
#     plt.title('Top 10 Brands by Average Discount %')
#     plt.xlabel('Average Discount Percentage (%)')
#     plt.ylabel('Brand')

#     # Box plot – Price distribution of top 5 brands by product count
#     plt.subplot(2, 2, 3)
#     top_brands_list = top_5_brands_by_count.index.tolist()
#     filtered_df_brands = df[df['Brand'].isin(top_brands_list)]
#     sns.boxplot(x='SalePrice', y='Brand', data=filtered_df_brands, palette='pastel')
#     plt.title('Price Distribution of Top 5 Brands')
#     plt.xlabel('Sale Price (Rs.)')
#     plt.ylabel('Brand')
#     plt.xlim(0, df['SalePrice'].quantile(0.90)) # Trim outliers

#     # Scatter plot – Ratings vs Discount Percentage
#     plt.subplot(2, 2, 4)
#     # Filter out products with 0 ratings as they are unrated
#     rated_products = df[df['Rating'] > 0]
#     sns.scatterplot(x='DiscountPercentage', y='Rating', data=rated_products, alpha=0.6, color='purple')
#     plt.title('Rating vs. Discount Percentage')
#     plt.xlabel('Discount Percentage (%)')
#     plt.ylabel('Rating (1-5)')

#     plt.tight_layout()
#     plt.savefig("myntra_analysis_visuals.png")
#     print("Visualizations saved to myntra_analysis_visuals.png")
#     plt.show()



    

# if __name__ == "__main__":
#     analyze_and_visualize()