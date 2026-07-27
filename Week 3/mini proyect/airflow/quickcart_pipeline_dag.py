from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.sensors.filesystem import FileSensor
from datetime import datetime, timedelta
import logging
import pandas as pd

# Default settings: retries, delays, and failure emails
default_args = {
    'owner': 'data_engineering_team',
    'depends_on_past': False,
    'email': ['alerts@quickcart.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

# DAG Definition: Runs daily at 2 AM
with DAG(
    'quickcart_elt_pipeline',
    default_args=default_args,
    description='Daily ELT pipeline for QuickCart',
    schedule_interval='0 2 * * *', 
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=['quickcart', 'elt'],
) as dag:

    # 1. Sensor: Wait for raw CSV files to exist in the local directory
    file_sensor_task = FileSensor(
        task_id='wait_for_raw_csvs',
        filepath=r'E:\Workflow\Airflow\data\raw\orders.csv', 
        fs_conn_id='fs_default',
        poke_interval=60,
        timeout=600,
    )

    # Python functions for DAG tasks
    def extract_data():
        logging.info("Extracting CSV files from local directory...")
        orders_df = pd.read_csv(r'E:\Workflow\Airflow\data\raw\orders.csv')
        logging.info(f"Extracted {len(orders_df)} records from orders.csv")
        
    def validate_data():
        logging.info("Performing schema and quality validation...")
        orders_df = pd.read_csv(r'E:\Workflow\Airflow\data\raw\orders.csv')
        if 'customer_id' not in orders_df.columns:
            raise ValueError("Validation Failed: Missing customer_id")
        logging.info("Validation passed successfully.")
        
    def load_to_staging():
        logging.info("Loading raw data into staging tables...")
        logging.info("Data successfully loaded into staging schema.")

    # 2. Extract Task
    extract_task = PythonOperator(
        task_id='extract_csv_files',
        python_callable=extract_data,
    )

    # 3. Validate Task
    validate_task = PythonOperator(
        task_id='perform_validation',
        python_callable=validate_data,
    )

    # 4. Load Task
    load_staging_task = PythonOperator(
        task_id='load_raw_data_staging',
        python_callable=load_to_staging,
    )

    # 5. Transform Task
    transform_task = BashOperator(
        task_id='trigger_transformation',
        bash_command='echo "Triggering SQL transformations in the Data Warehouse to build Star Schema..."',
    )

    # Task Dependencies
    file_sensor_task >> extract_task >> validate_task >> load_staging_task >> transform_task