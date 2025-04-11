from fastapi import HTTPException

from src.data.models import Log, Session, Guild, User
from src.services.public.auth import AuthService
from src.utils.db_manager import DbManager


auth_service = AuthService()


class LogService:
    async def get_logs(self, session_id: str, guild_id: str, limit: int) -> list[Log]:
        session: Session = await auth_service.validate_session(session_id=session_id)

        if not guild_id in [guild.id for guild in session.guilds]:
            raise HTTPException(status_code=404, detail="Guild not found in user session")

        async with DbManager() as db:
            log_rows: list[dict] = await db.execute_fetchall(query="SELECT guilds.id AS guild_id, guilds.name AS guild_name, guilds.icon AS guild_icon, guilds.bot_joined AS guild_bot_joined, users.id AS user_id, users.username AS user_username, users.avatar AS user_avatar, logs.action, logs.timestamp FROM logs JOIN users ON users.id = logs.user_id JOIN guilds ON guilds.id = logs.guild_id WHERE logs.guild_id = ? ORDER BY timestamp DESC LIMIT ?", params=(guild_id, limit))
        
        logs = [
                Log(
                    guild=Guild(
                        id=log_row["guild_id"],
                        name=log_row["guild_name"],
                        icon=log_row["guild_icon"],
                        bot_joined=log_row["guild_bot_joined"],
                    ),
                    user=User(
                        id=log_row["user_id"],
                        username=log_row["user_username"],
                        avatar=log_row["user_avatar"],
                    ),
                    action=log_row["action"],
                    timestamp=log_row["timestamp"],
                ) for log_row in log_rows
        ]
        
        return logs
