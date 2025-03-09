import sqlite3


class DbManager:
    def __enter__(self):
        self.conn = sqlite3.connect("database.db")
        self.conn.row_factory = sqlite3.Row
        return self


    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()


    def execute(self, query: str, params: tuple | None):
        with self.conn:
            self.conn.execute(query, params or ())


    def execute_fetchall(self, query: str, params: tuple | None):
        with self.conn:
            cursor = self.conn.execute(query, params or ())
        return cursor.fetchall()


    def execute_fetchone(self, query: str, params: tuple | None):
        with self.conn:
            cursor = self.conn.execute(query, params or ())
        return cursor.fetchone()
