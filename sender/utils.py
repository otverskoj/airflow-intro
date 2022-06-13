from sklearn.datasets import load_iris
import numpy as np


def prepare_iris():
    iris = load_iris()
    dataset = np.hstack((iris.data, iris.target[:, np.newaxis]))
    print(type(iris.data[0, 0]))
    np.random.shuffle(dataset)
    return dataset


if __name__ == '__main__':
    prepare_iris()
