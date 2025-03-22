from fastapi import APIRouter

from src.services.reaction_role import ReactionRoleService
from src.data.models import EmojiRole


router = APIRouter()
reaction_roles_service = ReactionRoleService()


@router.post("/reaction_role")
async def create_reaction_role(session_id: str, guild_id: str, channel_id: str, message: str, emoji_roles: list[EmojiRole]):
    return await reaction_roles_service.create_reaction_role(session_id=session_id, guild_id=guild_id, channel_id=channel_id, message=message, emoji_roles=emoji_roles)
