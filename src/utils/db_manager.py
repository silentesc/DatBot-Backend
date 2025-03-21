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
        with self.conn:
            self.conn.execute(query, params)


    def execute_fetchall(self, query: str, params: tuple = ()):
        with self.conn:
            cursor = self.conn.execute(query, params)
        return cursor.fetchall()


    def execute_fetchone(self, query: str, params: tuple = ()):
        with self.conn:
            cursor = self.conn.execute(query, params)
        return cursor.fetchone()


if __name__ == "__main__":
    with DbManager() as db:
        db.execute(query="""
            CREATE TABLE reaction_role_emoji_roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                emoji IDK,
                dc_role_id VARCHAR(255)
            )
            """
        )
        
        db.execute(query="""
            CREATE TABLE reaction_role_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                db_guild_id VARCHAR(255),
                db_role_id VARCHAR(255),
                message TEXT
            )
            """
        )

        db.execute(query="""
            CREATE TABLE reaction_roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reaction_role_messages_id INTEGER,
                reaction_role_emoji_roles_id INTEGER
            )
            """
        )
