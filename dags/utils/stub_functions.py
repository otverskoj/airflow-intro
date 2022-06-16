import urllib


def return_one_sample():
    return {
        'sepal_length': 1.0, 
        'sepal_width': 2.0,
        'petal_length': 3.0,
        'petal_width': 4.0,
        'target': 5.0
    }


def check_connection():
    urllib.request.urlopen('http://fastapi-iris-sender:8000/iris_sample')
