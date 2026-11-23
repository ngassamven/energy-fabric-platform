# Notebook Fabric : Bronze -> Silver INCRÉMENTAL pour éco2mix
# %run nb_watermark_helpers
from datetime import datetime
from delta.tables import DeltaTable
from pyspark.sql import functions as F, Window

spark.conf.set("spark.sql.session.timeZone", "UTC")

SRC, TGT, WM_KEY = "bronze_rte_eco2mix", "silver_eco2mix", "silver_eco2mix"

# 1. Borne basse (dernier lot traité) et borne haute (dernier lot disponible, figée maintenant)
last = datetime.fromisoformat(get_watermark(WM_KEY, "1970-01-01T00:00:00"))
bronze = spark.table(SRC)
upper = bronze.agg(F.max("_ingested_at")).collect()[0][0]

if upper is None or upper <= last:
    print("Rien de nouveau en Bronze.")
else:
    # 2. Lire UNIQUEMENT l'incrément
    inc = bronze.filter((F.col("_ingested_at") > F.lit(last)) & (F.col("_ingested_at") <= F.lit(upper)))

    num_cols = ["consommation", "nucleaire", "eolien", "solaire", "hydraulique",
                "gaz", "charbon", "fioul", "bioenergies", "taux_co2", "ech_physiques"]
    typed = inc.withColumn("date_heure", F.to_timestamp("date_heure"))
    for c in [c for c in num_cols if c in inc.columns]:
        typed = typed.withColumn(c, F.col(c).cast("double"))

    # 3. Séparer valides et rejets (règle : clé non nulle, consommation non négative)
    is_valid = F.col("date_heure").isNotNull() & F.coalesce(F.col("consommation") >= 0, F.lit(True))
    rejects = typed.filter(~is_valid)
    valid = typed.filter(is_valid)

    # 4. Dédoublonner dans l'incrément (garder l'ingestion la plus récente par clé)
    w = Window.partitionBy("date_heure").orderBy(F.col("_ingested_at").desc())
    dedup = valid.withColumn("_rn", F.row_number().over(w)).filter("_rn = 1").drop("_rn")

    # 5. MERGE idempotent : on ne remplace une ligne que si la source est plus récente
    if spark.catalog.tableExists(TGT):
        (DeltaTable.forName(spark, TGT).alias("t")
            .merge(dedup.alias("s"), "t.date_heure = s.date_heure")
            .whenMatchedUpdateAll(condition="s._ingested_at > t._ingested_at")
            .whenNotMatchedInsertAll().execute())
    else:
        dedup.write.format("delta").saveAsTable(TGT)

    rejects.withColumn("_rejected_at", F.current_timestamp()) \
           .write.format("delta").mode("append").saveAsTable("silver_eco2mix_rejects")

    # 6. Avancer le watermark en dernier
    set_watermark(WM_KEY, "_ingested_at", upper.isoformat())
    print(f"Silver éco2mix à jour jusqu'à {upper.isoformat()}")
