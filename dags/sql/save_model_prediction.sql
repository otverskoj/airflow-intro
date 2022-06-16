INSERT INTO
    model_predictions ( sample_id, prediction, proba )
VALUES
    (
        {% for value in ti.xcom_pull(task_ids='inference_model') %}
            {{ value }}{{ ", " if not loop.last }}
        {% endfor %}
    );