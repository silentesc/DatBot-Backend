import uuid
import requests
from datetime import datetime, timedelta
from loguru import logger

from src.data.models import Session, User, Guild
from src.utils.db_manager import DbManager


def refresh_data(access_token: str) -> Session:
        user_response = requests.get("https://discord.com/api/users/@me", headers={"Authorization": f"Bearer {access_token}"})
        user_response.raise_for_status()
        user_data: dict = user_response.json()

        guilds_response = requests.get("https://discord.com/api/users/@me/guilds", headers={"Authorization": f"Bearer {access_token}"})
        guilds_response.raise_for_status()
        guilds_data = guilds_response.json()

        user = User(
            id=user_data["id"],
            username=user_data["username"],
            avatar=user_data["avatar"],
        )

        user_guilds = [
            Guild(
                id=guild["id"],
                name=guild["name"],
                icon=guild["icon"],
            )
            for guild in guilds_data if (int(guild["permissions"]) & 0x20) or (int(guild["permissions"]) & 0x8)
        ]

        # If a session already exists and is not expired, refresh session
        with DbManager() as db:
            session_row: dict = db.execute_fetchone(query="SELECT * FROM sessions WHERE access_token = ?", params=(access_token,))
            if session_row and datetime.now() < str2datetime(session_row["session_expire_timestamp"]):
                session_id = session_row["id"]
                session_expire_timestamp = str2datetime(session_row["session_expire_timestamp"])

                # Update db
                db.execute(query="UPDATE users SET username = ?, avatar = ? WHERE id = ?", params=(user.username, user.avatar, user.id))
                for user_guild in user_guilds:
                    db.execute(query="UPDATE guilds SET name = ?, icon = ? WHERE id = ?", params=(user_guild.name, user_guild.icon, user_guild.id))
                db.execute(query="UPDATE sessions SET access_token_expire_timestamp = ? WHERE id = ?", params=((datetime.now() + timedelta(minutes=10)), session_id))

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
        with DbManager() as db:
            db.execute(query="INSERT OR IGNORE INTO users (id, username, avatar) VALUES (?, ?, ?) RETURNING id", params=(user.id, user.username, user.avatar))
            db.execute(query="INSERT OR IGNORE INTO sessions (id, user_id, session_expire_timestamp, access_token, access_token_expire_timestamp) VALUES (?, ?, ?, ?, ?)", params=(session.session_id, user.id, (datetime.now() + timedelta(days=7)), access_token, (datetime.now() + timedelta(minutes=10))))

            for user_guild in user_guilds:
                db.execute("INSERT OR IGNORE INTO guilds (id, name, icon) VALUES (?, ?, ?)", (user_guild.id, user_guild.name, user_guild.icon))
                db.execute("INSERT INTO sessions_guilds_map (session_id, guild_id) VALUES (?, ?)", (session.session_id, user_guild.id))

        logger.info(f"New session has been created.")

        return session


def get_session(session_id: str) -> Session:
    with DbManager() as db:
        sessions_row: dict = db.execute_fetchone(query="SELECT * FROM sessions WHERE id = ?", params=(session_id,))
        if not sessions_row:
            logger.info("Session not found")
            return None
        
        users_row: dict = db.execute_fetchone(query="SELECT * FROM users WHERE id = ?", params=(sessions_row["user_id"],))
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
            delete_session(session_id=session_id)
            return None
        
        if datetime.now() > access_token_expire_timestamp:
            logger.info("Access token expired, refreshing session")
            return refresh_data(access_token=access_token)

        guild_rows: list[dict] = db.execute_fetchall(query="SELECT * FROM guilds WHERE id IN (SELECT guild_id FROM sessions_guilds_map WHERE session_id = ?)", params=(session_id,))

        guilds: list[Guild] = []
        for guild_row in guild_rows:
            guilds.append(
                Guild(
                    id=guild_row["id"],
                    name=guild_row["name"],
                    icon=guild_row["icon"],
                )
            )
        
        return Session(session_id=session_id, user=user, guilds=guilds, expire_timestamp=session_expire_timestamp)


def delete_session(session_id: str) -> None:
    with DbManager() as db:
        db.execute(query="DELETE FROM sessions WHERE id = ?", params=(session_id,))
        db.execute(query="DELETE FROM sessions_guilds_map WHERE session_id = ?", params=(session_id,))
    logger.info(f"Deleted session with id {session_id}")


def clean_expired_sessions():
    with DbManager() as db:
        expired_session_rows: list[dict] = db.execute_fetchall(query="SELECT id FROM sessions WHERE session_expire_timestamp < ?", params=(datetime.now(),))
        expired_session_ids: list[str] = [expired_session_row["id"] for expired_session_row in expired_session_rows]

    for expired_session_id in expired_session_ids:
        delete_session(expired_session_id)

    logger.info(f"{len(expired_session_ids)} sessions have been removed due to expiration.")


def str2datetime(timestamp: str) -> datetime:
    return datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")
