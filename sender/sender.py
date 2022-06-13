# from time import sleep
# from typing import Union, Tuple
# from pprint import pprint

# from sklearn.datasets import load_iris
# import numpy as np
# import requests

# import config


# def send_sample(url: str, sample: dict[str, Union[float, int]]) -> None:
#     requests.post(url, sample)


# def main() -> None:
#     iris = load_iris()
#     for sample in zip(iris.data, iris.target):
#         send_sample(
#             config.URL,
#             _format_sample(sample)
#             )
#         sleep(config.SLEEP_SECONDS)


# def _format_sample(
#     sample: Tuple[np.ndarray, str]
# ) -> dict[str, Union[float, int]]:
#     data, target = sample
#     return {
#         'sepal_length': data[0],
#         'sepal_width': data[1],
#         'petal_length': data[2],
#         'petal_width': data[3],
#         'target': target
#     }


# if __name__ == '__main__':
#     main()


from fastapi import FastAPI
from pydantic import BaseModel

from utils import prepare_iris


app = FastAPI()


IRIS_DATASET = prepare_iris()
CURRENT_IRIS_SAMPLE_INDEX = 0


class IrisDatasetSample(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float
    target: int


@app.get('/iris_sample', response_model=IrisDatasetSample)
def iris_sample():
    global CURRENT_IRIS_SAMPLE_INDEX
    data = IRIS_DATASET[CURRENT_IRIS_SAMPLE_INDEX]
    CURRENT_IRIS_SAMPLE_INDEX += 1
    return {
        'sepal_length': data[0],
        'sepal_width': data[1],
        'petal_length': data[2],
        'petal_width': data[3],
        'target': data[4]
    }
