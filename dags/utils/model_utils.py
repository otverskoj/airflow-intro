from typing import Tuple, List
import pickle
import io

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from minio import Minio
from minio.error import S3Error
# from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.postgres.hooks.postgres import PostgresHook


def inference() -> Tuple[int, int, float]:
    client = Minio(
        'minio:9000',
        access_key='minioadmin',
        secret_key='minioadmin',
        secure=False
    )

    bucket_name = 'model-bucket'
    object_name = 'model.pickle'

    if not client.bucket_exists(bucket_name):
        print('CREATE NEW BUCKET')
        client.make_bucket(bucket_name)

    try:
        response = client.get_object(
            bucket_name=bucket_name,
            object_name=object_name
        )
        model = pickle.loads(response.read())
    except S3Error:
        model = get_underfitted_model()
    else:
        response.close()
    
    sample_id, *iris_data = select_last_sample()
    iris_data = np.array(iris_data).reshape(1, -1)
    
    proba = model.predict_proba(iris_data)

    all_samples = select_all_samples()
    data, target = split_selection(all_samples)
    
    model.fit(data, target)

    model_bytes = pickle.dumps(model)
    client.put_object(
        bucket_name=bucket_name,
        object_name=object_name,
        data=io.BytesIO(model_bytes),
        length=len(model_bytes)
    )

    print('PROBA:', proba)
    
    return sample_id, int(np.argmax(proba)), float(np.max(proba))


def select_last_sample() -> Tuple[int, float, float, float, float]:
    postgres_hook = PostgresHook(postgres_conn_id='postgres')

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
            result = cur.fetchone()
    conn.close()

    # if None?
    return result


def get_underfitted_model() -> RandomForestClassifier:
    model = RandomForestClassifier()
    all_samples = select_all_samples()
    data, target = split_selection(all_samples)
    # data = np.array([
    #     [6, 2.2, 4, 1],
    #     [6.5, 3.2, 5.1, 2],
    #     [5, 3.6, 1.4, 0.2]
    # ])
    # target = np.array([1, 2, 0])
    model.fit(data, target)
    return model


def select_all_samples():
    postgres_hook = PostgresHook(postgres_conn_id='postgres')

    with postgres_hook.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
            """
            SELECT
                sepal_length, sepal_width, petal_length, petal_width, target
            FROM
                iris_dataset_samples;
            """
            )
            result = cur.fetchall()
    conn.close()

    return result


def split_selection(selection: List[Tuple]) -> Tuple[np.array, np.array]:
    data = np.array(list(map(lambda row: row[:-1], selection)))
    target = np.array(list(map(lambda row: row[-1], selection)))
    return data, target
