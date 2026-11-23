# Notebook Fabric : Silver -> Gold INCRÉMENTAL (faits)
# Prérequis : gold_dimensions.sql exécuté ; tables Silver accessibles dans lh_gold via raccourcis OneLake.
# %run nb_watermark_helpers
from datetime import datetime
from delta.tables import DeltaTable
from pyspark.sql import functions as F

spark.conf.set("spark.sql.session.timeZone", "UTC")

EPOCH = "1970-01-01T00:00:00"
WM_E, WM_M = "gold_from_silver_eco2mix", "gold_from_silver_meteo"

last_e = datetime.fromisoformat(get_watermark(WM_E, EPOCH))
last_m = datetime.fromisoformat(get_watermark(WM_M, EPOCH))
eco = spark.table("silver_eco2mix")
met = spark.table("silver_meteo_hourly")
up_e = eco.agg(F.max("_ingested_at")).collect()[0][0] or last_e
up_m = met.agg(F.max("_ingested_at")).collect()[0][0] or last_m


def upsert(df, table, keys):
    if not spark.catalog.tableExists(table):
        df.write.format("delta").saveAsTable(table)
        return
    cond = " AND ".join(f"t.{k} = s.{k}" for k in keys)
    (DeltaTable.forName(spark, table).alias("t").merge(df.alias("s"), cond)
        .whenMatchedUpdateAll().whenNotMatchedInsertAll().execute())


# 1. Heures touchées par les nouvelles données Silver (éco2mix OU météo)
ch_e = (eco.filter((F.col("_ingested_at") > F.lit(last_e)) & (F.col("_ingested_at") <= F.lit(up_e)))
           .select(F.date_trunc("hour", "date_heure").alias("hour_ts")))
ch_m = (met.filter((F.col("_ingested_at") > F.lit(last_m)) & (F.col("_ingested_at") <= F.lit(up_m)))
           .select(F.date_trunc("hour", "time").alias("hour_ts")))
changed = ch_e.union(ch_m).distinct().cache()
changed.createOrReplaceTempView("changed_hours")
n_hours = changed.count()

if n_hours == 0:
    print("Aucune heure à recalculer.")
else:
    # 2. fact_production : grain heure x source, recalculé seulement pour les heures touchées
    prod = spark.sql("""
        SELECT CAST(date_format(date_trunc('hour', e.date_heure), 'yyyyMMdd') AS INT) AS date_key,
               date_trunc('hour', e.date_heure) AS hour_ts,
               s.source_key,
               AVG(CASE s.source_code
                     WHEN 'nucleaire' THEN e.nucleaire WHEN 'eolien' THEN e.eolien
                     WHEN 'solaire' THEN e.solaire WHEN 'hydraulique' THEN e.hydraulique
                     WHEN 'gaz' THEN e.gaz WHEN 'charbon' THEN e.charbon
                     WHEN 'fioul' THEN e.fioul WHEN 'bioenergies' THEN e.bioenergies END) AS production_mw
        FROM silver_eco2mix e
        JOIN changed_hours c ON date_trunc('hour', e.date_heure) = c.hour_ts
        CROSS JOIN dim_source s
        GROUP BY 1, 2, 3
    """)
    upsert(prod, "fact_production", ["hour_ts", "source_key"])

    # 3. fact_consumption_weather : grain heure x ville (le RLS filtre sur city_key)
    cw = spark.sql("""
        WITH eco AS (
          SELECT date_trunc('hour', e.date_heure) AS hour_ts,
                 AVG(e.consommation) AS consumption_mw,
                 AVG(e.taux_co2) AS co2_g_per_kwh
          FROM silver_eco2mix e
          JOIN changed_hours c ON date_trunc('hour', e.date_heure) = c.hour_ts
          GROUP BY 1
        ), met AS (
          SELECT date_trunc('hour', m.time) AS hour_ts, d.city_key,
                 AVG(m.temperature_2m) AS temperature_c,
                 AVG(m.wind_speed_10m) AS wind_kmh,
                 AVG(m.shortwave_radiation) AS radiation_wm2
          FROM silver_meteo_hourly m
          JOIN dim_city d ON d.city = m.city
          JOIN changed_hours c ON date_trunc('hour', m.time) = c.hour_ts
          GROUP BY 1, 2
        )
        SELECT CAST(date_format(met.hour_ts, 'yyyyMMdd') AS INT) AS date_key,
               met.hour_ts, met.city_key,
               eco.consumption_mw, eco.co2_g_per_kwh,
               met.temperature_c, met.wind_kmh, met.radiation_wm2
        FROM met LEFT JOIN eco ON eco.hour_ts = met.hour_ts
    """)
    upsert(cw, "fact_consumption_weather", ["hour_ts", "city_key"])

    # 4. Avancer les watermarks en dernier
    set_watermark(WM_E, "_ingested_at", up_e.isoformat())
    set_watermark(WM_M, "_ingested_at", up_m.isoformat())
    print(f"Gold mis à jour pour {n_hours} heure(s).")
