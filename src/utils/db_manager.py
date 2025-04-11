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
            CREATE TABLE IF NOT EXISTS reaction_role_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dc_guild_id VARCHAR(255),
                dc_channel_id VARCHAR(255),
                dc_message_id VARCHAR(255),
                type VARCHAR(255),
                message TEXT
            )
            """
        )

        db.execute(query="""
            CREATE TABLE IF NOT EXISTS reaction_roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reaction_role_messages_id INTEGER,
                emoji TEXT,
                dc_role_id VARCHAR(255)
            )
            """
        )

        db.execute(query="""
            CREATE TABLE IF NOT EXISTS welcome_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dc_guild_id VARCHAR(255) NOT NULL UNIQUE,
                dc_channel_id VARCHAR(255) NOT NULL UNIQUE,
                message TEXT NOT NULL
            )
            """
        )

        db.execute(query="""
            CREATE TABLE IF NOT EXISTS auto_roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dc_guild_id VARCHAR(255) NOT NULL
            )
            """
        )

        db.execute(query="""
            CREATE TABLE IF NOT EXISTS auto_roles_roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reaction_role_messages_id INTEGER NOT NULL,
                dc_role_id VARCHAR(255) NOT NULL
            )
            """
        )

        db.execute(query="""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id VARCHAR(255) NOT NULL,
                user_id VARCHAR(255) NOT NULL,
                action TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        db.execute(query="""
            CREATE TABLE IF NOT EXISTS users (
                id VARCHAR(255) NOT NULL UNIQUE,
                username VARCHAR(255) NOT NULL,
                avatar VARCHAR(255)
            )
            """
        )

        db.execute(query="""
            CREATE TABLE IF NOT EXISTS guilds (
                id VARCHAR(255) NOT NULL UNIQUE,
                name VARCHAR(255) NOT NULL,
                icon VARCHAR(255),
                bot_joined INTEGER NOT NULL CHECK (bot_joined IN (0, 1))
            )
            """
        )

        db.execute(query="""
            CREATE TABLE IF NOT EXISTS sessions (
                id VARCHAR(255) NOT NULL UNIQUE,
                user_id VARCHAR(255) NOT NULL,
                session_expire_timestamp TIMESTAMP NOT NULL,
                access_token VARCHAR(255),
                access_token_expire_timestamp TIMESTAMP NOT NULL
            )
            """
        )

        db.execute(query="""
            CREATE TABLE IF NOT EXISTS sessions_guilds_map (
                session_id VARCHAR(255) NOT NULL,
                guild_id VARCHAR(255) NOT NULL
            )
            """
        )
