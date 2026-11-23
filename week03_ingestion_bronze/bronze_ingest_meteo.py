# Notebook Fabric : ingestion INCRÉMENTALE Open-Meteo -> Bronze
# %run nb_watermark_helpers
import json
import requests
from datetime import datetime, timezone, timedelta
from pyspark.sql import functions as F

spark.conf.set("spark.sql.session.timeZone", "UTC")

TABLE = "bronze_meteo_hourly"
LOOKBACK_HOURS = 3
DEFAULT_BACKFILL_DAYS = 7
URL = "https://api.open-meteo.com/v1/forecast"
BATCH_ID = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
now = datetime.now(timezone.utc).replace(tzinfo=None)

# --- Paramètre du pipeline ---
since_override = None

LOCATIONS = {
    "paris": (48.85, 2.35),
    "marseille": (43.30, 5.37),
    "lille": (50.63, 3.06),
    "bordeaux": (44.84, -0.58),
    "strasbourg": (48.58, 7.75),
}

wm = since_override or get_watermark(TABLE, (now - timedelta(days=DEFAULT_BACKFILL_DAYS)).isoformat())
start = datetime.fromisoformat(wm) - timedelta(hours=LOOKBACK_HOURS)
past_days = min(92, max(1, (now - start).days + 1))   # l'API limite l'historique à 92 jours
print(f"Watermark: {wm} | fenêtre: {start.isoformat()} -> {now.isoformat()}")

# Tout est collecté avant d'écrire : si une ville échoue, rien n'est écrit et le watermark n'avance pas.
records = []
for city, (lat, lon) in LOCATIONS.items():
    r = requests.get(URL, params={
        "latitude": lat, "longitude": lon,
        "hourly": "temperature_2m,wind_speed_10m,shortwave_radiation",
        "past_days": past_days, "forecast_days": 1, "timezone": "UTC",
    }, timeout=60)
    r.raise_for_status()
    h = r.json()["hourly"]
    for i, t in enumerate(h["time"]):
        ts = datetime.fromisoformat(t)
        if start < ts <= now:          # ni prévisions futures, ni heures déjà chargées
            records.append({
                "city": city, "time": t,
                "temperature_2m": h["temperature_2m"][i],
                "wind_speed_10m": h["wind_speed_10m"][i],
                "shortwave_radiation": h["shortwave_radiation"][i],
            })

if not records:
    print("Aucune nouvelle donnée, rien à écrire.")
else:
    df = (spark.read.json(spark.sparkContext.parallelize([json.dumps(r) for r in records]))
            .withColumn("_ingested_at", F.current_timestamp())
            .withColumn("_source", F.lit("open_meteo"))
            .withColumn("_batch_id", F.lit(BATCH_ID)))
    new_wm = max(datetime.fromisoformat(r["time"]) for r in records)
    df.write.format("delta").mode("append").saveAsTable(TABLE)
    set_watermark(TABLE, "time", new_wm.isoformat())
    print(f"{df.count()} lignes écrites, nouveau watermark: {new_wm.isoformat()}, batch {BATCH_ID}")
