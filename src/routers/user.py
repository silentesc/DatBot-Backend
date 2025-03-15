from fastapi import APIRouter

from src.services.user import UserService


router = APIRouter()
user_service = UserService()


@router.get("/user_guilds")
async def get_user_guilds(session_id: str) -> list[dict]:
    return await user_service.get_user_guilds(session_id)
