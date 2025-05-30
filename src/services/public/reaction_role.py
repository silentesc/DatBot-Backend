from fastapi import HTTPException
from aiohttp import ClientSession
import emoji
import bleach
import json

from src.data.models import Session, EmojiRole, ReactionRole, EmojiRoleExtended, Channel, Role
from src.services.public.auth import AuthService
from src.services.public.guild import GuildService
from src.utils import response_manager, db_manager
from src import env


auth_service = AuthService()
guild_service = GuildService()


class ReactionRoleService:
    async def get_reaction_roles(self, session_id: str, guild_id: str) -> list[ReactionRole]:
        session: Session = await auth_service.validate_session(session_id=session_id)

        if not guild_id in [guild.id for guild in session.guilds]:
            raise HTTPException(status_code=404, detail="Guild not found in user session")
        
        guild_channels: list[Channel] = await guild_service.get_guild_channels(session_id=session_id, guild_id=guild_id)
        guild_roles: list[Role] = await guild_service.get_guild_roles(session_id=session_id, guild_id=guild_id)

        async with db_manager.DbManager() as db:
            reaction_role_messages_rows: list = await db.execute_fetchall(query="SELECT * FROM reaction_role_messages WHERE dc_guild_id = ?", params=(guild_id,))
            reaction_role_messages_ids: list = [reaction_role_message["id"] for reaction_role_message in reaction_role_messages_rows]

            placeholders = ','.join('?' for _ in reaction_role_messages_ids)
            query = f"SELECT * FROM reaction_roles WHERE reaction_role_messages_id IN ({placeholders})"
            reaction_roles_rows: list = await db.execute_fetchall(query=query, params=tuple(reaction_role_messages_ids))

        reaction_role_messages: dict[str, ReactionRole] = {}

        for reaction_role_messages_row in reaction_role_messages_rows:
            for channel in guild_channels:
                if channel.id == reaction_role_messages_row["dc_channel_id"]:
                    reaction_role_messages[reaction_role_messages_row["id"]] = ReactionRole(
                        message_id=reaction_role_messages_row["dc_message_id"],
                        guild_id=reaction_role_messages_row["dc_guild_id"],
                        channel_id=reaction_role_messages_row["dc_channel_id"],
                        channel_name=channel.name,
                        channel_type=channel.type,
                        channel_parent_id=channel.parent_id,
                        channel_position=channel.position,
                        type=reaction_role_messages_row["type"],
                        message=reaction_role_messages_row["message"],
                        emoji_roles=[]
                    )
        
        for reaction_roles_row in reaction_roles_rows:
            for role in guild_roles:
                if role.id == reaction_roles_row["dc_role_id"]:
                    rr: ReactionRole = reaction_role_messages[reaction_roles_row["reaction_role_messages_id"]]
                    rr.emoji_roles.append(
                        EmojiRoleExtended(
                            emoji=reaction_roles_row["emoji"],
                            role_id=reaction_roles_row["dc_role_id"],
                            role_name=role.name,
                            role_color=role.color,
                            role_position=role.position,
                        )
                    )
        
        return [v for _, v in reaction_role_messages.items()]


    async def create_reaction_role(self, session_id: str, guild_id: str, channel_id: str, reaction_role_type: str, message: str, emoji_roles: list[EmojiRole]) -> str:
        session: Session = await auth_service.validate_session(session_id=session_id)

        message = bleach.clean(message)

        guild = next((guild for guild in session.guilds if guild.id == guild_id), None)

        if not guild:
            raise HTTPException(status_code=404, detail="Guild not found in user session")
        
        for emoji_role in emoji_roles:
            if not emoji.is_emoji(emoji_role.emoji):
                raise HTTPException(status_code=400, detail="An emoji is not a real emoji")
        
        async with ClientSession() as client_session:
            async with client_session.post(f"http://localhost:3001/reaction_roles/{guild_id}/{channel_id}", headers={"Authorization": env.get_api_key()}, params={"message": message, "type": reaction_role_type, "emoji_roles": json.dumps([obj.dict() for obj in emoji_roles])}) as response:
                await response_manager.check_for_error(response=response)
                response_data = await response.json()

        dc_message_id = response_data["message_id"]

        async with db_manager.DbManager() as db:
            reaction_role_message_row = await db.execute_fetchone("INSERT INTO reaction_role_messages (dc_guild_id, dc_channel_id, dc_message_id, type, message) VALUES (?, ?, ?, ?, ?) RETURNING id", params=(guild_id, channel_id, dc_message_id, reaction_role_type, message))
            reaction_role_message_id = reaction_role_message_row["id"]

            reaction_role_emoji_roles_values = []
            for emoji_role in emoji_roles:
                reaction_role_emoji_roles_values.append(reaction_role_message_id)
                reaction_role_emoji_roles_values.append(emoji_role.emoji)
                reaction_role_emoji_roles_values.append(emoji_role.role_id)
            await db.execute(query=f"INSERT INTO reaction_roles (reaction_role_messages_id, emoji, dc_role_id) VALUES {",".join(["(?,?,?)" for _ in emoji_roles])}", params=tuple(reaction_role_emoji_roles_values))
        
        async with db_manager.DbManager() as db:
            await db.execute(query="INSERT OR IGNORE INTO guilds (id, name, icon) VALUES (?, ?, ?)", params=(guild_id, guild.name, guild.icon))
            await db.execute(query="INSERT OR IGNORE INTO users (id, username, avatar) VALUES (?, ?, ?)", params=(session.user.id, session.user.username, session.user.avatar))
            await db.execute(query="INSERT INTO logs (guild_id, user_id, action) VALUES (?, ?, ?)", params=(guild_id, session.user.id, "Added reaction role"))
        
        return dc_message_id


    async def delete_reaction_role(self, session_id: str, guild_id: str, channel_id: str, message_id: str):
        session: Session = await auth_service.validate_session(session_id=session_id)
        
        guild = next((guild for guild in session.guilds if guild.id == guild_id), None)

        if not guild:
            raise HTTPException(status_code=404, detail="Guild not found in user session")
        
        async with ClientSession() as client_session:
            async with client_session.delete(f"http://localhost:3001/reaction_roles/{guild_id}/{channel_id}/{message_id}", headers={"Authorization": env.get_api_key()}) as response:
                await response_manager.check_for_error(response=response)

        async with db_manager.DbManager() as db:
            reaction_role_message_row = await db.execute_fetchone(query="SELECT * FROM reaction_role_messages WHERE dc_guild_id = ? AND dc_channel_id = ? AND dc_message_id = ?", params=(guild_id, channel_id, message_id))
            if not reaction_role_message_row:
                raise HTTPException(status_code=404, detail="Couldn't find reaction role")
            reaction_role_message_id = reaction_role_message_row["id"]

            await db.execute("DELETE FROM reaction_roles WHERE reaction_role_messages_id = ?", params=(reaction_role_message_id,))
            await db.execute("DELETE FROM reaction_role_messages WHERE id = ?", params=(reaction_role_message_id,))
        
        async with db_manager.DbManager() as db:
            await db.execute(query="INSERT OR IGNORE INTO guilds (id, name, icon) VALUES (?, ?, ?)", params=(guild_id, guild.name, guild.icon))
            await db.execute(query="INSERT OR IGNORE INTO users (id, username, avatar) VALUES (?, ?, ?)", params=(session.user.id, session.user.username, session.user.avatar))
            await db.execute(query="INSERT INTO logs (guild_id, user_id, action) VALUES (?, ?, ?)", params=(guild_id, session.user.id, "Deleted reaction role"))
