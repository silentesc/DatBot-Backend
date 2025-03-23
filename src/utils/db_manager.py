import sqlite3


class DbManager:
    def __enter__(self):
        self.conn = sqlite3.connect("database.db")
        self.conn.row_factory = sqlite3.Row
        return self


    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.commit()
        self.conn.close()


    def execute(self, query: str, params: tuple = ()):
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        cursor.close()


    def execute_fetchall(self, query: str, params: tuple = ()):
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        result = cursor.fetchall()
        cursor.close()
        return result


    def execute_fetchone(self, query: str, params: tuple = ()):
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        result = cursor.fetchone()
        cursor.close()
        return result


if __name__ == "__main__":
    with DbManager() as db:
        db.execute(query="""
            CREATE TABLE reaction_role_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dc_guild_id VARCHAR(255),
                dc_channel_id VARCHAR(255),
                dc_message_id VARCHAR(255),
                message TEXT
            )
            """
        )

        db.execute(query="""
            CREATE TABLE reaction_roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reaction_role_messages_id INTEGER,
                emoji TEXT,
                dc_role_id VARCHAR(255)
            )
            """
        )
