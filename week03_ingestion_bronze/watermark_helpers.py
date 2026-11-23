# Helpers de watermark (à mettre dans un notebook Fabric `nb_watermark_helpers`,
# puis appelé au début des autres notebooks avec la commande magique : %run nb_watermark_helpers)
#
# Un watermark = la dernière valeur traitée d'une colonne (date ou timestamp d'ingestion).
# Il est stocké dans la table de contrôle ops_watermarks, une ligne par table/étape.
from datetime import datetime, timezone
from delta.tables import DeltaTable
from pyspark.sql import functions as F

spark.conf.set("spark.sql.session.timeZone", "UTC")
WM_TABLE = "ops_watermarks"


def ensure_watermark_table():
    spark.sql(f"""
        CREATE TABLE IF NOT EXISTS {WM_TABLE} (
            table_name STRING,
            watermark_column STRING,
            last_value STRING,
            updated_at TIMESTAMP
        ) USING DELTA
    """)


def get_watermark(table_name, default):
    """Retourne la dernière valeur (ISO 8601, UTC) ou `default` si aucune."""
    ensure_watermark_table()
    rows = (spark.table(WM_TABLE)
            .filter(F.col("table_name") == table_name)
            .select("last_value").collect())
    return rows[0][0] if rows else default


def set_watermark(table_name, column, value):
    """Enregistre le watermark. À appeler UNIQUEMENT après l'écriture réussie."""
    ensure_watermark_table()
    df = spark.createDataFrame(
        [(table_name, column, str(value), datetime.now(timezone.utc))],
        "table_name string, watermark_column string, last_value string, updated_at timestamp",
    )
    (DeltaTable.forName(spark, WM_TABLE).alias("t")
        .merge(df.alias("s"), "t.table_name = s.table_name")
        .whenMatchedUpdateAll().whenNotMatchedInsertAll().execute())
