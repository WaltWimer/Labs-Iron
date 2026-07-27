from datetime import datetime, timedelta
import os
import pandas as pd
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.sensors.filesystem import FileSensor
from airflow.operators.email import EmailOperator

# Default arguments for the DAG as requested by the mini-project
default_args = {
    'owner': 'data_engineer_walter',
    'depends_on_past': False,
    'email': ['test@ungabunga.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define Python functions for task execution
def validate_and_stage_data():
    """Validates raw schemas, handles duplicates, and stages data."""
    raw_dir = "data/raw"
    proc_dir = "data/processed"
    os.makedirs(proc_dir, exist_ok=True)
    
    customers = pd.read_csv(os.path.join(raw_dir, "customers.csv"))
    orders = pd.read_csv(os.path.join(raw_dir, "orders.csv"))
    products = pd.read_csv(os.path.join(raw_dir, "products.csv"))
    
    # Basic data validation and cleaning
    customers_clean = customers.drop_duplicates(subset=['customer_id']).copy()
    
    # Staging/Saving raw validated datasets
    customers_clean.to_csv(os.path.join(proc_dir, "staging_customers.csv"), index=False)
    orders.to_csv(os.path.join(proc_dir, "staging_orders.csv"), index=False)
    print("Data successfully validated and loaded into staging tables.")

def run_transformation_pipeline():
    """Triggers the core transformation and analytical export."""
    proc_dir = "data/processed"
    orders = pd.read_csv(os.path.join(proc_dir, "staging_orders.csv"))
    customers = pd.read_csv(os.path.join(proc_dir, "staging_customers.csv"))
    
    df_merged = orders.merge(customers, on='customer_id', how='left')
    df_merged['total_revenue'] = df_merged['quantity'] * df_merged['unit_price']
    
    # Export to Parquet for optimization
    output_parquet = os.path.join(proc_dir, "analytical_dataset.parquet")
    df_merged.to_parquet(output_parquet, index=False, engine='pyarrow')
    print("Transformation step completed. Parquet analytical dataset generated.")

# Define the DAG schedule and lifecycle
with DAG(
    dag_id='quickcart_daily_etl_pipeline',
    default_args=default_args,
    description='Daily automated ETL pipeline for QuickCart modern data platform',
    schedule_interval='0 2 * * *',  # Runs daily at 2 AM
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=['quickcart', 'etl', 'production'],
) as dag:

    # 1. Sensor task to check if raw source files exist before running
    wait_for_customers_file = FileSensor(
        task_id='wait_for_customers_file',
        filepath='data/raw/customers.csv',
        poke_interval=30,
        timeout=600,
        mode='poke',
    )

    # 2. Validation and Staging Task
    stage_data_task = PythonOperator(
        task_id='validate_and_stage_data',
        python_callable=validate_and_stage_data,
    )

    # 3. Transformation and Analytical Loading Task
    transform_task = PythonOperator(
        task_id='run_transformation_pipeline',
        python_callable=run_transformation_pipeline,
    )

    # 4. Failure Alert Notification Task (Triggers if upstream tasks fail)
    failure_alert = EmailOperator(
        task_id='send_failure_email_alert',
        to='data_ops@quickcart.com',
        subject='[ALARM] QuickCart ETL Pipeline Failed',
        html_content='<h3>The QuickCart Daily ETL Pipeline has failed. Please check Airflow logs.</h3>',
        trigger_rule='one_failed',
    )

    # Define Task Dependencies (Workflow sequence)
    wait_for_customers_file >> stage_data_task >> transform_task
    [stage_data_task, transform_task] >> failure_alert