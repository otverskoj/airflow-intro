from datetime import timedelta

from airflow import DAG
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.python import PythonOperator
from pendulum import datetime

from utils.utils import return_one_sample
from utils.model.utils import inference


with DAG(
    dag_id='iris_pipeline',
    default_args={
        'depends_on_past': False,
        'email': ['otverskoj@gmail.com'],
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(seconds=10)
    },
    schedule_interval=timedelta(seconds=10),
    start_date=datetime(2022, 6, 13),
    catchup=False,
    tags=['iris']
) as dag:
    
    # check_iris_sender = HttpSensor(
    #     task_id='check_iris_sender',
    #     http_conn_id='iris',
    #     endpoint='iris_sample'
    # )
    
    # get_iris_sample = SimpleHttpOperator(
    #     task_id='get_iris_sample',
    #     method='GET',
    #     http_conn_id='iris',  # configured in airflow UI
    #     endpoint='iris_sample',
    #     headers={'Content-Type': 'application/json'},
    #     response_check=lambda response: response.status_code == 200,
    #     log_response=True,
    #     dag=dag
    # )

    create_tables = PostgresOperator(
        depends_on_past=True,
        task_id='create_tables',
        postgres_conn_id='postgres',
        sql='sql/create_tables.sql'
    )

    tmp_task = PythonOperator(
        depends_on_past=True,
        task_id='tmp_task',
        python_callable=return_one_sample
    )

    save_iris_sample = PostgresOperator(
        depends_on_past=True,
        task_id='save_iris_sample',
        postgres_conn_id='postgres',
        sql='sql/save_iris_sample.sql'
    )

    work_with_model = PythonOperator(
        depends_on_past=True,
        task_id='work_with_model',
        python_callable=inference
    )

    create_tables >> tmp_task >> save_iris_sample >> work_with_model
