from fastapi import APIRouter

from src.services.auth import AuthService
from src.data.models import Session


router = APIRouter()
auth_service = AuthService()


@router.get("/login")
async def get_login_url() -> str:
    return await auth_service.get_login_url()


@router.get("/discord/callback")
async def discord_callback(code: str) -> dict:
    return await auth_service.discord_callback(code)


@router.get("/validate")
async def validate_session(session_id: str) -> Session:
    return await auth_service.validate_session(session_id=session_id)
