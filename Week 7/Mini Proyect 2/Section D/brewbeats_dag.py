from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'data_engineering',
    'depends_on_past': False,
    'start_date': datetime(2026, 8, 27),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG('brewbeats_daily_pipeline', default_args=default_args, schedule_interval='@daily', catchup=False) as dag:

    run_dbt = BashOperator(
        task_id='dbt_run_models',
        bash_command='dbt run --project-dir /opt/airflow/dbt/brewbeats'
    )

    check_today_data = SnowflakeOperator(
        task_id='check_mart_data_today',
        snowflake_conn_id='snowflake_default',
        sql="""
            SELECT COUNT(*) 
            FROM brewbeats_db.analytics.mart_daily_revenue 
            WHERE sale_date = CURRENT_DATE;
        """
    )

    run_dbt >> check_today_data