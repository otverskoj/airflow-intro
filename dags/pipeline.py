from datetime import timedelta

from airflow import DAG
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.http.operators.http import SimpleHttpOperator
from pendulum import datetime


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
    schedule_interval=timedelta(minutes=3),
    start_date=datetime(2022, 6, 13),
    catchup=False,
    tags=['iris']
) as dag:
    
    check_iris_sender = HttpSensor(
        task_id='check_iris_sender',
        http_conn_id='iris',
        endpoint='iris_sample'
    )
    
    get_iris_sample = SimpleHttpOperator(
        task_id='get_iris_sample',
        method='GET',
        http_conn_id='iris',  # configured in airflow UI
        endpoint='iris_sample',
        headers={'Content-Type': 'application/json'},
        response_check=lambda response: response.status_code == 200,
        log_response=True,
        dag=dag
    )
