from functools import cached_property, lru_cache
from logging import getLogger

from psycopg2.extensions import connection as _connection
from psycopg2.extras import execute_batch
from schemas import Model
from services.exceptions import LoadingError

logger = getLogger(__name__)


class PostgreSQLLoder:
    def __init__(self, pg_conn: _connection, schema: str) -> None:
        self._conn = pg_conn
        self._cursor = self._conn.cursor()
        self.schema = schema

    @cached_property
    def tables(self) -> list[str]:
        table_names = self._get_table_names()

        dependecies = {
            table_name: self._get_dependencies(table_name) for table_name in table_names
        }

        visited = set()
        result = []

        for table_name in table_names:
            if table_name not in visited:
                self._dfs(table_name, visited, dependecies, result)

        return result

    def _get_table_names(self) -> list[str]:
        try:
            self._cursor.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = '{}' AND table_type = 'BASE TABLE'
                """.format(
                    self.schema
                )
            )
        except Exception as e:
            logger.exception(e)
            raise LoadingError from e

        return [table_name for table_name, *_ in self._cursor.fetchall()]

    def _get_dependencies(self, table_name: str) -> list[str]:
        try:
            self._cursor.execute(
                """
                SELECT ccu.table_name AS foreign_table_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.constraint_column_usage AS ccu ON ccu.constraint_name = tc.constraint_name
                WHERE constraint_type = 'FOREIGN KEY' AND tc.table_name = '{table_name}' AND tc.table_schema = '{schema}'
                """.format(
                    table_name=table_name,
                    schema=self.schema,
                )
            )
        except Exception as e:
            logger.exception(e)
            raise LoadingError from e

        return [row[0] for row in self._cursor.fetchall()]

    @staticmethod
    def _dfs(node, visited, graph, result) -> None:
        visited.add(node)
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                PostgreSQLLoder._dfs(neighbor, visited, graph, result)
        result.append(node)

    @lru_cache
    def _create_insert_statement(self, table_name: str, columns: tuple[str]) -> str:
        query = """
        PREPARE {statement} AS
        INSERT INTO content.{table_name} ({column_names})
        VALUES ({values})
        ON CONFLICT (id) DO NOTHING
        """
        statement = table_name + "__insert"
        column_names = ", ".join(columns)
        values = ", ".join("${}".format(n + 1) for n in range(len(columns)))

        try:
            self._cursor.execute(
                query.format(
                    statement=statement,
                    table_name=table_name,
                    column_names=column_names,
                    values=values,
                )
            )
        except Exception as e:
            logger.exception(e)
            raise LoadingError from e

        return statement

    @lru_cache
    def _get_model_columns(self, model_class) -> tuple[str]:
        return tuple(
            field
            for field in model_class.model_fields
            if not model_class.model_fields[field].exclude
        )

    def _get_insert_query(self, table_name: str, model_class) -> str:
        columns = self._get_model_columns(model_class)
        statement = self._create_insert_statement(table_name, columns)

        query = """EXECUTE {statement}({values})""".format(
            statement=statement,
            values=", ".join("%s" for _ in range(len(columns))),
        )

        return query

    def load_batch(self, data: list[Model]) -> None:
        query = self._get_insert_query(data[0].table_name, data[0].__class__)
        tuples = [tuple(row.model_dump().values()) for row in data]

        try:
            execute_batch(self._cursor, query, tuples)
        except Exception as e:
            logger.exception(e)
            raise LoadingError from e

        self._conn.commit()
