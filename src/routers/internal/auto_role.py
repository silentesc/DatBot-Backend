from fastapi import APIRouter

from src.services.internal.auto_role import AutoRoleService
from src.data.models import Role


router = APIRouter()
auto_role_service = AutoRoleService()


@router.get("/auto_roles")
async def get_auto_roles(api_key: str, guild_id: str) -> list[Role]:
    return await auto_role_service.get_auto_roles(api_key=api_key, guild_id=guild_id)
