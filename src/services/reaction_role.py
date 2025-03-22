from fastapi import HTTPException
import requests
import emoji

from src.data.models import Session, EmojiRole
from src.services.auth import AuthService
from src.utils import response_manager, db_manager
from src import env


auth_service = AuthService()


class ReactionRoleService:
    async def create_reaction_role(self, session_id: str, guild_id: str, channel_id: str, message: str, emoji_roles: list[EmojiRole]):
        session: Session = await auth_service.validate_session(session_id=session_id)

        if not guild_id in [guild.id for guild in session.guilds]:
            raise HTTPException(status_code=404, detail="Guild not found in user session")
        
        if len(emoji_roles) > 20:
            raise HTTPException(status_code=400, detail="Maximum of 20 emojis on a message is exceeded")
        
        for emoji_role in emoji_roles:
            if not emoji.is_emoji(emoji_role.emoji):
                raise HTTPException(status_code=400, detail="An emoji is not a real emoji")
        
        response = requests.post(f"http://localhost:3001/reaction_role/{guild_id}/{channel_id}", headers={"Authorization": env.get_api_key()}, params={"message": message, "emoji_roles": emoji_roles})
        response_manager.check_for_error(response=response)

        with db_manager.DbManager() as db:
            reaction_role_message_id = db.execute_fetchone("INSERT INTO reaction_role_messages (dc_guild_id, dc_channel_id, message) VALUES (?, ?, ?) RETURNING id", params=(guild_id, channel_id, message))[0]

            reaction_role_emoji_roles_values = []
            for emoji_role in emoji_roles:
                reaction_role_emoji_roles_values.append(reaction_role_message_id)
                reaction_role_emoji_roles_values.append(emoji_role.emoji)
                reaction_role_emoji_roles_values.append(emoji_role.role_id)
            db.execute(query=f"INSERT INTO reaction_roles (reaction_role_messages_id, emoji, dc_role_id) VALUES {",".join(["(?,?,?)" for _ in emoji_roles])}", params=tuple(reaction_role_emoji_roles_values))
