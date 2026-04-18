from typing import Optional
from sqlalchemy import select
from src.domain.entities import User
from src.domain.repositories import UserRepository
from src.infrastructure.db.models import UserModel
from src.infrastructure.repositories.base_repo import SQLAlchemyBaseRepository

class SQLAlchemyUserRepository(SQLAlchemyBaseRepository[User, UserModel], UserRepository):
    def __init__(self, session):
        super().__init__(session, UserModel)

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        item = result.scalar_one_or_none()
        return self._to_entity(item) if item else None

    def _to_entity(self, model_obj: UserModel) -> User:
        return User(
            id=model_obj.id,
            telegram_id=model_obj.telegram_id,
            username=model_obj.username,
            created_at=model_obj.created_at
        )

    def _to_model(self, entity: User) -> UserModel:
        return UserModel(
            id=entity.id,
            telegram_id=entity.telegram_id,
            username=entity.username,
            created_at=entity.created_at
        )
