from fastapi import HTTPException

from src import env
from src.data.models import Guild
from src.utils.db_manager import DbManager


class GuildService:
    async def get_guilds(self, api_key: str) -> list[Guild]:
        if api_key != env.get_api_key():
            raise HTTPException(status_code=403, detail="Forbidden")
        
        async with DbManager() as db:
            guild_rows: list[dict] = await db.execute_fetchall(query="SELECT * FROM guilds")
        
        guilds: list[Guild] = [Guild(id=guild_row["id"], name=guild_row["name"], icon=guild_row["icon"], bot_joined=guild_row["bot_joined"]) for guild_row in guild_rows]
        return guilds


    async def update_guild(self, api_key: str, guild: Guild) -> None:
        if api_key != env.get_api_key():
            raise HTTPException(status_code=403, detail="Forbidden")

        async with DbManager() as db:
            guild_row: dict = await db.execute_fetchone(query="SELECT * FROM guilds WHERE id = ?", params=(guild.id,))
            if not guild_row:
                await db.execute(query="INSERT INTO guilds (id, name, icon, bot_joined) VALUES (?, ?, ?, ?)", params=(guild.id, guild.name, guild.icon, guild.bot_joined))
            else:
                await db.execute(query="UPDATE guilds SET name = ?, icon = ?, bot_joined = ? WHERE id = ?", params=(guild.name, guild.icon, guild.bot_joined, guild.id))
