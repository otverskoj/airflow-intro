from datetime import timedelta

from airflow import DAG
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.python import PythonOperator
from pendulum import datetime

from utils.utils import return_one_sample


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
        task_id='create_tables',
        postgres_conn_id='postgres-airflow',
        sql='sql/create_tables.sql'
    )

    tmp_task = PythonOperator(
        task_id='tmp_task',
        python_callable=return_one_sample
    )

    save_iris_sample = PostgresOperator(
        task_id='save_iris_sample',
        postgres_conn_id='postgres-airflow',
        sql='sql/save_iris_sample.sql'
        # params={
        #     'sepal_length': 1.0, 
        #     'sepal_width': 2.0,
        #     'petal_length': 3.0,
        #     'petal_width': 4.0,
        #     'target': 5.0
        # }
    )

    create_tables >> tmp_task >> save_iris_sample
