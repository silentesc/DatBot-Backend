from fastapi import APIRouter

from src.services.internal.leave_message import LeaveMessageService
from src.data.models import LeaveMessage


router = APIRouter()
leave_message_service = LeaveMessageService()


@router.get("/leave_message")
async def get_leave_message(api_key: str, guild_id: str) -> LeaveMessage | None:
    return await leave_message_service.get_leave_message(api_key=api_key, guild_id=guild_id)
