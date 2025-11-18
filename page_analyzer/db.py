from typing import Optional

import psycopg2
import psycopg2.extensions
from psycopg2.extras import RealDictCursor

from page_analyzer.date import URL, URLCheck


def get_db(app) -> psycopg2.extensions.connection:
    return psycopg2.connect(app.config["DATABASE_URL"])


class UrlRepository:
    def __init__(self, conn: psycopg2.extensions.connection):
        self._conn = conn

    @property
    def conn(self) -> psycopg2.extensions.connection:
        if self._conn is None:
            raise ValueError("Database connection is closed")
        return self._conn

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None

    def get_url_by_name(self, name: str) -> Optional[URL]:
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM urls WHERE name = %s", (name,))
            row = cur.fetchone()
            if row:
                url = URL(name=row["name"], id=row["id"])
                url.created_at = row["created_at"]
                return url
            return None

    def create_url(self, name: str) -> Optional[URL]:
        url_obj = URL(name)
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO urls (name)
                VALUES (%s)
                RETURNING id""",
                (url_obj.name,),
            )
            res = cur.fetchone()
            if res is None:
                raise RuntimeError("Failed to insert URL: no returning ID")
            url_obj.id = res["id"]
            self.conn.commit()
        return url_obj

    def get_url_by_id(self, url_id):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM urls WHERE id = %s", (url_id,))
            row = cur.fetchone()
            if row:
                url = URL(name=row["name"], id=row["id"])
                url.created_at = row["created_at"]
                return url
            return None

    def get_checks_for_url(self, url_id):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """SELECT *
                        FROM url_checks
                        WHERE url_id = %s
                        ORDER BY id DESC
                        """,
                (url_id,),
            )
            rows = cur.fetchall()
            if rows:
                urlcheck = []
                for row in rows:
                    created_at = row["created_at"]
                    del row["created_at"]
                    check = URLCheck(**row)
                    check.created_at = created_at
                    urlcheck.append(check)
                return urlcheck
            return None

    def create_url_check(self, url_check):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """INSERT INTO url_checks (
                        url_id, status_code, h1, title,
                        description)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING id""",
                (
                    url_check.url_id,
                    url_check.status_code,
                    url_check.h1,
                    url_check.title,
                    url_check.description,
                ),
            )
            res = cur.fetchone()
            if res is None:
                raise RuntimeError(
                    "Failed to insert URL check: no returning ID"
                )
            url_check.id = res["id"]
            self.conn.commit()
        return url_check

    def get_all_urls(self):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM urls ORDER BY id DESC")
            return [URL(**row) for row in cur]

    def get_all_checks(self):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM url_checks ORDER BY id DESC")
            return [URLCheck(**row) for row in cur]

    def get_urls_list(self):
        sql = """
        SELECT
            u.id,
            u.name,
            uc.created_at AS last_check_created_at,
            uc.status_code
        FROM urls AS u
        LEFT JOIN (
        SELECT
            url_id,
            created_at,
            status_code,
            ROW_NUMBER() OVER (
            PARTITION BY url_id ORDER BY created_at DESC
            ) AS rn
        FROM url_checks) 
        AS uc ON u.id = uc.url_id AND uc.rn = 1
        ORDER BY last_check_created_at DESC NULLS LAST"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql)
            urls = cur.fetchall()
        return urls
