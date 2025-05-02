from datetime import datetime
from pydantic import BaseModel


class Guild(BaseModel):
    id: str
    name: str
    icon: str | None
    bot_joined: bool


class User(BaseModel):
    id: str
    username: str
    avatar: str


class Session(BaseModel):
    session_id: str
    user: User
    guilds: list[Guild]
    expire_timestamp: datetime


class EmojiRole(BaseModel):
    emoji: str
    role_id: str


class EmojiRoleExtended(BaseModel):
    emoji: str
    role_id: str
    role_name: str
    role_color: int
    role_position: int


class ReactionRole(BaseModel):
    message_id: str
    guild_id: str
    channel_id: str
    channel_name: str
    channel_type: int
    channel_parent_id: str | None
    channel_position: int
    type: str
    message: str
    emoji_roles: list[EmojiRoleExtended]


class Channel(BaseModel):
    id: str
    name: str
    type: int
    parent_id: str | None
    position: int


class Role(BaseModel):
    id: str
    name: str
    color: int
    position: int
    managed: bool


class Log(BaseModel):
    guild: Guild
    user: User
    action: str
    timestamp: datetime


class WelcomeMessage(BaseModel):
    guild: Guild
    channel: Channel
    message: str


class LeaveMessage(BaseModel):
    guild: Guild
    channel: Channel
    message: str
