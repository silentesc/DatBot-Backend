from datetime import datetime
from pydantic import BaseModel


class Guild(BaseModel):
    id: str
    name: str
    icon: str | None


class User(BaseModel):
    id: str
    username: str
    avatar: str


class Session(BaseModel):
    session_id: str
    user: User
    guilds: list[Guild]
    expire_timestamp: datetime
