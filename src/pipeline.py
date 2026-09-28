import time
from dataclasses import dataclass, field
from typing import Optional

from src.extract.downloader import extract_all
from src.load.loader import load_all
from src.metrics.aggregator import run_all_metrics
from src.transform.cleaner import transform_all
from src.transform.quality import run_quality_checks
from src.utils.db import test_connection
from src.utils.logger import get_logger

log = get_logger("pipeline")


@dataclass
class PipelineResult:
    success: bool
    duration_seconds: float
    extract_stats: dict = field(default_factory=dict)
    transform_stats: dict = field(default_factory=dict)
    load_stats: dict = field(default_factory=dict)
    quality_passed: bool = True
    metrics_stats: list = field(default_factory=list)
    error: Optional[str] = None


def run_pipeline(
    data_dir: str = "data/raw",
    batch_size: int = 10000,
    skip_quality_checks: bool = False,
) -> PipelineResult:
    """Execute full ETL pipeline: Extract → Transform → Quality Check → Load."""
    log.info("=" * 60)
    log.info("ECOMMERCE ETL PIPELINE STARTING")
    log.info("=" * 60)
    start_time = time.time()

    if not test_connection():
        return PipelineResult(
            success=False,
            duration_seconds=0,
            error="Database connection failed. Is PostgreSQL running? Try: docker-compose up -d",
        )

    try:
        # Extract
        log.info("[1/5] EXTRACT")
        raw_dataframes = extract_all(data_dir)
        extract_stats = {name: len(df) for name, df in raw_dataframes.items()}

        if not raw_dataframes:
            return PipelineResult(
                success=False,
                duration_seconds=time.time() - start_time,
                error="Extraction returned no data",
            )

        # Transform
        log.info("[2/5] TRANSFORM")
        cleaned_dataframes, transform_stats = transform_all(raw_dataframes)

        # Quality checks
        log.info("[3/5] QUALITY CHECKS")
        quality_passed = True
        if not skip_quality_checks:
            quality_results = run_quality_checks(cleaned_dataframes)
            quality_passed = all(r.passed for r in quality_results)
            if not quality_passed:
                failed = [r.dataset for r in quality_results if not r.passed]
                log.warning(f"Quality checks failed for: {failed}")

        # Load
        log.info("[4/5] LOAD")
        load_stats = load_all(cleaned_dataframes, batch_size=batch_size)

        # Metrics aggregation
        log.info("[5/5] METRICS")
        metrics_stats = run_all_metrics()

        duration = time.time() - start_time
        success = all(v["status"] == "success" for v in load_stats.values())

        log.info("=" * 60)
        log.info(f"PIPELINE {'SUCCEEDED' if success else 'COMPLETED WITH ERRORS'}")
        log.info(f"Duration: {duration:.1f}s")
        log.info("=" * 60)

        return PipelineResult(
            success=success,
            duration_seconds=round(duration, 2),
            extract_stats=extract_stats,
            transform_stats=transform_stats,
            load_stats=load_stats,
            quality_passed=quality_passed,
            metrics_stats=metrics_stats,
        )

    except Exception as e:
        duration = time.time() - start_time
        log.error(f"Pipeline failed: {e}")
        return PipelineResult(
            success=False,
            duration_seconds=round(duration, 2),
            error=str(e),
        )
