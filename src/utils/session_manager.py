import uuid
from datetime import datetime, timedelta
from loguru import logger

from src.data.models import Guild, User
from src.data.models import Session


SESSIONS: dict[str, Session] = {}


def get_session(session_id: str) -> Session:
    session = SESSIONS.get(session_id)
    if not session or datetime.now() > session.expire_timestamp:
        return None
    return session


def generate_session(user: User, guilds: list[Guild]) -> str:
    session = Session(
        session_id=str(uuid.uuid4()),
        user=user,
        guilds=guilds,
        expire_timestamp=datetime.now() + timedelta(days=7)
    )
    SESSIONS[session.session_id] = session
    return session.session_id


def clean_expired_timestamps() -> None:
    count = 0
    for session in SESSIONS.values():
        if datetime.now() > session.expire_timestamp:
            del SESSIONS[session.session_id]
            count += 1
    logger.info(f"Removed {count} session due to expireation.")
