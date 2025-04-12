import uuid
from aiohttp import ClientSession
from datetime import datetime, timedelta
from loguru import logger
import os
import tempfile
from filelock import AsyncFileLock, Timeout

from src.data.models import Session, User, Guild
from src.utils.db_manager import DbManager
from src.utils import response_manager

from src import env


def get_refresh_lock(session_id: str):
    lock_path = os.path.join(tempfile.gettempdir(), f"session_lock_{session_id}.lock")
    return AsyncFileLock(lock_path, timeout=60)


async def refresh_data(access_token: str) -> Session:
        async with ClientSession() as session:
            async with session.get("https://discord.com/api/users/@me", headers={"Authorization": f"Bearer {access_token}"}) as response:
                await response_manager.check_for_error(response=response)
                user_data: dict = await response.json()
        
        async with ClientSession() as session:
            async with session.get("https://discord.com/api/users/@me/guilds", headers={"Authorization": f"Bearer {access_token}"}) as response:
                await response_manager.check_for_error(response=response)
                guilds_data: dict = await response.json()
        
        async with ClientSession() as session:
            async with session.get(f"http://localhost:3001/guilds", headers={"Authorization": env.get_api_key()}) as response:
                await response_manager.check_for_error(response=response)
                bot_joined_guild_ids: list[str] = [bot_guild["id"] for bot_guild in await response.json()]

        user = User(
            id=user_data["id"],
            username=user_data["username"],
            avatar=user_data["avatar"],
        )

        # Get guilds from user data and combine with bot_joined from db to make Guild list
        user_guilds: list[Guild] = []
        async with DbManager() as db:
            for guild in guilds_data:
                if not ((int(guild["permissions"]) & 0x20) or (int(guild["permissions"]) & 0x8)):
                    continue
                guild_row: dict = await db.execute_fetchone(query="SELECT * FROM guilds WHERE id = ?", params=(guild["id"],))
                if not guild_row:
                    if guild["id"] in bot_joined_guild_ids:
                        bot_joined = True
                    else:
                        bot_joined = False
                else:
                    bot_joined = True if guild_row["bot_joined"] else False
                user_guilds.append(
                    Guild(
                        id=guild["id"],
                        name=guild["name"],
                        icon=guild["icon"],
                        bot_joined=bot_joined,
                    )
                )

        # If a session already exists and is not expired, refresh session
        async with DbManager() as db:
            session_row: dict = await db.execute_fetchone(query="SELECT * FROM sessions WHERE access_token = ?", params=(access_token,))
            if session_row and datetime.now() < str2datetime(session_row["session_expire_timestamp"]):
                session_id = session_row["id"]
                session_expire_timestamp = str2datetime(session_row["session_expire_timestamp"])

                # Add new guilds to guilds and sessions_guilds_map
                sessions_guilds_map_rows: list[dict] = await db.execute_fetchall(query=f"SELECT * FROM sessions_guilds_map WHERE session_id = ?", params=(session_id,))
                sessions_guilds_map_guild_ids: list[str] = [sessions_guilds_map_row["guild_id"] for sessions_guilds_map_row in sessions_guilds_map_rows]
                for user_guild in user_guilds:
                    if user_guild.id not in sessions_guilds_map_guild_ids:
                        await db.execute("INSERT OR IGNORE INTO guilds (id, name, icon, bot_joined) VALUES (?, ?, ?, ?)", (user_guild.id, user_guild.name, user_guild.icon, user_guild.bot_joined))
                        await db.execute("INSERT INTO sessions_guilds_map (session_id, guild_id) VALUES (?, ?)", (session_id, user_guild.id))
                
                # Delete removed guilds from sessions_guilds_map
                await db.execute(query=f"DELETE FROM sessions_guilds_map WHERE session_id = ? AND guild_id NOT IN ({",".join("?" for _ in user_guilds)})", params=tuple([session_id] + [user_guild.id for user_guild in user_guilds]))
                
                # Update users, guilds, sessions
                await db.execute(query="UPDATE users SET username = ?, avatar = ? WHERE id = ?", params=(user.username, user.avatar, user.id))
                for user_guild in user_guilds:
                    user_guild: Guild
                    await db.execute(query="UPDATE guilds SET name = ?, icon = ? WHERE id = ?", params=(user_guild.name, user_guild.icon, user_guild.id)) # Not updating bot_joined since value is just received from the db
                await db.execute(query="UPDATE sessions SET access_token_expire_timestamp = ? WHERE id = ?", params=((datetime.now() + timedelta(minutes=10)), session_id))

                logger.info("Old session has been refreshed.")
                return Session(session_id=session_id, user=user, guilds=user_guilds, expire_timestamp=session_expire_timestamp)
        
        # If no session exists for that access token, create new one
        session = Session(
            session_id=str(uuid.uuid4()),
            user=user,
            guilds=user_guilds,
            expire_timestamp=(datetime.now() + timedelta(days=7))
        )

        # Create db entires
        async with DbManager() as db:
            await db.execute(query="INSERT OR IGNORE INTO users (id, username, avatar) VALUES (?, ?, ?) RETURNING id", params=(user.id, user.username, user.avatar))
            await db.execute(query="INSERT OR IGNORE INTO sessions (id, user_id, session_expire_timestamp, access_token, access_token_expire_timestamp) VALUES (?, ?, ?, ?, ?)", params=(session.session_id, user.id, (datetime.now() + timedelta(days=7)), access_token, (datetime.now() + timedelta(minutes=10))))

            for user_guild in user_guilds:
                await db.execute("INSERT OR IGNORE INTO guilds (id, name, icon, bot_joined) VALUES (?, ?, ?, ?)", (user_guild.id, user_guild.name, user_guild.icon, user_guild.bot_joined))
                await db.execute("INSERT INTO sessions_guilds_map (session_id, guild_id) VALUES (?, ?)", (session.session_id, user_guild.id))

        logger.info(f"New session has been created.")

        return session


