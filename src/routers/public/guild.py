from fastapi import APIRouter

from src.services.public.guild import GuildService
from src.data.models import Channel, Role


router = APIRouter()
guild_service = GuildService()


@router.get("/channels")
async def get_guild_channels(session_id: str, guild_id: str) -> list[Channel]:
    return await guild_service.get_guild_channels(session_id=session_id, guild_id=guild_id)


@router.get("/roles")
async def get_guild_roles(session_id: str, guild_id: str) -> list[Role]:
    return await guild_service.get_guild_roles(session_id=session_id, guild_id=guild_id)
