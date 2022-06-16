INSERT INTO 
    iris_dataset_samples ( sepal_length, sepal_width, petal_length, petal_width, target )
VALUES
    (
        {% for value in ti.xcom_pull(task_ids='get_iris_sample').values() %}
            {{ value }}{{ ", " if not loop.last }}
        {% endfor %}
    );