from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

DBT_PROJECT_DIR = '/opt/airflow/dbt_project'
DBT_PROFILES_DIR = '/opt/airflow/dbt_project'
DBT_FLAGS = f'--project-dir {DBT_PROJECT_DIR} --profiles-dir {DBT_PROFILES_DIR}'

default_args = {
    'owner': 'data-team',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='dbt_snowflake_pipeline_with_sql_check',
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule='@daily',
    catchup=False,
    tags=['dbt', 'snowflake'],
) as dag:

    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command=f'dbt run {DBT_FLAGS}',
    )

    dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command=f'dbt test {DBT_FLAGS}',
    )

    check_row_count = SQLExecuteQueryOperator(
        task_id='check_customer_orders_row_count',
        conn_id='snowflake_default',
        sql='''
            select case
                when count(*) = 0 then 1 / 0
                else 1
            end
            from dbt_dev.customer_orders;
        ''',
    )

    publish = EmptyOperator(task_id='publish')

    dbt_run >> dbt_test >> check_row_count >> publish