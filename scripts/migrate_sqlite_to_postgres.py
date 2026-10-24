#!/usr/bin/env python3
"""One-off copy of ReviewPilot data from SQLite file to PostgreSQL (schema via Alembic)."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

TABLE_ORDER = (
    "users",
    "promo_codes",
    "marketplace_accounts",
    "tone_profiles",
    "reviews",
    "generated_replies",
    "subscriptions",
    "promo_redemptions",
)


def _sync_url(database_url: str) -> str:
    url = database_url.strip()
    if url.startswith("postgresql+asyncpg://"):
        return "postgresql+psycopg2://" + url.split("postgresql+asyncpg://", 1)[1]
    if url.startswith("sqlite+aiosqlite:"):
        return "sqlite://" + url.split("sqlite+aiosqlite:", 1)[1]
    return url


def _boolean_columns(engine: Engine, table: str) -> set[str]:
    from sqlalchemy import inspect

    insp = inspect(engine)
    return {
        col["name"]
        for col in insp.get_columns(table)
        if str(col["type"]).upper().startswith("BOOLEAN")
    }


def _normalize_row(row: dict, bool_cols: set[str]) -> dict:
    out = dict(row)
    for col in bool_cols:
        if col in out and out[col] is not None:
            out[col] = bool(out[col])
    return out


def copy_table(src: Engine, dst: Engine, table: str) -> int:
    bool_cols = _boolean_columns(dst, table)
    with src.connect() as sconn, dst.connect() as dconn:
        rows = sconn.execute(text(f"SELECT * FROM {table}")).mappings().all()
        if not rows:
            return 0
        cols = list(rows[0].keys())
        col_list = ", ".join(cols)
        placeholders = ", ".join(f":{c}" for c in cols)
        insert = text(f"INSERT INTO {table} ({col_list}) VALUES ({placeholders})")
        for row in rows:
            dconn.execute(insert, _normalize_row(dict(row), bool_cols))
        dconn.commit()
        return len(rows)


def reset_sequences(dst: Engine) -> None:
    with dst.connect() as conn:
        for table in TABLE_ORDER:
            conn.execute(
                text(
                    f"""
                    SELECT setval(
                        pg_get_serial_sequence('{table}', 'id'),
                        COALESCE((SELECT MAX(id) FROM {table}), 1),
                        (SELECT COUNT(*) > 0 FROM {table})
                    )
                    """
                )
            )
        conn.commit()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--sqlite",
        default=str(ROOT / "reviewpilot.db"),
        help="Path to source SQLite file",
    )
    parser.add_argument(
        "--postgres-url",
        default=os.environ.get("DATABASE_URL", ""),
        help="Target DATABASE_URL (postgresql+asyncpg://…)",
    )
    args = parser.parse_args()
    if not args.postgres_url.strip():
        raise SystemExit("Set --postgres-url or DATABASE_URL")

    sqlite_path = Path(args.sqlite)
    if not sqlite_path.is_file():
        raise SystemExit(f"SQLite file not found: {sqlite_path}")

    src = create_engine(f"sqlite:///{sqlite_path.resolve()}")
    dst = create_engine(_sync_url(args.postgres_url))

    with dst.connect() as conn:
        for table in reversed(TABLE_ORDER):
            conn.execute(text(f"TRUNCATE {table} RESTART IDENTITY CASCADE"))
        conn.commit()

    total = 0
    for table in TABLE_ORDER:
        n = copy_table(src, dst, table)
        print(f"{table}: {n} rows")
        total += n
    reset_sequences(dst)
    print(f"Done. {total} rows copied.")


if __name__ == "__main__":
    main()
