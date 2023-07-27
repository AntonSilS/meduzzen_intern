from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models import User as UserFromModels
from schemas.users import SignUpRequestModel, UserUpdateRequestModel, UserStatus
from db.connect import Base


class Paginateable:

    @staticmethod
    async def paginate_query(entity: Base, page: int, page_size: int, async_session: AsyncSession) -> List[Base]:
        skip = (page - 1) * page_size
        stmt = select(entity).limit(page_size).offset(skip)
        res = await async_session.execute(stmt)
        users = res.scalars().all()
        return users


class Users(Paginateable):

    @staticmethod
    async def get(async_session: AsyncSession, user: UserFromModels) -> List[UserFromModels]:
        stmt = select(user)
        res = await async_session.execute(stmt)
        users = res.scalars().all()
        return users


class User:

    @staticmethod
    def update_entity_fields(user: UserFromModels, body: UserUpdateRequestModel):
        res = {key: value for key, value in dict(body).items() if value is not None}
        for field, value in res.items():
            setattr(user, field, value)

    @staticmethod
    async def get(async_session: AsyncSession, user_id: int) -> UserFromModels:
        stmt = select(UserFromModels).where(UserFromModels.id == user_id)
        res = await async_session.execute(stmt)
        user = res.scalars().one()
        return user

    @staticmethod
    async def create(async_session: AsyncSession, body: SignUpRequestModel) -> UserFromModels:
        new_user = UserFromModels(username=body.username, email=body.email, hash_password=body.hash_password)
        async_session.add(new_user)
        await async_session.commit()
        await async_session.refresh(new_user)
        return new_user

    @staticmethod
    async def update(async_session: AsyncSession, body: UserUpdateRequestModel, user_id: int):
        stmt = select(UserFromModels).where(UserFromModels.id == user_id)
        res = await async_session.execute(stmt)
        user = res.scalars().one()
        if user:
            User.update_entity_fields(user, body)
            await async_session.commit()
            await async_session.refresh(user)
        return user

    @staticmethod
    async def update_status(async_session: AsyncSession, body: UserStatus, user_id: int):
        stmt = select(UserFromModels).where(UserFromModels.id == user_id)
        res = await async_session.execute(stmt)
        user = res.scalars().one()
        if user:
            user.status = body.status
            await async_session.commit()
            await async_session.refresh(user)
        return user

    @staticmethod
    async def delete(async_session: AsyncSession, user_id: int) -> None:
        stmt = select(UserFromModels).where(UserFromModels.id == user_id)
        res = await async_session.execute(stmt)
        user = res.scalars().one()
        if user:
            await async_session.delete(user)
            await async_session.commit()
