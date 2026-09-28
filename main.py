#!/usr/bin/env python3
"""Entry point for the ecommerce ETL pipeline."""
import argparse
import sys

from dotenv import load_dotenv

load_dotenv()

from src.pipeline import run_pipeline
from src.utils.logger import get_logger

log = get_logger("main")


def parse_args():
    parser = argparse.ArgumentParser(description="Ecommerce ETL Pipeline")
    parser.add_argument("--data-dir", default="data/raw", help="Directory for raw data")
    parser.add_argument("--batch-size", type=int, default=10000, help="Rows per DB batch")
    parser.add_argument("--skip-quality", action="store_true", help="Skip data quality checks")
    return parser.parse_args()


def main():
    args = parse_args()
    result = run_pipeline(
        data_dir=args.data_dir,
        batch_size=args.batch_size,
        skip_quality_checks=args.skip_quality,
    )

    if result.success:
        log.info(f"Pipeline completed in {result.duration_seconds}s")
        sys.exit(0)
    else:
        log.error(f"Pipeline failed: {result.error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
