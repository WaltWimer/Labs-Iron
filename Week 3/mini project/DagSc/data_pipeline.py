import os
import pandas as pd

# Define base directories using the project structure
RAW_DIR = "data/raw"
PROC_DIR = "data/processed"

os.makedirs(PROC_DIR, exist_ok=True)

def run_data_pipeline():
    print("--- 1. DATA INGESTION ---")
    customers = pd.read_csv(os.path.join(RAW_DIR, "customers.csv"))
    orders = pd.read_csv(os.path.join(RAW_DIR, "orders.csv"))
    products = pd.read_csv(os.path.join(RAW_DIR, "products.csv"))
    clickstream = pd.read_csv(os.path.join(RAW_DIR, "clickstream.csv"))
    
    print(f"Loaded customers: {len(customers)} rows")
    print(f"Loaded orders: {len(orders)} rows")
    print(f"Loaded products: {len(products)} rows")
    print(f"Loaded clickstream: {len(clickstream)} rows")

    print("\n--- 2. SCHEMA VALIDATION & DUPLICATE DETECTION ---")
    # Detect duplicate customers by customer_id
    dup_customers = customers[customers.duplicated(subset=['customer_id'], keep=False)]
    print(f"Duplicate customer records detected: {len(dup_customers)}")
    
    # Clean duplicate customers
    customers_clean = customers.drop_duplicates(subset=['customer_id']).copy()
    
    # Standardize city names
    if 'city' in customers_clean.columns:
        customers_clean['city'] = customers_clean['city'].str.strip().str.title()

    # Convert timestamps correctly
    if 'signup_date' in customers_clean.columns:
        customers_clean['signup_date'] = pd.to_datetime(customers_clean['signup_date'], errors='coerce')

    if 'order_date' in orders.columns:
        orders['order_date'] = pd.to_datetime(orders['order_date'], errors='coerce')

    print("\n--- 3. DATA TRANSFORMATION & MERGING ---")
    # Merge orders with customers and products for analytical processing
    df_merged = orders.merge(customers_clean, on='customer_id', how='left')
    df_merged = df_merged.merge(products, on='product_id', how='left')
    
    # Calculate total revenue per row
    if 'quantity' in df_merged.columns and 'unit_price' in df_merged.columns:
        df_merged['total_revenue'] = df_merged['quantity'] * df_merged['unit_price']

    # Export analytical dataset into CSV format
    output_csv = os.path.join(PROC_DIR, "analytical_dataset.csv")
    df_merged.to_csv(output_csv, index=False)
    print(f"Analytical dataset saved to CSV: {output_csv}")

    print("\n--- 4. EXPORT OPTIMIZATION & FORMAT COMPARISON ---")
    # Export analytical dataset into Parquet format
    output_parquet = os.path.join(PROC_DIR, "analytical_dataset.parquet")
    df_merged.to_parquet(output_parquet, index=False, engine='pyarrow')
    print(f"Analytical dataset saved to Parquet: {output_parquet}")

    # Compare storage sizes on disk
    csv_size = os.path.getsize(output_csv) / 1024
    parquet_size = os.path.getsize(output_parquet) / 1024
    print(f"\nStorage Size Comparison:")
    print(f" - CSV Size: {csv_size:.2f} KB")
    print(f" - Parquet Size: {parquet_size:.2f} KB")

if __name__ == "__main__":
    run_data_pipeline()