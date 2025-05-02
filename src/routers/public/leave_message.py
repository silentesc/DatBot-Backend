from fastapi import APIRouter

from src.services.public.leave_message import LeaveMessageService
from src.data.models import LeaveMessage


router = APIRouter()
leave_message_service = LeaveMessageService()


@router.get("/leave_message")
async def get_leave_message(session_id: str, guild_id: str) -> LeaveMessage | None:
    return await leave_message_service.get_leave_message(session_id=session_id, guild_id=guild_id)


@router.put("/leave_message")
async def set_leave_message(session_id: str, guild_id: str, channel_id: str, message: str) -> None:
    return await leave_message_service.set_leave_message(session_id=session_id, guild_id=guild_id, channel_id=channel_id, message=message)


@router.delete("/leave_message")
async def delete_leave_message(session_id: str, guild_id: str) -> None:
    return await leave_message_service.delete_leave_message(session_id=session_id, guild_id=guild_id)
