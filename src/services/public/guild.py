from fastapi import HTTPException
from aiohttp import ClientSession

from src.services.public.auth import AuthService
from src.data.models import Session, Channel, Role
from src.utils import response_manager
from src import env


auth_service = AuthService()


class GuildService:
    async def get_guild_channels(self, session_id: str, guild_id: str) -> list[Channel]:
        session: Session = await auth_service.validate_session(session_id=session_id)

        if not guild_id in [guild.id for guild in session.guilds]:
            raise HTTPException(status_code=404, detail="Guild not found in user session")
        
        async with ClientSession() as client_session:
            async with client_session.get(f"http://localhost:3001/guilds/{guild_id}/channels", headers={"Authorization": env.get_api_key()}) as response:
                await response_manager.check_for_error(response=response)
                response_data = await response.json()

        channels = [Channel(id=channel["id"], name=channel["name"], type=channel["type"], parent_id=channel["parentId"], position=channel["position"]) for channel in response_data]

        return channels


    async def get_guild_roles(self, session_id: str, guild_id: str) -> list[Role]:
        session: Session = await auth_service.validate_session(session_id=session_id)

        if not guild_id in [guild.id for guild in session.guilds]:
            raise HTTPException(status_code=404, detail="Guild not found in user session")

        async with ClientSession() as client_session:
            async with client_session.get(f"http://localhost:3001/guilds/{guild_id}/roles", headers={"Authorization": env.get_api_key()}) as response:
                await response_manager.check_for_error(response=response)
                response_data = await response.json()

        roles = [Role(id=role["id"], name=role["name"], color=role["color"], position=role["position"], managed=role["managed"]) for role in response_data]

        return roles
