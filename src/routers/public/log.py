from fastapi import APIRouter

from src.services.public.log import LogService
from src.data.models import Log


router = APIRouter()
log_service = LogService()


@router.get("/logs/{guild_id}")
async def get_logs(session_id: str, guild_id: str, limit: int = 10) -> list[Log]:
    return await log_service.get_logs(session_id=session_id, guild_id=guild_id, limit=limit)
