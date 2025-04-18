from fastapi import APIRouter

from src.services.public.auto_role import AutoRoleService
from src.data.models import Role


router = APIRouter()
auto_role_service = AutoRoleService()


@router.get("/auto_roles")
async def get_reaction_roles(session_id: str, guild_id: str) -> list[Role]:
    return await auto_role_service.get_auto_roles(session_id=session_id, guild_id=guild_id)


@router.post("/auto_role")
async def add_auto_role(session_id: str, guild_id: str, role_id: str) -> Role | None:
    return await auto_role_service.add_auto_role(session_id=session_id, guild_id=guild_id, role_id=role_id)


@router.delete("/auto_role")
async def remove_auto_role(session_id: str, guild_id: str, role_id: str) -> None:
    return await auto_role_service.remove_auto_role(session_id=session_id, guild_id=guild_id, role_id=role_id)
