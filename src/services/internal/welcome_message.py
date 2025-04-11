from fastapi import HTTPException
import requests

from src.data.models import Channel, Guild, WelcomeMessage
from src.services.public.auth import AuthService
from src.services.public.guild import UserService
from src.utils import response_manager
from src.utils.db_manager import DbManager

from src import env


auth_service = AuthService()
user_service = UserService()


class WelcomeMessageService:
    async def get_welcome_message(self, api_key: str, guild_id: str) -> WelcomeMessage | None:
        if api_key != env.get_api_key():
            raise HTTPException(status_code=403, detail="Forbidden")
        
        response = requests.get(f"http://localhost:3001/guilds/{guild_id}/channels", headers={"Authorization": env.get_api_key()})
        response_manager.check_for_error(response=response)
        
        async with DbManager() as db:
            welcome_message_row: dict = await db.execute_fetchone(query="SELECT * FROM welcome_messages WHERE dc_guild_id = ?", params=(guild_id,))
        
        if not welcome_message_row:
            return None
        
        channels: list[Channel] = [
            Channel(id=channel["id"], name=channel["name"], type=channel["type"], parent_id=channel["parentId"], position=channel["position"])
            for channel in response.json()
            if channel["id"] == welcome_message_row["dc_channel_id"]
        ]

        if len(channels) != 1:
            raise HTTPException(status_code=400, detail="Channel is not found in guild")
        
        async with DbManager() as db:
            guild_row: dict = await db.execute_fetchone(query="SELECT * FROM guilds WHERE id = ?", params=(guild_id,))
        
        if not guild_row:
            raise HTTPException(status_code=400, detail="Guild not found in db")
        
        guild: Guild = Guild(
            id=guild_row["id"],
            name=guild_row["name"],
            icon=guild_row["icon"],
            bot_joined=guild_row["bot_joined"],
        )
        
        return WelcomeMessage(
            guild=guild,
            channel=channels[0],
            message=welcome_message_row["message"]
        )
