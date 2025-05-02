from fastapi import APIRouter

from src.services.internal.welcome_message import WelcomeMessageService
from src.data.models import Guild, WelcomeMessage, Channel


router = APIRouter()
welcome_message_service = WelcomeMessageService()


@router.get("/welcome_message")
async def get_welcome_message(api_key: str, guild_id: str) -> WelcomeMessage | None:
    return await welcome_message_service.get_welcome_message(api_key=api_key, guild_id=guild_id)
