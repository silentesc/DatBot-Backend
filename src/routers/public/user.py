from fastapi import APIRouter

from src.services.public.user import UserService
from src.data.models import UserGuild


router = APIRouter()
user_service = UserService()


@router.get("/user_guilds")
async def get_user_guilds(session_id: str) -> list[UserGuild]:
    return await user_service.get_user_guilds(session_id)

@router.get("/guild_channels")
async def get_guild_channels(session_id: str, guild_id: str) -> list[dict]:
    return await user_service.get_guild_channels(session_id=session_id, guild_id=guild_id)

@router.get("/guild_roles")
async def get_guild_roles(session_id: str, guild_id: str) -> list[dict]:
    return await user_service.get_guild_roles(session_id=session_id, guild_id=guild_id)
