from typing import Optional
from src.domain.entities import User
from src.domain.repositories import UserRepository

class UserService:
    """
    Service for managing users.
    """
    def __init__(self, user_repo: UserRepository):
        """
        Initialize UserService with a UserRepository.

        Args:
            user_repo (UserRepository): Repository for user data.
        """
        self.user_repo = user_repo

    async def create_user(self, telegram_id: int, username: Optional[str] = None) -> User:
        """
        Create a new user.

        Args:
            telegram_id (int): Telegram ID of the user.
            username (Optional[str]): Username of the user.

        Returns:
            User: Created user entity.
        """
        user = User(id=None, telegram_id=telegram_id, username=username)
        return await self.user_repo.create(user)

    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """
        Get a user by their Telegram ID.

        Args:
            telegram_id (int): Telegram ID of the user.

        Returns:
            Optional[User]: User entity if found, None otherwise.
        """
        return await self.user_repo.get_by_telegram_id(telegram_id)
