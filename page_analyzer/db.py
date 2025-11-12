import psycopg2
import psycopg2.extensions
from psycopg2.extras import RealDictCursor
from typing import Optional, Dict, Any
from .date import URL, URLCheck


def get_db(app) -> psycopg2.extensions.connection:
    return psycopg2.connect(app.config["DATABASE_URL"])


class Url_Repository:
    def __init__(self, conn: psycopg2.extensions.connection):
        self.conn = conn

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def get_url_by_name(self, name: str) -> Optional[URL]:
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM urls WHERE name = %s", (name,))
            row = cur.fetchone()
            return URL(**row) if row else None

    def create_url(self, name: str) -> Optional[Dict]:
        url_obj = URL(name)
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO urls (name, created_at)
                VALUES (%s, %s)
                RETURNING id""",
                (url_obj.name, url_obj.created_at),
            )
            res = cur.fetchone()
            url_obj.id = res["id"]
            self.conn.commit()
        return url_obj

    def get_url_by_id(self, url_id):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM urls WHERE id = %s", (url_id,))
            row = cur.fetchone()
            self.conn.commit()
            return URL(**row) if row else None

    def get_checks_for_urls(self, url_id):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM url_checks")
            return [URLCheck(**row) for row in cur]
