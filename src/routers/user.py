from fastapi import APIRouter

from src.services.user import UserService
from src.data.models import Guild


router = APIRouter()
user_service = UserService()


@router.get("/user_guilds")
async def get_user_guilds(session_id: str) -> list[Guild]:
    return await user_service.get_user_guilds(session_id)
