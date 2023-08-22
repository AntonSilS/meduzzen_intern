from typing import List
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from db.models import User as UserFromModels, Action as ActionFromModels, TypeAction
from .base import BaseEntitiesRepository, BaseEntityRepository
from schemas.action import ActionRequestModel


class InvitesRepository(BaseEntitiesRepository):

    async def paginate_query(self, user_id: int, page: int, page_size: int) -> List[ActionFromModels]:
        skip = (page - 1) * page_size

        stmt = select(self.entity).where((self.entity.type_action == TypeAction.INVITE) &
                                         (self.entity.recipient_id == user_id)).options(joinedload(self.entity.sender)).limit(page_size).offset(skip)

        res = await self.async_session.execute(stmt)
        entities = res.scalars().all()
        return entities


class InviteRepository(BaseEntityRepository):

    async def create(self, company_id: int, body: ActionRequestModel, user: UserFromModels) -> ActionFromModels:
        return await super().create(
            type_action=TypeAction.INVITE,
            company_id=company_id,
            sender_id=user.id,
            recipient_id=body.recipient_id
        )
