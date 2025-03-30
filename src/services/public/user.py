from fastapi import HTTPException
import requests

from src.services.public.auth import AuthService
from src.data.models import Session, Guild, UserGuild
from src.utils import response_manager
from src import env


auth_service = AuthService()


class UserService:
    async def get_user_guilds(self, session_id: str) -> list[UserGuild]:
        session: Session = await auth_service.validate_session(session_id=session_id)

        response = requests.get("http://localhost:3001/guilds", headers={"Authorization": env.get_api_key()})
        response_manager.check_for_error(response=response)

        user_guilds = []
        for user_guild in session.guilds:
            user_guild: Guild
            found_bot_guild = False
            for bot_guild in response.json():
                if user_guild.id == bot_guild["id"]:
                    user_guilds.append(UserGuild(bot_joined=True, guild=user_guild))
                    found_bot_guild = True
                    break
            if not found_bot_guild:
                user_guilds.append(UserGuild(bot_joined=False, guild=user_guild))

        return user_guilds


    async def get_guild_channels(self, session_id: str, guild_id: str) -> list[dict]:
        session: Session = await auth_service.validate_session(session_id=session_id)

        if not guild_id in [guild.id for guild in session.guilds]:
            raise HTTPException(status_code=404, detail="Guild not found in user session")

        response = requests.get(f"http://localhost:3001/guilds/{guild_id}/channels", headers={"Authorization": env.get_api_key()})
        response_manager.check_for_error(response=response)

        return response.json()


    async def get_guild_roles(self, session_id: str, guild_id: str) -> list[dict]:
        session: Session = await auth_service.validate_session(session_id=session_id)

        if not guild_id in [guild.id for guild in session.guilds]:
            raise HTTPException(status_code=404, detail="Guild not found in user session")

        response = requests.get(f"http://localhost:3001/guilds/{guild_id}/roles", headers={"Authorization": env.get_api_key()})
        response_manager.check_for_error(response=response)

        return response.json()
