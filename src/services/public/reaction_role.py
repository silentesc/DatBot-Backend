from fastapi import HTTPException
import requests
import emoji

from src.data.models import Session, EmojiRole
from src.services.public.auth import AuthService
from src.services.public.user import UserService
from src.utils import response_manager, db_manager
from src import env


auth_service = AuthService()
user_service = UserService()


class ReactionRoleService:
    async def get_reaction_roles(self, session_id: str, guild_id: str):
        session: Session = await auth_service.validate_session(session_id=session_id)

        if not guild_id in [guild.id for guild in session.guilds]:
            raise HTTPException(status_code=404, detail="Guild not found in user session")
        
        guild_channels: list[dict] = await user_service.get_guild_channels(session_id=session_id, guild_id=guild_id)
        guild_roles: list[dict] = await user_service.get_guild_roles(session_id=session_id, guild_id=guild_id)

        with db_manager.DbManager() as db:
            reaction_role_messages_rows: list = db.execute_fetchall(query="SELECT * FROM reaction_role_messages WHERE dc_guild_id = ?", params=(guild_id,))
            reaction_role_messages_ids: list = [reaction_role_message["id"] for reaction_role_message in reaction_role_messages_rows]

            placeholders = ','.join('?' for _ in reaction_role_messages_ids)
            query = f"SELECT * FROM reaction_roles WHERE reaction_role_messages_id IN ({placeholders})"
            reaction_roles_rows: list = db.execute_fetchall(query=query, params=tuple(reaction_role_messages_ids))

        reaction_role_messages: dict[str, dict[str, any]] = {}

        for reaction_role_messages_row in reaction_role_messages_rows:
            for channel in guild_channels:
                if channel["id"] == reaction_role_messages_row["dc_channel_id"]:
                    reaction_role_messages[reaction_role_messages_row["id"]] = {
                        "message_id": reaction_role_messages_row["dc_message_id"],
                        "guild_id": reaction_role_messages_row["dc_guild_id"],
                        "channel_id": reaction_role_messages_row["dc_channel_id"],
                        "channel_name": channel["name"],
                        "channel_type": channel["type"],
                        "channel_parent_id": channel["parentId"],
                        "type": reaction_role_messages_row["type"],
                        "message": reaction_role_messages_row["message"],
                    }
        
        for reaction_roles_row in reaction_roles_rows:
            if not reaction_role_messages[reaction_roles_row["reaction_role_messages_id"]].get("emoji_roles"):
                reaction_role_messages[reaction_roles_row["reaction_role_messages_id"]]["emoji_roles"] = []
            
            for role in guild_roles:
                if role["id"] == reaction_roles_row["dc_role_id"]:
                    reaction_role_messages[reaction_roles_row["reaction_role_messages_id"]]["emoji_roles"].append({
                        "emoji": reaction_roles_row["emoji"],
                        "role_id": reaction_roles_row["dc_role_id"],
                        "role_name": role["name"],
                        "role_color": role["color"],
                        "role_position": role["position"],
                    })
        
        return [v for _, v in reaction_role_messages.items()]


    async def create_reaction_role(self, session_id: str, guild_id: str, channel_id: str, reaction_role_type: str, message: str, emoji_roles: list[EmojiRole]) -> str:
        session: Session = await auth_service.validate_session(session_id=session_id)

        if not guild_id in [guild.id for guild in session.guilds]:
            raise HTTPException(status_code=404, detail="Guild not found in user session")
        
        for emoji_role in emoji_roles:
            if not emoji.is_emoji(emoji_role.emoji):
                raise HTTPException(status_code=400, detail="An emoji is not a real emoji")
        
        response = requests.post(f"http://localhost:3001/reaction_roles/{guild_id}/{channel_id}", headers={"Authorization": env.get_api_key()}, params={"message": message, "type": reaction_role_type, "emoji_roles": emoji_roles})
        response_manager.check_for_error(response=response)

        dc_message_id = response.json()["message_id"]

        with db_manager.DbManager() as db:
            reaction_role_message_id = db.execute_fetchone("INSERT INTO reaction_role_messages (dc_guild_id, dc_channel_id, dc_message_id, type, message) VALUES (?, ?, ?, ?, ?) RETURNING id", params=(guild_id, channel_id, dc_message_id, reaction_role_type, message))["id"]

            reaction_role_emoji_roles_values = []
            for emoji_role in emoji_roles:
                reaction_role_emoji_roles_values.append(reaction_role_message_id)
                reaction_role_emoji_roles_values.append(emoji_role.emoji)
                reaction_role_emoji_roles_values.append(emoji_role.role_id)
            db.execute(query=f"INSERT INTO reaction_roles (reaction_role_messages_id, emoji, dc_role_id) VALUES {",".join(["(?,?,?)" for _ in emoji_roles])}", params=tuple(reaction_role_emoji_roles_values))
        
        return dc_message_id


    async def delete_reaction_role(self, session_id: str, guild_id: str, channel_id: str, message_id: str):
        session: Session = await auth_service.validate_session(session_id=session_id)

        if not guild_id in [guild.id for guild in session.guilds]:
            raise HTTPException(status_code=404, detail="Guild not found in user session")
        
        response = requests.delete(f"http://localhost:3001/reaction_roles/{guild_id}/{channel_id}/{message_id}", headers={"Authorization": env.get_api_key()})
        response_manager.check_for_error(response=response)

        with db_manager.DbManager() as db:
            reaction_role_message_row = db.execute_fetchone(query="SELECT * FROM reaction_role_messages WHERE dc_guild_id = ? AND dc_channel_id = ? AND dc_message_id = ?", params=(guild_id, channel_id, message_id))
            if not reaction_role_message_row:
                raise HTTPException(status_code=404, detail="Couldn't find reaction role")
            reaction_role_message_id = reaction_role_message_row["id"]

            db.execute("DELETE FROM reaction_roles WHERE reaction_role_messages_id = ?", params=(reaction_role_message_id,))
            db.execute("DELETE FROM reaction_role_messages WHERE id = ?", params=(reaction_role_message_id,))
