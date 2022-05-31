from time import sleep
from typing import Union, Tuple
from pprint import pprint

from sklearn.datasets import load_iris
import numpy as np
import requests

import config


def send_sample(url: str, sample: dict[str, Union[float, int]]) -> None:
    requests.post(url, sample)


def main() -> None:
    iris = load_iris()
    for sample in zip(iris.data, iris.target):
        send_sample(
            config.URL,
            _format_sample(sample)
            )
        sleep(config.SLEEP_SECONDS)


def _format_sample(
    sample: Tuple[np.ndarray, str]
) -> dict[str, Union[float, int]]:
    data, target = sample
    return {
        'sepal_length': data[0],
        'sepal_width': data[1],
        'petal_length': data[2],
        'petal_width': data[3],
        'target': target
    }


if __name__ == '__main__':
    main()
