from sqlalchemy import select
from sqlalchemy.orm import joinedload

from db.models import User as UserFromModels
from repository.base import BaseEntitiesRepository, BaseEntityRepository
from libs.hash import Hash
from schemas.users import SignUpRequestModel, UserUpdateRequestModel, UserStatus


class UsersRepository(BaseEntitiesRepository):
    pass


class UserRepository(BaseEntityRepository):

    async def create(self, body: SignUpRequestModel) -> UserFromModels:
        hashed_password = Hash.get_password_hash(body.password)
        return await super().create(username=body.username, email=body.email, password=hashed_password)

    async def update(self, user_id: int, body: UserUpdateRequestModel) -> UserFromModels:
        if body.password:
            body.password = Hash.get_password_hash(body.password)
        return await super().update(user_id, body)

    async def update_status(self, body: UserStatus, user_id: int) -> UserFromModels:
        stmt = select(self.entity).where(self.entity.id == user_id)
        res = await self.async_session.execute(stmt)
        user = res.scalars().one()
        if user:
            user.status = body.status
            await self.async_session.commit()
            await self.async_session.refresh(user)
        return user

    async def get_user_by_login(self, login) -> UserFromModels:
        stmt = select(UserFromModels).where(UserFromModels.email == login).\
            options(
                joinedload(UserFromModels.owner_of_companies),
                joinedload(UserFromModels.sent_actions),
                joinedload(UserFromModels.member_of_companies)
            )
        res = await self.async_session.execute(stmt)
        user = res.scalars().first()
        return user
