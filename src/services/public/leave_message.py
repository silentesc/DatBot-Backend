from fastapi import HTTPException
from aiohttp import ClientSession
import bleach

from src.data.models import Channel, Session, LeaveMessage
from src.services.public.auth import AuthService
from src.utils import response_manager
from src.utils.db_manager import DbManager

from src import env


auth_service = AuthService()


class LeaveMessageService:
    async def get_leave_message(self, session_id: str, guild_id: str) -> LeaveMessage | None:
        session: Session = await auth_service.validate_session(session_id=session_id)

        guild = next((guild for guild in session.guilds if guild.id == guild_id), None)
        if not guild:
            raise HTTPException(status_code=404, detail="Guild not found in user session")
        
        async with ClientSession() as client_session:
            async with client_session.get(f"http://localhost:3001/guilds/{guild_id}/channels", headers={"Authorization": env.get_api_key()}) as response:
                await response_manager.check_for_error(response=response)
                response_data = await response.json()
        
        async with DbManager() as db:
            leave_message_row = await db.execute_fetchone(query="SELECT * FROM leave_messages WHERE dc_guild_id = ?", params=(guild_id,))
        
        if not leave_message_row:
            return None
        
        channels: list[Channel] = [
            Channel(id=channel["id"], name=channel["name"], type=channel["type"], parent_id=channel["parentId"], position=channel["position"])
            for channel in response_data
            if channel["id"] == leave_message_row["dc_channel_id"]
        ]

        if len(channels) != 1:
            raise HTTPException(status_code=400, detail="Channel is not found in guild")
        
        return LeaveMessage(
            guild=guild,
            channel=channels[0],
            message=leave_message_row["message"]
        )


    async def set_leave_message(self, session_id: str, guild_id: str, channel_id: str, message: str) -> None:
        session: Session = await auth_service.validate_session(session_id=session_id)

        if not guild_id in [guild.id for guild in session.guilds]:
            raise HTTPException(status_code=404, detail="Guild not found in user session")
        
        async with ClientSession() as client_session:
            async with client_session.get(f"http://localhost:3001/guilds/{guild_id}/channels", headers={"Authorization": env.get_api_key()}) as response:
                await response_manager.check_for_error(response=response)
                response_data = await response.json()

        channel_found = False
        for channel in response_data:
            if channel["id"] == channel_id:
                channel_found = True
                break

        if not channel_found:
            raise HTTPException(status_code=400, detail="Channel is not found in guild")

        message = bleach.clean(message)

        if len(message) <= 0 or len(message) > 2000:
            raise HTTPException(status_code=400, detail="Message length must be between 0 and 2000")

        async with DbManager() as db:
            leave_message_row = await db.execute_fetchone(query="SELECT * FROM leave_messages WHERE dc_guild_id = ?", params=(guild_id,))
            if not leave_message_row:
                await db.execute(query="INSERT INTO leave_messages (dc_guild_id, dc_channel_id, message) VALUES (?, ?, ?)", params=(guild_id, channel_id, message))
            else:
                await db.execute(query="UPDATE leave_messages SET dc_channel_id = ?, message = ? WHERE dc_guild_id = ?", params=(channel_id, message, guild_id))
            
            await db.execute(query="INSERT INTO logs (guild_id, user_id, action) VALUES (?, ?, ?)", params=(guild_id, session.user.id, "Update leave message"))


    async def delete_leave_message(self, session_id: str, guild_id: str) -> None:
        session: Session = await auth_service.validate_session(session_id=session_id)
        
        if not guild_id in [guild.id for guild in session.guilds]:
            raise HTTPException(status_code=404, detail="Guild not found in user session")
        
        async with DbManager() as db:
            leave_message_row = await db.execute_fetchone(query="SELECT * FROM leave_messages WHERE dc_guild_id = ?", params=(guild_id,))
            if not leave_message_row:
                raise HTTPException(status_code=404, detail="This guild has no leave message set")
            else:
                await db.execute(query="DELETE FROM leave_messages WHERE dc_guild_id = ?", params=(guild_id,))
            
            await db.execute(query="INSERT INTO logs (guild_id, user_id, action) VALUES (?, ?, ?)", params=(guild_id, session.user.id, "Delete leave message"))
