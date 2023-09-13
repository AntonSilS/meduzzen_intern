from pydantic import BaseModel as BaseModelPydantic
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from db.connect import Base
from db.models import Base as BaseFromModels, Company as CompanyFromModels, User as UserFromModels, \
    StatusActionForResponse, Action as ActionFromModels
from schemas.action import ActionRequestModel


class Paginateable:

    def __init__(self, async_session: AsyncSession):
        self.async_session = async_session

    @staticmethod
    def apply_pagination(stmt, page: int, page_size: int):
        skip = (page - 1) * page_size
        return stmt.limit(page_size).offset(skip)

    async def paginate_query(self, entity: Base, page: int, page_size: int) -> List[BaseFromModels]:
        stmt = select(entity)
        stmt_with_pagination = self.apply_pagination(stmt, page, page_size)
        res = await self.async_session.execute(stmt_with_pagination)
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

    async def add_member(self, company_id: int, action: ActionRequestModel) -> None:
        stmt_1 = select(CompanyFromModels).where(CompanyFromModels.id == company_id)
        res = await self.async_session.execute(stmt_1)
        company = res.scalars().one()

        member_id = action.recipient_id
        stmt_2 = select(UserFromModels).where(UserFromModels.id == member_id).options(
            joinedload(UserFromModels.member_of_companies),
        )
        res = await self.async_session.execute(stmt_2)
        member = res.scalars().unique().one()

        member.member_of_companies.append(company)

    async def response(self, action_id: int, body: StatusActionForResponse, company_id: int) -> ActionFromModels:
        stmt = select(self.entity).where(self.entity.id == action_id)
        res = await self.async_session.execute(stmt)
        action = res.scalars().one()
        if action:
            action.status_action = body
            if body.value == "accepted":
                await self.add_member(company_id=company_id, action=action)

            await self.async_session.commit()
            await self.async_session.refresh(action)
        return action

    async def get_entity_with_loading_field(self, entity: BaseFromModels, entity_id: int,
                                            *fields_to_load: str) -> BaseFromModels:
        stmt = select(entity).where(entity.id == entity_id)
        for field in fields_to_load:
            stmt = stmt.options(joinedload(field))

        res = await self.async_session.execute(stmt)
        entity_res = res.scalars().first()
        return entity_res
