from typing import List
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from db.models import User as UserFromModels, Action as ActionFromModels, TypeAction
from .base import BaseEntitiesRepository, BaseEntityRepository, Paginateable
from schemas.action import ActionRequestModel


class InvitesRepository(BaseEntitiesRepository):

    async def paginate_query(self, user_id: int, page: int, page_size: int) -> List[ActionFromModels]:
        stmt = select(self.entity).where((self.entity.type_action == TypeAction.INVITE) &
                                         (self.entity.recipient_id == user_id)).options(joinedload(self.entity.sender))
        stmt_with_pagination = self.apply_pagination(stmt, page, page_size)
        res = await self.async_session.execute(stmt_with_pagination)
        entities = res.scalars().all()
        return entities


class InviteRepository(BaseEntityRepository, Paginateable):

    async def get_action_with_load_fields(self, action: ActionFromModels):
        stmt = select(ActionFromModels).where(ActionFromModels.id == action.id). \
            options(
            joinedload(ActionFromModels.sender),
            joinedload(ActionFromModels.company)
        )
        res = await self.async_session.execute(stmt)
        action_with_loading_fields = res.scalars().one()
        return action_with_loading_fields

    async def create(self, company_id: int, body: ActionRequestModel, user: UserFromModels) -> ActionFromModels:
        action = await super().create(
            type_action=TypeAction.INVITE,
            company_id=company_id,
            sender_id=user.id,
            recipient_id=body.recipient_id
        )

        return await self.get_action_with_load_fields(action=action)

    async def paginate_query(self, company_id: int, page: int, page_size: int) -> List[UserFromModels]:
        stmt = select(UserFromModels).join(self.entity, UserFromModels.id == self.entity.recipient_id). \
            where((self.entity.type_action == TypeAction.INVITE) & (self.entity.company_id == company_id))
        stmt_with_pagination = self.apply_pagination(stmt, page, page_size)
        res = await self.async_session.execute(stmt_with_pagination)
        entities = res.scalars().all()
        return entities
