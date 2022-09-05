import psycopg

from psycopg.rows import Row
from psycopg.connection import Connection

from beholder.catalog.base import BaseDataCatalog


class HiveDataCatalog(BaseDataCatalog):
    def __init__(self):
        super().__init__()

    def _get_client(self):
        conn: Connection = psycopg.connect("host=localhost port=5432 dbname=hive")
        rs: list[Row] = conn.execute('SELECT * FROM "VERSION"').fetchall()
        if not rs:
            raise Exception("VERSION table not found in host, is the hive metastore initialized?")
        return conn

    def get_table_by_name(self, db: str, table: str):
        query = """
            
        """

    def get_table_by_location(self, db: str, table: str):
        pass

    def get_table_partition_keys(self, db: str, table: str):
        pass
