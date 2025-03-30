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


class UserGuild(BaseModel):
    bot_joined: bool
    guild: Guild


class EmojiRole(BaseModel):
    emoji: str
    role_id: str


class Channel(BaseModel):
    id: str
    name: str
    type: int
    parent_id: str | None


class Role(BaseModel):
    id: str
    name: str
    color: int
    position: int
