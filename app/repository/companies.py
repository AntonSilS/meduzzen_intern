from typing import List

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from db.models import Company as CompanyFromModels, User as UserFromModels
from repository.base import BaseEntitiesRepository, BaseEntityRepository, Paginateable
from schemas.companies import CompanyRequestModel


class CompaniesRepository(BaseEntitiesRepository):

    async def paginate_query(self, entity: CompanyFromModels, page: int, page_size: int) -> List[CompanyFromModels]:
        companies = await super().paginate_query(entity, page, page_size)
        visible_companies = [company for company in companies if company.visible]
        return visible_companies


class CompanyRepository(BaseEntityRepository, Paginateable):

    async def create(self, body: CompanyRequestModel, user: UserFromModels) -> CompanyFromModels:
        return await super().create(
            company_name=body.company_name,
            description=body.description,
            owner_id=user.id
        )

    async def delete_member(self, company_id: int, member_id: int) -> None:
        stmt = select(self.entity).where(self.entity.id == company_id).options(selectinload(self.entity.members))
        res = await self.async_session.execute(stmt)
        company = res.scalars().one()

        stmt_2 = select(UserFromModels).where(UserFromModels.id == member_id)
        res = await self.async_session.execute(stmt_2)
        member = res.scalars().one()

        if member in company.members:
            company.members.remove(member)

        await self.async_session.commit()
        await self.async_session.refresh(company)

    async def paginate_query(self, company_id: int, page: int, page_size: int) -> List[UserFromModels]:
        stmt = select(UserFromModels).join(UserFromModels, self.entity.members). \
            where(CompanyFromModels.id == company_id)
        stmt_with_pagination = self.apply_pagination(stmt, page, page_size)
        res = await self.async_session.execute(stmt_with_pagination)
        entities = res.scalars().all()
        return entities
