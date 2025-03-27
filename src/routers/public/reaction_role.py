from fastapi import APIRouter

from src.services.public.reaction_role import ReactionRoleService
from src.data.models import EmojiRole


router = APIRouter()
reaction_roles_service = ReactionRoleService()


@router.get("/reaction_roles")
async def get_reaction_roles(session_id: str, guild_id: str):
    return await reaction_roles_service.get_reaction_roles(session_id=session_id, guild_id=guild_id)


@router.post("/reaction_role")
async def create_reaction_role(session_id: str, guild_id: str, channel_id: str, reaction_role_type: str, message: str, emoji_roles: list[EmojiRole]) -> str:
    return await reaction_roles_service.create_reaction_role(session_id=session_id, guild_id=guild_id, channel_id=channel_id, reaction_role_type=reaction_role_type, message=message, emoji_roles=emoji_roles)


@router.delete("/reaction_role")
async def delete_reaction_role(session_id: str, guild_id: str, channel_id: str, message_id: str):
    return await reaction_roles_service.delete_reaction_role(session_id=session_id, guild_id=guild_id, channel_id=channel_id, message_id=message_id)
