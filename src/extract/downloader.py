import time
from pathlib import Path
from typing import Optional

import pandas as pd
import requests
from tqdm import tqdm

from src.utils.logger import get_logger

log = get_logger("extractor")

OLIST_DATASETS = {
    "orders": "https://raw.githubusercontent.com/ruthwiksai9/ecommerce-etl-pipeline/main/data/raw/olist_orders_dataset.csv",
    "order_items": "https://raw.githubusercontent.com/ruthwiksai9/ecommerce-etl-pipeline/main/data/raw/olist_order_items_dataset.csv",
    "customers": "https://raw.githubusercontent.com/ruthwiksai9/ecommerce-etl-pipeline/main/data/raw/olist_customers_dataset.csv",
    "products": "https://raw.githubusercontent.com/ruthwiksai9/ecommerce-etl-pipeline/main/data/raw/olist_products_dataset.csv",
    "sellers": "https://raw.githubusercontent.com/ruthwiksai9/ecommerce-etl-pipeline/main/data/raw/olist_sellers_dataset.csv",
    "order_payments": "https://raw.githubusercontent.com/ruthwiksai9/ecommerce-etl-pipeline/main/data/raw/olist_order_payments_dataset.csv",
    "order_reviews": "https://raw.githubusercontent.com/ruthwiksai9/ecommerce-etl-pipeline/main/data/raw/olist_order_reviews_dataset.csv",
    "geolocation": "https://raw.githubusercontent.com/ruthwiksai9/ecommerce-etl-pipeline/main/data/raw/olist_geolocation_dataset.csv",
}

KAGGLE_URLS = {
    "orders": "https://storage.googleapis.com/kaggle-data-sets/55151/105464/bundle/archive.zip",
}


def download_olist_data(output_dir: str = "data/raw", max_retries: int = 3) -> dict:
    """Download Olist e-commerce dataset from public source."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    downloaded = {}

    datasets_url = {
        "orders": "https://raw.githubusercontent.com/erkansirin78/datasets/master/olist_orders_dataset.csv",
        "order_items": "https://raw.githubusercontent.com/erkansirin78/datasets/master/olist_order_items_dataset.csv",
        "customers": "https://raw.githubusercontent.com/erkansirin78/datasets/master/olist_customers_dataset.csv",
        "products": "https://raw.githubusercontent.com/erkansirin78/datasets/master/olist_products_dataset.csv",
        "sellers": "https://raw.githubusercontent.com/erkansirin78/datasets/master/olist_sellers_dataset.csv",
        "order_payments": "https://raw.githubusercontent.com/erkansirin78/datasets/master/olist_order_payments_dataset.csv",
    }

    for name, url in tqdm(datasets_url.items(), desc="Downloading datasets"):
        output_path = Path(output_dir) / f"{name}.csv"
        if output_path.exists():
            log.info(f"Dataset {name} already exists, skipping download")
            downloaded[name] = str(output_path)
            continue

        for attempt in range(max_retries):
            try:
                log.info(f"Downloading {name} (attempt {attempt + 1})")
                response = requests.get(url, timeout=30, stream=True)
                response.raise_for_status()
                with open(output_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                downloaded[name] = str(output_path)
                log.info(f"Downloaded {name} -> {output_path}")
                break
            except requests.RequestException as e:
                log.warning(f"Attempt {attempt + 1} failed for {name}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    log.error(f"Failed to download {name} after {max_retries} attempts")

    return downloaded


def load_csv(filepath: str, dtype: Optional[dict] = None) -> pd.DataFrame:
    """Load CSV with validation."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {filepath}")

    df = pd.read_csv(filepath, dtype=dtype, low_memory=False)
    log.info(f"Loaded {filepath}: {len(df):,} rows, {len(df.columns)} columns")
    return df


def extract_all(data_dir: str = "data/raw") -> dict:
    """Extract all datasets, return dict of DataFrames."""
    log.info("Starting extraction phase")
    downloaded = download_olist_data(data_dir)

    dataframes = {}
    for name, filepath in downloaded.items():
        try:
            dataframes[name] = load_csv(filepath)
        except Exception as e:
            log.error(f"Failed to load {name}: {e}")

    log.info(f"Extraction complete: {len(dataframes)} datasets loaded")
    return dataframes
