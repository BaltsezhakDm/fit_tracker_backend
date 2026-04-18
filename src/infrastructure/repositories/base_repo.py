from typing import List, Optional, TypeVar, Generic, Type
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.repositories import BaseRepository

T = TypeVar("T")
M = TypeVar("M")

class SQLAlchemyBaseRepository(Generic[T, M]):
    def __init__(self, session: AsyncSession, model: Type[M]):
        self.session = session
        self.model = model

    async def get_by_id(self, id: int) -> Optional[T]:
        stmt = select(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        item = result.scalar_one_or_none()
        return self._to_entity(item) if item else None

    async def get_all(self) -> List[T]:
        stmt = select(self.model)
        result = await self.session.execute(stmt)
        items = result.scalars().all()
        return [self._to_entity(item) for item in items]

    async def create(self, entity: T) -> T:
        model_obj = self._to_model(entity)
        self.session.add(model_obj)
        await self.session.commit()
        await self.session.refresh(model_obj)
        return self._to_entity(model_obj)

    async def update(self, entity: T) -> Optional[T]:
        model_obj = await self.session.get(self.model, entity.id)
        if not model_obj:
            return None
        for key, value in entity.__dict__.items():
            if key != "id" and hasattr(model_obj, key):
                setattr(model_obj, key, value)
        await self.session.commit()
        await self.session.refresh(model_obj)
        return self._to_entity(model_obj)

    async def delete(self, id: int) -> None:
        stmt = delete(self.model).where(self.model.id == id)
        await self.session.execute(stmt)
        await self.session.commit()

    def _to_entity(self, model_obj: M) -> T:
        raise NotImplementedError

    def _to_model(self, entity: T) -> M:
        raise NotImplementedError
