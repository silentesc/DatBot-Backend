import requests

from src.services.auth import AuthService
from src.data.models import Session, Guild
from src import env


auth_service = AuthService()


class UserService:
    async def get_user_guilds(self, session_id: str) -> list[dict]:
        session: Session = await auth_service.validate_session(session_id=session_id)

        response = requests.get("http://localhost:3001/guilds", headers={"Authorization": env.get_api_key()})
        response.raise_for_status()

        user_guilds = []
        for user_guild in session.guilds:
            user_guild: Guild
            found_bot_guild = False
            for bot_guild in response.json():
                if user_guild.id == bot_guild["id"]:
                    user_guilds.append({
                        "guild": user_guild,
                        "bot_joined": True,
                    })
                    found_bot_guild = True
                    break
            if not found_bot_guild:
                user_guilds.append({
                    "guild": user_guild,
                    "bot_joined": False,
                })

        return user_guilds
