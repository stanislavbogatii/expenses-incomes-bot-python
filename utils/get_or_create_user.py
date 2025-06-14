from models import UserModel
from repositories import UserRepository

user_repository = UserRepository()

async def get_or_create_user(username: str, user_id: int) -> UserModel:
    user = await user_repository.find_one_by_username(username)
    if user:
        if (user.username != username):
            user.username = username
            return await user_repository.update(user)
        return user
    
    user = UserModel(
        username=username,
        user_id=user_id
    )
    await user_repository.store(user)
    return user