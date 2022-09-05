import abc


class BaseDataCatalog:
    def __init__(self):
        pass
        self.client = self._get_client()

    def _get_client(self):
        pass

    @abc.abstractmethod
    def get_table_by_name(self, db: str, table: str):
        pass

    @abc.abstractmethod
    def get_table_by_location(self, db: str, table: str):
        pass

    @abc.abstractmethod
    def get_table_partition_keys(self, db: str, table: str):
        pass
