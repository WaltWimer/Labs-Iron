import pandas as pd
import numpy as np
import os
import time

# ==========================================
# Q1. Data Ingestion Pipeline
# ==========================================

def ingest_and_validate():
    print("Starting data ingestion...")
    try:
        # Paths updated to your exact local directory
        customers = pd.read_csv(r'E:\Workflow\Airflow\data\raw\customers.csv')
        orders = pd.read_csv(r'E:\Workflow\Airflow\data\raw\orders.csv')
        products = pd.read_csv(r'E:\Workflow\Airflow\data\raw\products.csv')
        clickstream = pd.read_csv(r'E:\Workflow\Airflow\data\raw\clickstream.csv')
    except FileNotFoundError as e:
        print(f"File loading error: {e}")
        return None, None, None, None

    # Validate schema consistency
    expected_customers_cols = {'customer_id', 'customer_name', 'email', 'city', 'signup_date'}
    if not expected_customers_cols.issubset(customers.columns):
        raise ValueError("Schema error: Missing columns in customers.csv")

    # Detect duplicate customers
    duplicate_customers = customers[customers.duplicated(subset=['email'], keep=False)]
    print(f"Duplicate customers detected: {len(duplicate_customers)}")

    # Identify invalid records
    invalid_orders = orders[(orders['quantity'] <= 0) | (orders['unit_price'] < 0) | orders['customer_id'].isna()]
    print(f"Invalid records in orders: {len(invalid_orders)}")
    
    return customers, orders, products, clickstream

# ==========================================
# Q2. Data Cleaning & Transformation
# ==========================================

def clean_data(customers, orders, products, clickstream):
    print("Cleaning and transforming data...")
    # Standardize city names
    if 'city' in customers.columns:
        customers['city'] = customers['city'].astype(str).str.strip().str.title()

    # Convert timestamps correctly
    customers['signup_date'] = pd.to_datetime(customers['signup_date'], errors='coerce')
    orders['order_date'] = pd.to_datetime(orders['order_date'], errors='coerce')
    clickstream['event_timestamp'] = pd.to_datetime(clickstream['event_timestamp'], errors='coerce')

    # Handle missing values
    orders['payment_status'] = orders['payment_status'].fillna('UNKNOWN')
    
    # Remove corrupted rows
    customers_clean = customers.dropna(subset=['customer_id', 'email']).drop_duplicates(subset=['email'])
    orders_clean = orders[(orders['quantity'] > 0) & (orders['unit_price'] >= 0)].dropna(subset=['order_id', 'customer_id'])
    products_clean = products.dropna(subset=['product_id'])
    clickstream_clean = clickstream.dropna(subset=['event_id', 'customer_id', 'event_timestamp'])

    return customers_clean, orders_clean, products_clean, clickstream_clean

# ==========================================
# Q3. Clickstream Analytics
# ==========================================

def analyze_clickstream(clickstream):
    print("\n--- Clickstream Analytics ---")
    
    # Find the most visited pages
    top_pages = clickstream['page_url'].value_counts().head(5)
    print("\nMost Visited Pages:\n", top_pages)

    # Calculate session counts (30-minute inactivity logic)
    clickstream = clickstream.sort_values(by=['customer_id', 'event_timestamp'])
    clickstream['time_diff'] = clickstream.groupby('customer_id')['event_timestamp'].diff()
    
    clickstream['new_session'] = (clickstream['time_diff'] > pd.Timedelta(minutes=30)) | clickstream['time_diff'].isna()
    clickstream['session_id'] = clickstream['new_session'].cumsum()
    
    total_sessions = clickstream['session_id'].nunique()
    print(f"\nTotal Sessions: {total_sessions}")

    # Find bounce rate
    events_per_session = clickstream.groupby('session_id').size()
    bounced_sessions = (events_per_session == 1).sum()
    bounce_rate = (bounced_sessions / total_sessions) * 100 if total_sessions > 0 else 0
    print(f"Bounce Rate: {bounce_rate:.2f}%")

    # Find mobile vs desktop traffic percentage
    traffic_pct = clickstream['device_type'].value_counts(normalize=True) * 100
    print("\nTraffic Percentage by Device:\n", traffic_pct)
    
    return clickstream

# ==========================================
# Q4. Export Optimization
# ==========================================

def export_and_compare(clickstream_df):
    print("\n--- Export Optimization ---")
    
    csv_filename = r'E:\Workflow\Airflow\data\clickstream_analytical.csv'
    parquet_filename = r'E:\Workflow\Airflow\data\clickstream_analytical.parquet'
    
    # Export analytical dataset
    clickstream_df.to_csv(csv_filename, index=False)
    clickstream_df.to_parquet(parquet_filename, index=False)
    
    # Compare storage sizes
    csv_size = os.path.getsize(csv_filename) / (1024 * 1024)
    parquet_size = os.path.getsize(parquet_filename) / (1024 * 1024)
    
    print(f"CSV Size: {csv_size:.2f} MB")
    print(f"Parquet Size: {parquet_size:.2f} MB")
    
    # Compare read performance
    start_time = time.time()
    pd.read_csv(csv_filename)
    csv_read_time = time.time() - start_time
    
    start_time = time.time()
    pd.read_parquet(parquet_filename)
    parquet_read_time = time.time() - start_time
    
    print(f"CSV Read Time: {csv_read_time:.4f} seconds")
    print(f"Parquet Read Time: {parquet_read_time:.4f} seconds")

# ==========================================
# Main Execution
# ==========================================
if __name__ == "__main__":
    raw_cust, raw_ord, raw_prod, raw_click = ingest_and_validate()
    
    if raw_cust is not None:
        clean_cust, clean_ord, clean_prod, clean_click = clean_data(raw_cust, raw_ord, raw_prod, raw_click)
        analyzed_clickstream = analyze_clickstream(clean_click)
        export_and_compare(analyzed_clickstream)