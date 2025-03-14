import requests
from fastapi import HTTPException

from src.utils import session_manager
from src.data.models import Session, Guild
from src import env


class UserService:
    async def get_user_guilds(self, session_id: str) -> list[Guild]:
        session: Session = session_manager.get_session(session_id=session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session does not exist or is expired.")
        
        user_guild_ids = [user_guild.id for user_guild in session.guilds]
        
        response = requests.get("http://localhost:3001/guilds", headers={"Authorization": env.get_api_key()})
        response.raise_for_status()

        guilds: list[dict] = [Guild(id=guild["id"], name=guild["name"], icon=guild["icon"]) for guild in response.json() if guild["id"] in user_guild_ids]
        return guilds
