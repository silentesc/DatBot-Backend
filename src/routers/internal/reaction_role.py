from fastapi import APIRouter

from src.services.internal.reaction_role import ReactionRoleService


router = APIRouter()
reaction_roles_service = ReactionRoleService()


@router.get("/reaction_roles/{guild_id}")
async def get_reaction_roles(api_key: str, guild_id: str):
    return await reaction_roles_service.get_reaction_roles(api_key=api_key, guild_id=guild_id)
