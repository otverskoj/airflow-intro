from typing import Tuple
import pickle
import io

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from minio import Minio
from minio.error import S3Error
# from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.postgres.hooks.postgres import PostgresHook


def inference():
    client = Minio(
        'minio:9000',
        access_key='minioadmin',
        secret_key='minioadmin',
        secure=False
    )

    bucket_name = 'model-bucket'
    object_name = 'model.pickle'

    if not client.bucket_exists(bucket_name):
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
    
    id, *iris_data, target = select_last_sample()
    iris_data = np.array(iris_data).reshape(1, -1)
    
    proba = model.predict_proba(iris_data)[0][0]

    model.fit(iris_data, [target])

    model_bytes = pickle.dumps(model)
    client.put_object(
        bucket_name=bucket_name,
        object_name=object_name,
        data=io.BytesIO(model_bytes),
        length=len(model_bytes)
    )
    
    return id, int(np.argmax(proba)), int(np.max(proba))
    
    # insert_model_prediction(
    #     sample_id=id,
    #     prediction=np.argmax(proba),
    #     proba=np.max(proba)
    # )


def select_last_sample() -> Tuple[int, float, float, float, float, int]:
    postgres_hook = PostgresHook(postgres_conn_id='postgres')

    with postgres_hook.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
            """
            SELECT
                id, sepal_length, sepal_width, petal_length, petal_width, target
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
    data = np.array([
        [6, 2.2, 4, 1],
        [6.5, 3.2, 5.1, 2],
        [5, 3.6, 1.4, 0.2]
    ])
    target = np.array([1, 2, 0])
    model.fit(data, target)
    return model


# def insert_model_prediction(sample_id: int, prediction: int, proba=float):
#     postgres_hook = PostgresHook(postgres_conn_id='postgres')

#     with postgres_hook.get_conn() as conn:
#         with conn.cursor() as cur:
#             cur.execute(
#             """
#             INSERT INTO
#                 model_predictions ( sample_id, prediction, proba )
#             VALUES
#                 ( %s, %s, %s );
#             """,
#             (sample_id, prediction, proba)
#             )
#     conn.close()
