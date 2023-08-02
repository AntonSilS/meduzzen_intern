from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models import User as UserFromModels
from libs.hash import Hash
from schemas.users import SignUpRequestModel, UserUpdateRequestModel, UserStatus, SignInRequestModel
from db.connect import Base


class Paginateable:

    def __init__(self, async_session: AsyncSession):
        self.async_session = async_session

    async def paginate_query(self, entity: Base, page: int, page_size: int) -> List[Base]:
        skip = (page - 1) * page_size
        stmt = select(entity).limit(page_size).offset(skip)
        res = await self.async_session.execute(stmt)
        users = res.scalars().all()
        return users


class UsersRepository(Paginateable):

    def __init__(self, async_session: AsyncSession):
        super().__init__(async_session)

    async def get(self, user: UserFromModels) -> List[UserFromModels]:
        stmt = select(user)
        res = await self.async_session.execute(stmt)
        users = res.scalars().all()
        return users


class UserRepository:

    def __init__(self, async_session: AsyncSession):
        self.async_session = async_session

    def update_entity_fields(self, user: UserFromModels, body: UserUpdateRequestModel):
        res = {key: value for key, value in dict(body).items() if value is not None}
        for field, value in res.items():
            setattr(user, field, value)

    async def get(self, user_id: int) -> UserFromModels:
        stmt = select(UserFromModels).where(UserFromModels.id == user_id)
        res = await self.async_session.execute(stmt)
        user = res.scalars().one()
        return user

    async def create(self, body: SignUpRequestModel) -> UserFromModels:
        new_user = UserFromModels(
            username=body.username, email=body.email,
            password=Hash.get_password_hash(body.password)
        )
        self.async_session.add(new_user)
        await self.async_session.commit()
        await self.async_session.refresh(new_user)
        return new_user

    async def update(self, body: UserUpdateRequestModel, user_id: int):
        stmt = select(UserFromModels).where(UserFromModels.id == user_id)
        res = await self.async_session.execute(stmt)
        user = res.scalars().one()
        if user:
            self.update_entity_fields(user, body)
            await self.async_session.commit()
            await self.async_session.refresh(user)
        return user

    async def update_status(self, body: UserStatus, user_id: int):
        stmt = select(UserFromModels).where(UserFromModels.id == user_id)
        res = await self.async_session.execute(stmt)
        user = res.scalars().one()
        if user:
            user.status = body.status
            await self.async_session.commit()
            await self.async_session.refresh(user)
        return user

    async def delete(self, user_id: int) -> None:
        stmt = select(UserFromModels).where(UserFromModels.id == user_id)
        res = await self.async_session.execute(stmt)
        user = res.scalars().one()
        if user:
            await self.async_session.delete(user)
            await self.async_session.commit()

    async def get_user_by_login(self, login) -> UserFromModels:
        stmt = select(UserFromModels).where(UserFromModels.email == login)
        res = await self.async_session.execute(stmt)
        user = res.scalars().first()
        return user
