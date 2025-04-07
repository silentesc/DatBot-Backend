from fastapi import APIRouter

from src.services.internal.guild import GuildService
from src.data.models import Guild


router = APIRouter()
guild_service = GuildService()


@router.get("/guilds")
async def get_guilds(api_key: str) -> list[Guild]:
    return await guild_service.get_guilds(api_key=api_key)


@router.put("/guild")
async def update_guild(api_key: str, guild: Guild) -> None:
    return await guild_service.update_guild(api_key=api_key, guild=guild)
