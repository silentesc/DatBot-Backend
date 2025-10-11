from fastapi import HTTPException

from src import env
from src.data.models import EmojiRole
from src.utils.db_manager import DbManager


class ReactionRoleService:
    async def get_reaction_roles(self, api_key: str, guild_id: str):
        if api_key != env.get_api_key():
            raise HTTPException(status_code=403, detail="Forbidden")

        async with DbManager() as db:
            reaction_role_messages_rows = await db.execute_fetchall(query="SELECT * FROM reaction_role_messages WHERE dc_guild_id = ?", params=(guild_id,))
            reaction_role_messages_ids = [reaction_role_message["id"] for reaction_role_message in reaction_role_messages_rows]

            placeholders = ','.join('?' for _ in reaction_role_messages_ids)
            query = f"SELECT * FROM reaction_roles WHERE reaction_role_messages_id IN ({placeholders})"
            reaction_roles_rows = await db.execute_fetchall(query=query, params=tuple(reaction_role_messages_ids))

        reaction_role_messages: dict[str, dict[str, str | EmojiRole | list[EmojiRole]]] = {}

        for reaction_role_messages_row in reaction_role_messages_rows:
            reaction_role_messages[reaction_role_messages_row["id"]] = {
                "type": reaction_role_messages_row["type"],
                "guild_id": reaction_role_messages_row["dc_guild_id"],
                "channel_id": reaction_role_messages_row["dc_channel_id"],
                "message_id": reaction_role_messages_row["dc_message_id"],
                "emoji_roles": [],
            }
        
        for reaction_roles_row in reaction_roles_rows:
            list(reaction_role_messages[reaction_roles_row["reaction_role_messages_id"]]["emoji_roles"]).append(
                EmojiRole(
                    emoji=reaction_roles_row["emoji"],
                    role_id=reaction_roles_row["dc_role_id"]
                )
            )
        
        return [v for _, v in reaction_role_messages.items()]
