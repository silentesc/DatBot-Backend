from pydantic import BaseModel


class Guild(BaseModel):
    id: str
    name: str
    icon: str


class User(BaseModel):
    id: str
    username: str
    avatar: str
