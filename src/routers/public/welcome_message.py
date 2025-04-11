from fastapi import APIRouter

from src.services.public.welcome_message import WelcomeMessageService
from src.data.models import WelcomeMessage


router = APIRouter()
welcome_message_service = WelcomeMessageService()


@router.get("/welcome_message")
async def get_reaction_roles(session_id: str, guild_id: str) -> WelcomeMessage | None:
    return await welcome_message_service.get_welcome_message(session_id=session_id, guild_id=guild_id)


@router.put("/welcome_message")
async def create_reaction_role(session_id: str, guild_id: str, channel_id: str, message: str) -> None:
    return await welcome_message_service.set_welcome_message(session_id=session_id, guild_id=guild_id, channel_id=channel_id, message=message)


@router.delete("/welcome_message")
async def delete_reaction_role(session_id: str, guild_id: str) -> None:
    return await welcome_message_service.delete_welcome_message(session_id=session_id, guild_id=guild_id)
