-- Dimensions Gold (Spark SQL dans lh_gold, tables sources via raccourcis OneLake vers lh_silver)
CREATE OR REPLACE TABLE dim_date USING DELTA AS
SELECT
  CAST(date_format(d, 'yyyyMMdd') AS INT) AS date_key,
  d AS date, year(d) AS year, month(d) AS month, day(d) AS day,
  date_format(d, 'EEEE') AS weekday, quarter(d) AS quarter,
  dayofweek(d) IN (1, 7) AS is_weekend
FROM (SELECT explode(sequence(to_date('2024-01-01'), to_date('2027-12-31'), interval 1 day)) AS d);

CREATE OR REPLACE TABLE dim_source USING DELTA AS
SELECT * FROM VALUES
  (1, 'nucleaire', 'Nucléaire', false),
  (2, 'eolien', 'Éolien', true),
  (3, 'solaire', 'Solaire', true),
  (4, 'hydraulique', 'Hydraulique', true),
  (5, 'gaz', 'Gaz', false),
  (6, 'charbon', 'Charbon', false),
  (7, 'fioul', 'Fioul', false),
  (8, 'bioenergies', 'Bioénergies', true)
AS t(source_key, source_code, source_label, is_renewable);

CREATE OR REPLACE TABLE dim_city USING DELTA AS
SELECT * FROM VALUES
  (1, 'paris'), (2, 'marseille'), (3, 'lille'), (4, 'bordeaux'), (5, 'strasbourg')
AS t(city_key, city);
