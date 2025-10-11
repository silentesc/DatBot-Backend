from fastapi import APIRouter

from src.services.public.auth import AuthService
from src.data.models import Session


router = APIRouter()
auth_service = AuthService()


@router.get("/invite")
async def get_invite_url(guild_id: str) -> str:
    return await auth_service.get_invite_url(guild_id=guild_id)


@router.get("/login")
async def get_login_url() -> str:
    return await auth_service.get_login_url()


@router.post("/logout")
async def logout(session_id: str) -> None:
    return await auth_service.logout(session_id=session_id)


@router.get("/discord/callback")
async def discord_callback(code: str) -> Session:
    return await auth_service.discord_callback(code)


@router.get("/validate_session")
async def validate_session(session_id: str) -> Session:
    return await auth_service.validate_session(session_id=session_id)
