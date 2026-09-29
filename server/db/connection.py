import os
from typing import Generator
import psycopg2
import psycopg2.extensions
from server.utils.logger import get_logger

logger = get_logger(__name__)

def get_db_connection() -> Generator[psycopg2.extensions.connection, None, None]:
    """Dependency that provides a postgres connection"""
    conn = None
    try:
        conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST'),
            port=os.getenv('POSTGRES_PORT'),
            dbname=os.getenv('POSTGRES_DB'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD')
        )
        yield conn
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()
