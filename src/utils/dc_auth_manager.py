import uuid
import requests
from datetime import datetime, timedelta
from loguru import logger

from src.data.models import Session, User, Guild


SESSIONS: list[dict] = []


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
            for guild in guilds_data if guild["permissions"] == 2147483647
        ]

        # If a session already exists and is not expired, refresh session
        for entry in SESSIONS:
            if access_token == entry["access_token"]:
                session: Session = entry["session"]
                if datetime.now() < session.expire_timestamp:
                    session.user = user
                    session.guilds = user_guilds
                    entry["session"] = session
                    entry["token_expire"] = datetime.now() + timedelta(minutes=10)
                    logger.info("Old session has been refreshed.")
                    return session
        
        # If no session exists for that access token, create new one

        session = Session(
            session_id=str(uuid.uuid4()),
            user=user,
            guilds=user_guilds,
            expire_timestamp=datetime.now() + timedelta(days=7)
        )

        SESSIONS.append({
            "session": session,
            "access_token": access_token,
            "token_expire": datetime.now() + timedelta(minutes=1)
        })

        logger.info(f"New session has been created. Currently there are {len(SESSIONS)} sessions.")

        return session


def get_session(session_id: str) -> Session:
    for entry in SESSIONS:
        session: Session = entry["session"]
        access_token: str = entry["access_token"]
        token_expire: datetime = entry["token_expire"]

        if session_id == session.session_id:
            if datetime.now() > session.expire_timestamp:
                logger.info("Session expired")
                return None
            if datetime.now() > token_expire:
                logger.info("Access token expired, refreshing data")
                return refresh_data(access_token=access_token)
            logger.info("Everything good, returning session")
            return session
    
    logger.info("Session not found")
    return None


def clean_expired_sessions():
    count = 0
    for entry in SESSIONS:
        session: Session = entry["session"]
        if datetime.now() > session.expire_timestamp:
            SESSIONS.remove(entry)
            count += 1
    logger.info(f"{count} sessions have been removed due to expiration.")
