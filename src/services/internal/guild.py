from aiohttp import ClientSession
from fastapi import HTTPException

from src import env
from src.data.models import Guild, Role
from src.utils import response_manager
from src.utils.db_manager import DbManager


class GuildService:
    async def get_guilds(self, api_key: str) -> list[Guild]:
        if api_key != env.get_api_key():
            raise HTTPException(status_code=403, detail="Forbidden")
        
        async with DbManager() as db:
            guild_rows = await db.execute_fetchall(query="SELECT * FROM guilds")
        
        guilds: list[Guild] = [Guild(id=guild_row["id"], name=guild_row["name"], icon=guild_row["icon"], bot_joined=guild_row["bot_joined"]) for guild_row in guild_rows]
        return guilds


    async def update_guild(self, api_key: str, guild: Guild) -> None:
        if api_key != env.get_api_key():
            raise HTTPException(status_code=403, detail="Forbidden")

        async with DbManager() as db:
            guild_row = await db.execute_fetchone(query="SELECT * FROM guilds WHERE id = ?", params=(guild.id,))
            if not guild_row:
                await db.execute(query="INSERT INTO guilds (id, name, icon, bot_joined) VALUES (?, ?, ?, ?)", params=(guild.id, guild.name, guild.icon, guild.bot_joined))
            else:
                await db.execute(query="UPDATE guilds SET name = ?, icon = ?, bot_joined = ? WHERE id = ?", params=(guild.name, guild.icon, guild.bot_joined, guild.id))


    async def get_guild_roles(self, guild_id: str) -> list[Role]:
        async with ClientSession() as client_session:
            async with client_session.get(f"http://localhost:3001/guilds/{guild_id}/roles", headers={"Authorization": env.get_api_key()}) as response:
                await response_manager.check_for_error(response=response)
                response_data = await response.json()

        roles = [Role(id=role["id"], name=role["name"], color=role["color"], position=role["position"], managed=role["managed"]) for role in response_data]

        return roles
