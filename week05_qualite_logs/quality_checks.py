# Contrôles qualité sur Silver ; les résultats vont dans ops_quality_results
from datetime import datetime, timezone
from pyspark.sql import functions as F

def record(run_id, table, check, passed, details=""):
    spark.createDataFrame(
        [(run_id, table, check, bool(passed), details, datetime.now(timezone.utc))],
        ["run_id", "table_name", "check_name", "passed", "details", "checked_at"]
    ).write.format("delta").mode("append").saveAsTable("ops_quality_results")

def run_checks(run_id):
    df = spark.table("silver_eco2mix")

    # 1. Pas de doublons sur la clé
    dups = df.groupBy("date_heure").count().filter("count > 1").count()
    record(run_id, "silver_eco2mix", "no_duplicate_key", dups == 0, f"{dups} doublons")

    # 2. Taux de nulls sur la consommation < 5 %
    total = df.count()
    nulls = df.filter(F.col("consommation").isNull()).count()
    ratio = nulls / total if total else 1
    record(run_id, "silver_eco2mix", "consommation_null_ratio_lt_5pct", ratio < 0.05, f"{ratio:.2%}")

    # 3. Fraîcheur : dernière donnée de moins de 6 h
    last = df.agg(F.max("date_heure")).collect()[0][0]
    age_h = (datetime.now() - last).total_seconds() / 3600 if last else 9999
    record(run_id, "silver_eco2mix", "freshness_lt_6h", age_h < 6, f"{age_h:.1f} h")

    # 4. Plage de valeurs : taux de CO2 entre 0 et 200 g/kWh
    if "taux_co2" in df.columns:
        bad = df.filter(~F.col("taux_co2").between(0, 200)).count()
        record(run_id, "silver_eco2mix", "co2_in_range", bad == 0, f"{bad} hors plage")
