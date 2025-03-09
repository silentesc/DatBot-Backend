import uuid
from datetime import datetime, timedelta
from loguru import logger

from src.data.models import Guild, User
from src.data import models


class Session:
    def __init__(self, user: User, guilds: list[Guild]):
        self.session_id = str(uuid.uuid4())
        self.user = user
        self.guilds = guilds
        self.expire_timestamp = datetime.now() + timedelta(days=1)


SESSIONS: dict[str, Session] = {}


def get_session(session_id: str) -> models.Session:
    session = SESSIONS.get(session_id)
    if not session or datetime.now() > session.expire_timestamp:
        return None
    return session


def generate_session(user: User, guilds: list[Guild]) -> str:
    session = Session(user=user, guilds=guilds)
    SESSIONS[session.session_id] = session
    return session.session_id


def clean_expired_timestamps() -> None:
    count = 0
    for session in SESSIONS.values():
        if datetime.now() > session.expire_timestamp:
            del SESSIONS[session.session_id]
            count += 1
    logger.info(f"Removed {count} session due to expireation.")
