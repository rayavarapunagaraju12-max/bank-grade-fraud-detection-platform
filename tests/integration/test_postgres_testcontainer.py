import pytest
from sqlalchemy import create_engine, text
from testcontainers.postgres import PostgresContainer


@pytest.mark.integration
def test_postgres_testcontainer_round_trip() -> None:
    with PostgresContainer("postgres:16-alpine") as postgres:
        engine = create_engine(postgres.get_connection_url(driver="psycopg"))
        with engine.begin() as conn:
            conn.execute(text("CREATE TABLE smoke (id int primary key, name text)"))
            conn.execute(text("INSERT INTO smoke VALUES (1, 'ok')"))
            row = conn.execute(text("SELECT name FROM smoke WHERE id = 1")).scalar_one()
        assert row == "ok"
