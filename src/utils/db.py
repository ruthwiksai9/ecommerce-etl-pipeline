import os
from contextlib import contextmanager
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from src.utils.logger import get_logger

load_dotenv()
log = get_logger("db")


def get_connection_string() -> str:
    return (
        f"postgresql+psycopg2://"
        f"{os.getenv('POSTGRES_USER', 'etl_user')}:"
        f"{os.getenv('POSTGRES_PASSWORD', 'etl_password')}@"
        f"{os.getenv('POSTGRES_HOST', 'localhost')}:"
        f"{os.getenv('POSTGRES_PORT', '5432')}/"
        f"{os.getenv('POSTGRES_DB', 'ecommerce_dw')}"
    )


def get_engine(pool_size: int = 5, max_overflow: int = 10):
    return create_engine(
        get_connection_string(),
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_pre_ping=True,
    )


@contextmanager
def get_session() -> Generator[Session, None, None]:
    engine = get_engine()
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        log.error(f"Session rollback due to: {e}")
        raise
    finally:
        session.close()


def test_connection() -> bool:
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        log.info("Database connection successful")
        return True
    except Exception as e:
        log.error(f"Database connection failed: {e}")
        return False
