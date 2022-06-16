import json
from datetime import timedelta

from airflow import DAG
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.python import PythonOperator
from pendulum import datetime

from utils.stub_functions import return_one_sample, check_connection
from utils.model_utils import inference


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
    schedule_interval=timedelta(seconds=30),
    start_date=datetime(2022, 6, 13),
    catchup=False,
    tags=['iris']
) as dag:
    
    check_iris_sender = HttpSensor(
        depends_on_past=True,
        task_id='check_iris_sender',
        http_conn_id='iris',
        endpoint='iris_sample'
    )
    
    get_iris_sample = SimpleHttpOperator(
        depends_on_past=True,
        task_id='get_iris_sample',
        method='GET',
        http_conn_id='iris',
        endpoint='iris_sample',
        headers={'Content-Type': 'application/json'},
        response_check=lambda response: response.status_code == 200,
        response_filter= lambda response: json.loads(response.text),
        log_response=True,
        dag=dag
    )

    create_tables = PostgresOperator(
        depends_on_past=True,
        task_id='create_tables',
        postgres_conn_id='postgres',
        sql='sql/create_tables.sql'
    )

    insert_init_values = PostgresOperator(
        depends_on_past=True,
        task_id='insert_init_values',
        postgres_conn_id='postgres',
        sql='sql/insert_init_values.sql'
    )

    save_iris_sample = PostgresOperator(
        depends_on_past=True,
        task_id='save_iris_sample',
        postgres_conn_id='postgres',
        sql='sql/save_iris_sample.sql'
    )

    inference_model = PythonOperator(
        depends_on_past=True,
        task_id='inference_model',
        python_callable=inference
    )

    save_model_prediction = PostgresOperator(
        depends_on_past=True,
        task_id='save_model_prediction',
        postgres_conn_id='postgres',
        sql='sql/save_model_prediction.sql'
    )

    create_tables >> insert_init_values >> check_iris_sender >> \
        get_iris_sample >> save_iris_sample >> inference_model >> \
            save_model_prediction


# if __name__ == "__main__":
#     from airflow.utils.state import State

#     dag.clear()
#     dag.run()
