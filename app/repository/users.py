from typing import List, Union

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
        stmt = select(UserFromModels).where(UserFromModels.email == login)
        res = await self.async_session.execute(stmt)
        user = res.scalars().first()
        return user

    async def get_user_with_loading_field(self, user_id: int, *fields_to_load: str) -> UserFromModels:
        stmt = select(UserFromModels).where(UserFromModels.id == user_id)

        for field in fields_to_load:
            stmt = stmt.options(joinedload(field))

        res = await self.async_session.execute(stmt)
        user = res.scalars().first()
        return user

    async def get_user_with_owner_of_companies(self, user_id: int) -> UserFromModels:
        return await self.get_user_with_loading_field(user_id, 'owner_of_companies', )

    async def get_user_with_member_of_companies(self, user_id: int) -> UserFromModels:
        return await self.get_user_with_loading_field(user_id, 'member_of_companies', )

    async def get_user_with_admin_owner(self, user_id: int) -> UserFromModels:
        user = await self.get_user_with_loading_field(user_id, 'owner_of_companies', 'admin_of_companies')
        return user
