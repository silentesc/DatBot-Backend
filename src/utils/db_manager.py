import aiosqlite
import asyncio


class DbManager:
    async def __aenter__(self):
        self.conn = await aiosqlite.connect("database.db")
        self.conn.row_factory = aiosqlite.Row
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.conn.commit()
        await self.conn.close()

    async def execute(self, query: str, params: tuple = ()):
        cursor = await self.conn.execute(query, params)
        await cursor.close()

    async def execute_fetchall(self, query: str, params: tuple = ()):
        cursor = await self.conn.execute(query, params)
        result = await cursor.fetchall()
        await cursor.close()
        return result

    async def execute_fetchone(self, query: str, params: tuple = ()):
        cursor = await self.conn.execute(query, params)
        result = await cursor.fetchone()
        await cursor.close()
        return result


if __name__ == "__main__":
    async def main():
        async with DbManager() as db:
            await db.execute(query="""
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

            await db.execute(query="""
                CREATE TABLE IF NOT EXISTS reaction_roles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    reaction_role_messages_id INTEGER,
                    emoji TEXT,
                    dc_role_id VARCHAR(255)
                )
                """
            )

            await db.execute(query="""
                CREATE TABLE IF NOT EXISTS welcome_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dc_guild_id VARCHAR(255) NOT NULL UNIQUE,
                    dc_channel_id VARCHAR(255) NOT NULL UNIQUE,
                    message TEXT NOT NULL
                )
                """
            )

            await db.execute(query="""
                CREATE TABLE IF NOT EXISTS auto_roles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dc_guild_id VARCHAR(255) NOT NULL
                )
                """
            )

            await db.execute(query="""
                CREATE TABLE IF NOT EXISTS auto_roles_roles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    reaction_role_messages_id INTEGER NOT NULL,
                    dc_role_id VARCHAR(255) NOT NULL
                )
                """
            )

            await db.execute(query="""
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id VARCHAR(255) NOT NULL,
                    user_id VARCHAR(255) NOT NULL,
                    action TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            await db.execute(query="""
                CREATE TABLE IF NOT EXISTS users (
                    id VARCHAR(255) NOT NULL UNIQUE,
                    username VARCHAR(255) NOT NULL,
                    avatar VARCHAR(255)
                )
                """
            )

            await db.execute(query="""
                CREATE TABLE IF NOT EXISTS guilds (
                    id VARCHAR(255) NOT NULL UNIQUE,
                    name VARCHAR(255) NOT NULL,
                    icon VARCHAR(255),
                    bot_joined INTEGER NOT NULL CHECK (bot_joined IN (0, 1))
                )
                """
            )

            await db.execute(query="""
                CREATE TABLE IF NOT EXISTS sessions (
                    id VARCHAR(255) NOT NULL UNIQUE,
                    user_id VARCHAR(255) NOT NULL,
                    session_expire_timestamp TIMESTAMP NOT NULL,
                    access_token VARCHAR(255),
                    access_token_expire_timestamp TIMESTAMP NOT NULL
                )
                """
            )

            await db.execute(query="""
                CREATE TABLE IF NOT EXISTS sessions_guilds_map (
                    session_id VARCHAR(255) NOT NULL,
                    guild_id VARCHAR(255) NOT NULL
                )
                """
            )

    asyncio.run(main())
