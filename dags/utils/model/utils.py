from minio import Minio
from minio.error import S3Error
# from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.postgres.hooks.postgres import PostgresHook
from sklearn.tree import DecisionTreeClassifier


def inference():
    client = Minio(
        'minio:9000',
        access_key='minioadmin',
        secret_key='minioadmin',
        secure=False
    )

    bucket_name = 'model-bucket'
    object_name = 'model.sav'

    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)

    try:
        model = client.fget_object(bucket_name, object_name, './file.txt')
    except S3Error:
        model = DecisionTreeClassifier()
    
    sample = select_last_sample()


def select_last_sample():
    postgres_hook = PostgresHook(postgres_conn_id='postgres')
    # conn = postgres_hook.get_conn()
    # cur = conn.cursor()
    # cur.execute(
    #     """
    #     SELECT
    #         id, sepal_length, sepal_width, petal_length, petal_width
    #     FROM
    #         iris_dataset_samples
    #     ORDER BY
    #         id DESC
    #     LIMIT 1;"""
    # )
    # result = cur.fetchall()
    # conn.commit()
    # cur.close()
    # conn.close()

    with postgres_hook.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
            """
            SELECT
                id, sepal_length, sepal_width, petal_length, petal_width
            FROM
                iris_dataset_samples
            ORDER BY
                id DESC
            LIMIT 1;"""
            )
            result = cur.fetchall()
    conn.close()

    print('result', result)
