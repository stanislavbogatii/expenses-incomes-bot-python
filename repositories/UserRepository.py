from db.mongo import db
from models import UserModel
from models import PyObjectId

class UserRepository:
    def __init__(self) -> None:
        self.users = db['users']

    async def find_one_by_username(self, username: str) -> UserModel | None:
        user = await self.users.find_one({"username": username})
        if user:
            return UserModel(**user)
        return None
    
    async def update(self, user: UserModel)-> UserModel:
        return await self.users.update_one({"_id": PyObjectId(user.id)}, {"$set": user.dict(by_alias=True)})
    
    async def find_one_by_id(self, id: str) -> UserModel | None:
        user = await self.users.find_one({"_id": PyObjectId(id)})
        if user:
            return UserModel(**user)
        return None
    
    async def find_all(self) -> list[UserModel]:
        users = []
        async for user in self.users.find():
            users.append(UserModel(**user))
        return users
    
    async def store(self, user: UserModel) -> UserModel:
        user = await self.users.insert_one(user.dict(by_alias=True))