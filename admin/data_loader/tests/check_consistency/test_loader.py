import pytest


@pytest.mark.parametrize(
    "table_name",
    ["genre", "person", "film_work", "genre_film_work", "person_film_work"],
)
def test_records_count(sqlite_cursor, pg_cursor, table_name):
    query = """SELECT COUNT(*) FROM {}""".format(table_name)

    sqlite_cursor.execute(query)
    pg_cursor.execute(query)

    assert sqlite_cursor.fetchone()[0] == pg_cursor.fetchone()[0]


@pytest.mark.parametrize(
    "table_name",
    ["genre", "person", "film_work", "genre_film_work", "person_film_work"],
)
def test_values(sqlite_cursor, pg_cursor, table_name):
    get_columns_query = """SELECT column_name FROM information_schema.columns WHERE table_name = '{}'""".format(
        table_name
    )
    pg_cursor.execute(get_columns_query)
    columns = ", ".join(
        row[0]
        for row in pg_cursor.fetchall()
        if row[0] not in ["created_at", "updated_at"]
    )

    query = """SELECT {} FROM {}""".format(columns, table_name)

    sqlite_cursor.execute(query)
    pg_cursor.execute(query)

    assert set(sqlite_cursor.fetchall()) == set(pg_cursor.fetchall())
