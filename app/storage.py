"""Where short links are saved.

With DATABASE_URL set, links go to PostgreSQL. Without it, they stay in
memory, which is enough for local development and tests.
"""

import os

import psycopg


class MemoryStore:
    def __init__(self):
        self.links: dict[str, str] = {}

    def save(self, code: str, url: str) -> None:
        self.links[code] = url

    def get(self, code: str) -> str | None:
        return self.links.get(code)


class PostgresStore:
    def __init__(self, database_url: str):
        self.database_url = database_url
        with psycopg.connect(self.database_url) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS links (code TEXT PRIMARY KEY, url TEXT NOT NULL)"
            )

    def save(self, code: str, url: str) -> None:
        # Parameters (%s) are sent separately from the SQL, which prevents SQL injection.
        with psycopg.connect(self.database_url) as conn:
            conn.execute("INSERT INTO links (code, url) VALUES (%s, %s)", (code, url))

    def get(self, code: str) -> str | None:
        with psycopg.connect(self.database_url) as conn:
            row = conn.execute("SELECT url FROM links WHERE code = %s", (code,)).fetchone()
        return row[0] if row else None


def create_store() -> MemoryStore | PostgresStore:
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return PostgresStore(database_url)
    return MemoryStore()
