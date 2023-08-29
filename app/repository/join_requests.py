from typing import List
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from db.models import Company as CompanyFromModels, User as UserFromModels, Action as ActionFromModels, TypeAction
from .base import BaseEntitiesRepository, BaseEntityRepository


class JoinRequestsRepository(BaseEntitiesRepository):
    async def paginate_query(self, user_id: int, page: int, page_size: int) -> List[ActionFromModels]:

        stmt = select(self.entity).where((self.entity.type_action == TypeAction.JOIN_REQUEST) &
                                         (self.entity.sender_id == user_id)).\
                                          options(
                                              joinedload(ActionFromModels.sender),
                                              joinedload(ActionFromModels.company)
                                          )
        stmt_with_pagination = self.apply_pagination(stmt, page, page_size)

        res = await self.async_session.execute(stmt_with_pagination)
        entities = res.scalars().all()
        return entities


class JoinRequestRepository(BaseEntityRepository):
    async def get_company_by_id(self, company_id: int):
        stmt = select(CompanyFromModels).where(CompanyFromModels.id == company_id)
        res = await self.async_session.execute(stmt)
        company = res.scalars().one()
        return company

    async def create(self, company_id: int, user: UserFromModels) -> ActionFromModels:
        return await super().create(
            type_action=TypeAction.JOIN_REQUEST,
            company_id=company_id,
            sender_id=user.id,
            recipient_id=user.id
        )

