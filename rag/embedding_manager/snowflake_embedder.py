from __future__ import annotations

import json
import os
from typing import Optional

import snowflake.connector


class EmbeddingManager:
    """Generates embeddings via Snowflake Cortex. Manages its own connection lifecycle."""

    _RECONNECT_EVERY = 50

    def __init__(self, model: str, dimension: int) -> None:
        self._model = model
        self._dimension = dimension
        self._conn: Optional[snowflake.connector.SnowflakeConnection] = None
        self._call_count = 0

    # ── Public API ──

    def embed_text(self, text: str) -> list[float]:
        """Generate embedding for a single text string."""
        self._call_count += 1
        if self._call_count % self._RECONNECT_EVERY == 0:
            self._refresh_connection()

        conn = self._get_connection()
        query = f"SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_{self._dimension}(%s, %s)"

        cursor = conn.cursor()
        try:
            cursor.execute(query, (self._model, text))
            result = cursor.fetchone()[0]
            return self._parse_embedding(result)
        except Exception as e:
            if "Session no longer exists" in str(e) or "session" in str(e).lower():
                print("    [Auth] Session expired. Refreshing connection...")
                self._refresh_connection()
                cursor = self._get_connection().cursor()
                try:
                    cursor.execute(query, (self._model, text))
                    result = cursor.fetchone()[0]
                    return self._parse_embedding(result)
                finally:
                    cursor.close()
            raise
        finally:
            cursor.close()

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts."""
        return [self.embed_text(t) for t in texts]

    def close(self) -> None:
        """Close the Snowflake connection."""
        if self._conn is not None:
            try:
                self._conn.close()
            except Exception:
                pass
            self._conn = None

    # ── Connection Management ──

    def _get_connection(self) -> snowflake.connector.SnowflakeConnection:
        if self._conn is None:
            self._conn = self._create_connection()
        return self._conn

    def _create_connection(self) -> snowflake.connector.SnowflakeConnection:
        conn = snowflake.connector.connect(
            user=os.getenv("SNOWFLAKE_USER"),
            password=os.getenv("SNOWFLAKE_PASSWORD"),
            account=os.getenv("SNOWFLAKE_ACCOUNT"),
            passcode="987043"
        )

        cursor = conn.cursor()
        warehouse = os.getenv("SNOWFLAKE_WAREHOUSE")
        database = os.getenv("SNOWFLAKE_DATABASE")
        schema = os.getenv("SNOWFLAKE_SCHEMA")

        if warehouse:
            try:
                cursor.execute(f"CREATE WAREHOUSE IF NOT EXISTS {warehouse}")
            except Exception:
                pass
            cursor.execute(f"USE WAREHOUSE {warehouse}")
        if database:
            try:
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
            except Exception:
                pass
            cursor.execute(f"USE DATABASE {database}")
        if schema:
            try:
                cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
            except Exception:
                pass
            cursor.execute(f"USE SCHEMA {schema}")

        cursor.close()
        return conn

    def _refresh_connection(self) -> None:
        if self._conn is not None:
            try:
                self._conn.close()
            except Exception:
                pass
        self._conn = self._create_connection()

    # ── Parsing ──

    @staticmethod
    def _parse_embedding(raw) -> list[float]:
        if isinstance(raw, list):
            return [float(x) for x in raw]
        if isinstance(raw, str):
            parsed = json.loads(raw)
            return [float(x) for x in parsed]
        return [float(x) for x in raw]
