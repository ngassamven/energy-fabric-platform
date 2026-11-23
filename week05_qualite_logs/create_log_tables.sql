-- Tables d'observabilité (à exécuter dans le Lakehouse Silver, SQL endpoint ou notebook Spark SQL)
CREATE TABLE IF NOT EXISTS ops_pipeline_runs (
  run_id STRING,
  pipeline_name STRING,
  notebook_name STRING,
  status STRING,          -- SUCCESS | FAILED
  rows_read BIGINT,
  rows_written BIGINT,
  rows_rejected BIGINT,
  error_message STRING,
  started_at TIMESTAMP,
  ended_at TIMESTAMP
) USING DELTA;

CREATE TABLE IF NOT EXISTS ops_quality_results (
  run_id STRING,
  table_name STRING,
  check_name STRING,
  passed BOOLEAN,
  details STRING,
  checked_at TIMESTAMP
) USING DELTA;
