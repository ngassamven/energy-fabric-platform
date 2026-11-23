# Notebook Fabric : Bronze -> Silver INCRÉMENTAL pour la météo
# %run nb_watermark_helpers
from datetime import datetime
from delta.tables import DeltaTable
from pyspark.sql import functions as F, Window

spark.conf.set("spark.sql.session.timeZone", "UTC")

SRC, TGT, WM_KEY = "bronze_meteo_hourly", "silver_meteo_hourly", "silver_meteo_hourly"

last = datetime.fromisoformat(get_watermark(WM_KEY, "1970-01-01T00:00:00"))
bronze = spark.table(SRC)
upper = bronze.agg(F.max("_ingested_at")).collect()[0][0]

if upper is None or upper <= last:
    print("Rien de nouveau en Bronze.")
else:
    inc = bronze.filter((F.col("_ingested_at") > F.lit(last)) & (F.col("_ingested_at") <= F.lit(upper)))

    typed = (inc.withColumn("time", F.to_timestamp("time"))
             .withColumn("temperature_2m", F.col("temperature_2m").cast("double"))
             .withColumn("wind_speed_10m", F.col("wind_speed_10m").cast("double"))
             .withColumn("shortwave_radiation", F.col("shortwave_radiation").cast("double")))

    # Règle : clé non nulle et température plausible (-50 à 60 °C), une température nulle est rejetée
    is_valid = F.col("time").isNotNull() & F.coalesce(F.col("temperature_2m").between(-50, 60), F.lit(False))
    rejects = typed.filter(~is_valid)
    valid = typed.filter(is_valid)

    w = Window.partitionBy("city", "time").orderBy(F.col("_ingested_at").desc())
    dedup = valid.withColumn("_rn", F.row_number().over(w)).filter("_rn = 1").drop("_rn")

    if spark.catalog.tableExists(TGT):
        (DeltaTable.forName(spark, TGT).alias("t")
            .merge(dedup.alias("s"), "t.city = s.city AND t.time = s.time")
            .whenMatchedUpdateAll(condition="s._ingested_at > t._ingested_at")
            .whenNotMatchedInsertAll().execute())
    else:
        dedup.write.format("delta").saveAsTable(TGT)

    rejects.withColumn("_rejected_at", F.current_timestamp()) \
           .write.format("delta").mode("append").saveAsTable("silver_meteo_rejects")

    set_watermark(WM_KEY, "_ingested_at", upper.isoformat())
    print(f"Silver météo à jour jusqu'à {upper.isoformat()}")
