# Ecommerce ETL Pipeline

[![CI](https://github.com/ruthwiksai9/ecommerce-etl-pipeline/actions/workflows/ci.yml/badge.svg)](https://github.com/ruthwiksai9/ecommerce-etl-pipeline/actions/workflows/ci.yml)

End-to-end Python ETL pipeline that ingests Brazilian e-commerce data (Olist dataset), applies transformations and data quality checks, and loads into a PostgreSQL data warehouse with a star schema.

## Architecture

```
┌─────────────┐    ┌──────────────┐    ┌───────────────┐    ┌──────────────┐
│   Extract   │───▶│  Transform   │───▶│ Quality Check │───▶│    Load      │
│  (CSV/HTTP) │    │  (Pandas)    │    │  (custom DQ)  │    │ (PostgreSQL) │
└─────────────┘    └──────────────┘    └───────────────┘    └──────────────┘
```

**Raw Layer** → staging tables mirror source schema  
**Warehouse Layer** → star schema: `fact_orders`, `fact_order_items` + 4 dimension tables  
**Metrics Layer** → aggregated reporting tables

## Tech Stack

| Layer | Tool |
|-------|------|
| Language | Python 3.12 |
| Transformation | Pandas |
| Database | PostgreSQL 15 |
| Containerization | Docker + Docker Compose |
| Testing | pytest |
| Logging | Loguru |

## Dataset

[Brazilian E-Commerce (Olist)](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) — 100k orders, 9 tables, real retail data from 2016–2018.

## Quickstart

```bash
# 1. Clone and set up environment
git clone https://github.com/ruthwiksai9/ecommerce-etl-pipeline.git
cd ecommerce-etl-pipeline
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env

# 3. Start PostgreSQL
docker-compose up -d

# 4. Run pipeline
python main.py

# 5. Run tests
pytest tests/ -v --cov=src
```

## Project Structure

```
ecommerce-etl-pipeline/
├── src/
│   ├── extract/        # Data ingestion from HTTP sources
│   ├── transform/      # Pandas transformations + DQ checks
│   ├── load/           # PostgreSQL loaders (batch + upsert)
│   └── utils/          # DB connections, logging
├── sql/
│   └── schema/         # SQL DDL: staging, star schema, indexes
├── tests/              # Unit tests (pytest)
├── config/             # Pipeline configuration (YAML)
├── data/raw/           # Downloaded source files (gitignored)
├── logs/               # Pipeline run logs (gitignored)
├── docker-compose.yml  # PostgreSQL container
├── main.py             # CLI entry point
└── requirements.txt
```

## Data Quality Checks

- **Null checks** — critical columns below configurable threshold (default 5%)
- **Duplicate detection** — primary key uniqueness enforcement
- **Referential integrity** — FK validation before warehouse load
- **Value range validation** — price/freight non-negative constraints

## Star Schema

```
                    ┌──────────────┐
                    │  dim_date    │
                    └──────┬───────┘
                           │
┌───────────────┐    ┌─────┴──────┐    ┌──────────────┐
│ dim_customers │────│ fact_orders│────│ dim_products │
└───────────────┘    └─────┬──────┘    └──────────────┘
                           │
                    ┌──────┴───────┐
                    │  dim_sellers │
                    └──────────────┘
```

## CLI Options

```bash
python main.py --help
python main.py --batch-size 5000          # smaller batches
python main.py --skip-quality             # skip DQ checks
python main.py --data-dir /path/to/data   # custom data directory
```
