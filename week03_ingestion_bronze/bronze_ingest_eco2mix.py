# Notebook Fabric : ingestion INCRÉMENTALE éco2mix -> Bronze
# Source : ODRE (Opendatasoft), jeu de données eco2mix-national-tr
# Avant de lancer : vérifie le nom du dataset, les champs et la syntaxe du filtre `where`
# sur https://odre.opendatasoft.com (la syntaxe date'...' est à confirmer).
#
# %run nb_watermark_helpers
import json
import requests
from datetime import datetime, timezone, timedelta
from pyspark.sql import functions as F

spark.conf.set("spark.sql.session.timeZone", "UTC")

TABLE = "bronze_rte_eco2mix"
LOOKBACK_HOURS = 3          # relit un peu en arrière pour rattraper les données tardives
DEFAULT_BACKFILL_DAYS = 30  # premier chargement : 30 jours seulement (protège la capacité)

# --- Paramètres du pipeline (cellule « paramètres » du notebook) ---
since_override = None       # ex. "2026-11-01T00:00:00" pour un backfill manuel

BASE = "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/eco2mix-national-tr/exports/json"
BATCH_ID = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
now = datetime.now(timezone.utc).replace(tzinfo=None)

# 1. Lire le watermark (dernière date_heure chargée)
wm = since_override or get_watermark(TABLE, (now - timedelta(days=DEFAULT_BACKFILL_DAYS)).isoformat())
start = datetime.fromisoformat(wm) - timedelta(hours=LOOKBACK_HOURS)
print(f"Watermark: {wm} | extraction depuis: {start.isoformat()}")

# 2. Extraire uniquement la fenêtre utile
params = {
    "where": f"date_heure >= date'{start.strftime('%Y-%m-%dT%H:%M:%SZ')}'",
    "order_by": "date_heure",
    "limit": -1,
}
resp = requests.get(BASE, params=params, timeout=120)
resp.raise_for_status()
rows = resp.json()

if not rows:
    print("Aucune nouvelle donnée, rien à écrire.")
else:
    df = spark.read.json(spark.sparkContext.parallelize([json.dumps(r) for r in rows]))
    df = (df.withColumn("_ingested_at", F.current_timestamp())
            .withColumn("_source", F.lit("odre_eco2mix_national_tr"))
            .withColumn("_batch_id", F.lit(BATCH_ID)))

    new_wm = df.agg(F.max(F.to_timestamp("date_heure"))).collect()[0][0]

    # 3. Écrire (append, Bronze reste brut : les doublons de la fenêtre de recouvrement
    #    sont éliminés en Silver)
    df.write.format("delta").mode("append").saveAsTable(TABLE)

    # 4. Avancer le watermark APRÈS l'écriture réussie (au pire, on relit : at-least-once)
    set_watermark(TABLE, "date_heure", new_wm.isoformat())
    print(f"{df.count()} lignes écrites, nouveau watermark: {new_wm.isoformat()}, batch {BATCH_ID}")
