import requests
from fastapi import HTTPException

from src.utils import session_manager
from src import env
from src.data.models import Guild, User, Session


class AuthService:
    async def get_login_url(self) -> str:
        discord_auth_url = (
            f"https://discord.com/api/oauth2/authorize?client_id={env.get_client_id()}"
            f"&redirect_uri={env.get_redirect_uri()}&response_type=code&scope=identify%20guilds"
        )
        return discord_auth_url


    async def discord_callback(self, code: str) -> dict:
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

        token_response = requests.post("https://discord.com/api/oauth2/token", data=data, headers=headers)
        token_response.raise_for_status()
        token_data: dict = token_response.json()
        access_token = token_data["access_token"]

        user_response = requests.get("https://discord.com/api/users/@me", headers={"Authorization": f"Bearer {access_token}"})
        user_data: dict = user_response.json()

        guilds_response = requests.get("https://discord.com/api/users/@me/guilds", headers={"Authorization": f"Bearer {access_token}"})
        guilds_data = guilds_response.json()

        user = User(
            id=user_data["id"],
            username=user_data["username"],
            avatar=user_data["avatar"],
        )

        user_guilds = [
            Guild(
                id=guild["id"],
                name=guild["name"],
                icon=guild["icon"] or "",
            )
            for guild in guilds_data if guild["permissions"] == 2147483647
        ]

        session_id: str = session_manager.generate_session(user=user, guilds=user_guilds)

        return { "user": user, "guilds": user_guilds, "session_id": session_id }


    async def validate_session_id(self, session_id: str) -> Session:
        session: Session = session_manager.get_session(session_id=session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session does not exist or is expired.")
        return session
