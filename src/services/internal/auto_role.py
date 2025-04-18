from fastapi import HTTPException
from loguru import logger

from src.data.models import Role
from src.services.internal.guild import GuildService
from src.utils.db_manager import DbManager

from src import env


guild_service = GuildService()


class AutoRoleService:
    async def get_auto_roles(self, api_key: str, guild_id: str) -> list[Role]:
        if api_key != env.get_api_key():
            raise HTTPException(status_code=403, detail="Forbidden")
        
        # Get roles from bot
        roles = await guild_service.get_guild_roles(guild_id=guild_id)

        # Get auto roles from db
        async with DbManager() as db:
            auto_roles_rows: list[dict] = await db.execute_fetchall(query="SELECT * FROM auto_roles WHERE dc_guild_id = ?", params=(guild_id,))
        
        # Map list to only contain the auto roles
        auto_roles: list[Role] = []
        for auto_role_row in auto_roles_rows:
            role_id: str = auto_role_row["dc_role_id"]
            role = next((role for role in roles if role.id == role_id), None)
            if role:
                auto_roles.append(role)
            else:
                logger.warning(f"Role with id {role_id} does not exist in the guild with id {guild_id}")
        
        return auto_roles
