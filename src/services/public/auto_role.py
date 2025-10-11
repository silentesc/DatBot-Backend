from fastapi import HTTPException
from loguru import logger

from src.data.models import Session, Role
from src.services.public.auth import AuthService
from src.services.public.guild import GuildService
from src.utils.db_manager import DbManager


auth_service = AuthService()
guild_service = GuildService()


class AutoRoleService:
    async def get_auto_roles(self, session_id: str, guild_id: str) -> list[Role]:
        session: Session = await auth_service.validate_session(session_id=session_id)

        # Get guild from session
        guild = next((guild for guild in session.guilds if guild.id == guild_id), None)
        if not guild:
            raise HTTPException(status_code=404, detail="Guild not found in user session")
        
        # Get roles from bot
        roles = await guild_service.get_guild_roles(session_id=session_id, guild_id=guild_id)

        # Get auto roles from db
        async with DbManager() as db:
            auto_roles_rows = await db.execute_fetchall(query="SELECT * FROM auto_roles WHERE dc_guild_id = ?", params=(guild_id,))
        
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


    async def add_auto_role(self, session_id: str, guild_id: str, role_id: str) -> Role | None:
        session: Session = await auth_service.validate_session(session_id=session_id)

        if not guild_id in [guild.id for guild in session.guilds]:
            raise HTTPException(status_code=404, detail="Guild not found in user session")
        
        roles: list[Role] = await guild_service.get_guild_roles(session_id=session_id, guild_id=guild_id)

        if not (role_id in [role.id for role in roles]):
            raise HTTPException(status_code=404, detail="Role does not exist on guild");
        
        async with DbManager() as db:
            auto_roles_row = await db.execute_fetchone(query="SELECT * FROM auto_roles WHERE dc_guild_id = ? AND dc_role_id = ?", params=(guild_id, role_id))
            if auto_roles_row:
                raise HTTPException(status_code=400, detail="This role for this guild is already a auto role")
            await db.execute(query="INSERT INTO auto_roles (dc_guild_id, dc_role_id) VALUES (?, ?)", params=(guild_id, role_id))

            await db.execute(query="INSERT INTO logs (guild_id, user_id, action) VALUES (?, ?, ?)", params=(guild_id, session.user.id, "Add a role to auto roles"))
        
        return next((role for role in roles if role.id == role_id), None)


    async def remove_auto_role(self, session_id: str, guild_id: str, role_id: str) -> None:
        session: Session = await auth_service.validate_session(session_id=session_id)
        
        if not guild_id in [guild.id for guild in session.guilds]:
            raise HTTPException(status_code=404, detail="Guild not found in user session")
        
        async with DbManager() as db:
            auto_roles_row = await db.execute_fetchone(query="SELECT * FROM auto_roles WHERE dc_guild_id = ? AND dc_role_id = ?", params=(guild_id, role_id))
            if not auto_roles_row:
                raise HTTPException(status_code=404, detail="This role for this guild does not exist")
            await db.execute(query="DELETE FROM auto_roles WHERE dc_guild_id = ? AND dc_role_id = ?", params=(guild_id, role_id))

            await db.execute(query="INSERT INTO logs (guild_id, user_id, action) VALUES (?, ?, ?)", params=(guild_id, session.user.id, "Remove a role from auto roles"))