async def get_session(session_id: str) -> Session:
    async with DbManager() as db:
        sessions_row: dict = await db.execute_fetchone(query="SELECT * FROM sessions WHERE id = ?", params=(session_id,))
        if not sessions_row:
            logger.info("Session not found")
            return None
        
        users_row: dict = await db.execute_fetchone(query="SELECT * FROM users WHERE id = ?", params=(sessions_row["user_id"],))
        user = User(
            id=users_row["id"],
            username=users_row["username"],
            avatar=users_row["avatar"],
        )

        session_expire_timestamp = str2datetime(sessions_row["session_expire_timestamp"])
        access_token = sessions_row["access_token"]
        access_token_expire_timestamp = str2datetime(sessions_row["access_token_expire_timestamp"])

    if datetime.now() > session_expire_timestamp:
        logger.info("Session expired")
        await delete_session(session_id=session_id)
        return None

    # Use AsyncFileLock to ensure only one refresh occurs
    if datetime.now() > access_token_expire_timestamp:
        refresh_lock = get_refresh_lock(session_id)
        try:
            # Try to acquire lock in non-blocking mode
            await refresh_lock.acquire(blocking=False)
        except Timeout:
            logger.info("Refresh in progress, waiting for refreshed session")
            async with get_refresh_lock(session_id):
                return await get_session(session_id)
        else:
            try:
                logger.info("Access token expired, refreshing session")
                return await refresh_data(access_token=access_token)
            finally:
                await refresh_lock.release()

    async with DbManager() as db:
        guild_rows: list[dict] = await db.execute_fetchall(
            query="SELECT * FROM guilds WHERE id IN (SELECT guild_id FROM sessions_guilds_map WHERE session_id = ?)",
            params=(session_id,)
        )

    guilds: list[Guild] = []
    for guild_row in guild_rows:
        guilds.append(
            Guild(
                id=guild_row["id"],
                name=guild_row["name"],
                icon=guild_row["icon"],
                bot_joined=guild_row["bot_joined"],
            )
        )
    
    return Session(session_id=session_id, user=user, guilds=guilds, expire_timestamp=session_expire_timestamp)


async def delete_session(session_id: str) -> None:
    async with DbManager() as db:
        await db.execute(query="DELETE FROM sessions WHERE id = ?", params=(session_id,))
        await db.execute(query="DELETE FROM sessions_guilds_map WHERE session_id = ?", params=(session_id,))
    logger.info(f"Deleted session with id {session_id}")


async def clean_expired_sessions():
    async with DbManager() as db:
        expired_session_rows: list[dict] = await db.execute_fetchall(query="SELECT id FROM sessions WHERE session_expire_timestamp < ?", params=(datetime.now(),))
        expired_session_ids: list[str] = [expired_session_row["id"] for expired_session_row in expired_session_rows]

    for expired_session_id in expired_session_ids:
        await delete_session(expired_session_id)

    logger.info(f"{len(expired_session_ids)} sessions have been removed due to expiration.")


def str2datetime(timestamp: str) -> datetime:
    return datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")
