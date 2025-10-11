from aiohttp import ClientSession
from fastapi import HTTPException

from src.utils import session_manager, response_manager
from src import env
from src.data.models import  Session


class AuthService:
    async def get_login_url(self) -> str:
        discord_auth_url = (
            f"https://discord.com/api/oauth2/authorize?client_id={env.get_client_id()}"
            f"&redirect_uri={env.get_redirect_uri()}&response_type=code&scope=identify%20guilds"
        )
        return discord_auth_url


    async def get_invite_url(self, guild_id: str) -> str:
        invite_url = (
            f"https://discord.com/oauth2/authorize?client_id={env.get_client_id()}&guild_id={guild_id}&permissions=268520512&integration_type=0&scope=bot"
        )
        return invite_url


    async def discord_callback(self, code: str) -> Session:
        if not code:
            raise HTTPException(status_code=400, detail="No code.")

        data = {
            "client_id": env.get_client_id(),
            "client_secret": env.get_client_secret(),
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": env.get_redirect_uri(),
            "scope": "identify guilds"
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        async with ClientSession() as client_session:
            async with client_session.post("https://discord.com/api/oauth2/token", data=data, headers=headers) as response:
                await response_manager.check_for_error(response=response)
                token_data: dict = await response.json()
                access_token = token_data["access_token"]

        return await session_manager.refresh_data(access_token=access_token)


    async def validate_session(self, session_id: str) -> Session:
        session: Session | None = await session_manager.get_session(session_id=session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session does not exist or is expired.")
        return session


    async def logout(self, session_id: str) -> None:
        session: Session | None = await session_manager.get_session(session_id=session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session does not exist or is already expired.")
        
        await session_manager.delete_session(session_id=session_id)
