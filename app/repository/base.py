from pydantic import BaseModel as BaseModelPydantic
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.connect import Base
from db.models import Base as BaseFromModels


class Paginateable:

    def __init__(self, async_session: AsyncSession):
        self.async_session = async_session

    async def paginate_query(self, entity: Base, page: int, page_size: int) -> List[BaseFromModels]:
        skip = (page - 1) * page_size
        stmt = select(entity).limit(page_size).offset(skip)
        res = await self.async_session.execute(stmt)
        entities = res.scalars().all()
        return entities


class BaseEntitiesRepository(Paginateable):

    def __init__(self, async_session: AsyncSession, entity: BaseFromModels):
        super().__init__(async_session)
        self.entity = entity

    async def get(self) -> List[BaseFromModels]:
        stmt = select(self.entity)
        res = await self.async_session.execute(stmt)
        return res.scalars().all()


class BaseEntityRepository:

    def __init__(self, async_session: AsyncSession, entity: BaseFromModels):
        self.async_session = async_session
        self.entity = entity

    async def get(self, entity_id: int) -> Optional[BaseFromModels]:
        stmt = select(self.entity).where(self.entity.id == entity_id)
        res = await self.async_session.execute(stmt)
        return res.scalars().one()

    async def create(self, **kwargs) -> BaseFromModels:
        new_entity = self.entity(**kwargs)
        self.async_session.add(new_entity)
        await self.async_session.commit()
        await self.async_session.refresh(new_entity)
        return new_entity

    async def update(self, entity_id: int, body: BaseModelPydantic) -> Optional[BaseFromModels]:
        entity = await self.get(entity_id)
        if entity:
            for key, value in dict(body).items():
                if value is not None:
                    setattr(entity, key, value)
            await self.async_session.commit()
            await self.async_session.refresh(entity)
        return entity

    async def delete(self, entity_id: int) -> None:
        entity = await self.get(entity_id)
        if entity:
            await self.async_session.delete(entity)
            await self.async_session.commit()
