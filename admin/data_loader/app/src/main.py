import sqlite3
from contextlib import closing

import click
import psycopg2
from psycopg2.extensions import connection as _connection
from services import PostgreSQLLoder, SQLiteExtractor

# TODO: это все нужно переделать в Django-команду и добавить в Makefile


def load_from_sqlite(
    connection: sqlite3.Connection,
    pg_conn: _connection,
    batch_size: int,
) -> None:
    """Основной метод загрузки данных из SQLite в Postgres"""

    loader = PostgreSQLLoder(pg_conn, "content")
    extractor = SQLiteExtractor(connection)

    for table in loader.tables:
        for batch in extractor.select_table(table, batch_size):
            loader.load_batch(batch)


@click.command()
@click.option("--path", required=True, help="Path to sqlite file")
@click.option("--db", required=True, help="Database name")
@click.option("--user", required=True, help="Database user")
@click.option("--password", required=True, help="Database password")
@click.option("--host", default="127.0.0.1", help="Database host")
@click.option("--port", default=5454, help="Database port")
@click.option("--batch_size", default=1000, help="Batch size")
def run(
    path: str,
    db: str,
    user: str,
    password: str,
    host: str,
    port: int,
    batch_size: int,
):
    dsl = {
        "dbname": db,
        "user": user,
        "password": password,
        "host": host,
        "port": port,
    }
    with closing(sqlite3.connect(path)) as sqlite_conn, closing(
        psycopg2.connect(**dsl)
    ) as pg_conn:
        load_from_sqlite(sqlite_conn, pg_conn, batch_size)


if __name__ == "__main__":
    run()
