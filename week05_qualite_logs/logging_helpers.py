# Helpers de journalisation à importer dans les notebooks (%run ou module)
from datetime import datetime, timezone
import traceback

def log_run(run_id, pipeline, notebook, status, rows_read=0, rows_written=0,
            rows_rejected=0, error=None, started_at=None):
    row = [(run_id, pipeline, notebook, status, rows_read, rows_written,
            rows_rejected, error, started_at or datetime.now(timezone.utc),
            datetime.now(timezone.utc))]
    cols = ["run_id", "pipeline_name", "notebook_name", "status", "rows_read",
            "rows_written", "rows_rejected", "error_message", "started_at", "ended_at"]
    spark.createDataFrame(row, cols).write.format("delta").mode("append") \
         .saveAsTable("ops_pipeline_runs")

def run_with_logging(run_id, pipeline, notebook, fn):
    """Exécute fn(), journalise le succès ou l'échec, relance l'exception."""
    started = datetime.now(timezone.utc)
    try:
        stats = fn() or {}
        log_run(run_id, pipeline, notebook, "SUCCESS", started_at=started, **stats)
    except Exception:
        log_run(run_id, pipeline, notebook, "FAILED",
                error=traceback.format_exc()[:4000], started_at=started)
        raise
