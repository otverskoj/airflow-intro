CREATE TABLE IF NOT EXISTS "iris_dataset_samples" (
  "id" SERIAL PRIMARY KEY,
  "created_at" timestamp NOT NULL DEFAULT (now()),
  "sepal_length" float8 NOT NULL,
  "sepal_width" float8 NOT NULL,
  "petal_length" float8 NOT NULL,
  "petal_width" float8 NOT NULL,
  "target" varchar NOT NULL
);

CREATE TABLE IF NOT EXISTS "model_predictions" (
  "id" SERIAL PRIMARY KEY,
  "sample_id" int UNIQUE NOT NULL,
  "created_at" timestamp NOT NULL DEFAULT (now()),
  "prediction" varchar NOT NULL,
  "proba" float8 NOT NULL
);

ALTER TABLE "model_predictions" ADD FOREIGN KEY ("sample_id") REFERENCES "iris_dataset_samples" ("id");
