from db.mongo import db
from models import UserModel

class UserRepository:
    def __init__(self) -> None:
        self.users = db['users']

    async def find_one_by_username(self, username: str) -> UserModel | None:
        user = await self.users.find_one({"username": username})
        if user:
            return UserModel(**user)
        return None
    
    async def store(self, user: UserModel) -> UserModel:
        user = await self.users.insert_one(user.dict(by_alias=True))