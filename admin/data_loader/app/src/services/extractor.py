import sqlite3
from logging import getLogger
from typing import Any, Generator

from schemas import Model, Row
from services.exceptions import ExtractionError

logger = getLogger(__name__)


class SQLiteExtractor:
    def __init__(self, connection: sqlite3.Connection):
        self._conn = connection
        self._conn.row_factory = sqlite3.Row
        self._cursor = self._conn.cursor()

    def _get_select_query(self, table_name: str) -> str:
        query = """SELECT {columns} FROM {table_name}"""
        return query.format(
            table_name=table_name,
            columns="*",
        )

    def select_table(
        self,
        table: str,
        batch_size: int,
    ) -> Generator[list[tuple[Any]], None, None]:
        query = self._get_select_query(table)

        try:
            self._cursor.execute(query)
        except sqlite3.OperationalError as e:
            logger.exception(e)
            raise ExtractionError from e

        while data := self._cursor.fetchmany(batch_size):
            yield [self._deserialize(table, row) for row in data]

    def _deserialize(self, table_name: str, data) -> Model:
        data = {"table_name": table_name} | dict(data)
        return Row(model=data).model
