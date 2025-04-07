from fastapi import APIRouter

from src.services.public.guild import UserService
from src.data.models import Channel, Role


router = APIRouter()
user_service = UserService()


@router.get("/channels")
async def get_guild_channels(session_id: str, guild_id: str) -> list[Channel]:
    return await user_service.get_guild_channels(session_id=session_id, guild_id=guild_id)


@router.get("/roles")
async def get_guild_roles(session_id: str, guild_id: str) -> list[Role]:
    return await user_service.get_guild_roles(session_id=session_id, guild_id=guild_id)
