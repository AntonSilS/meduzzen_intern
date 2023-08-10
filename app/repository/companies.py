from typing import List

from db.models import Company as CompanyFromModels, User as UserFromModels
from .base import BaseEntitiesRepository, BaseEntityRepository
from schemas.companies import CompanyRequestModel

class CompaniesRepository(BaseEntitiesRepository):

    async def paginate_query(self, entity: CompanyFromModels, page: int, page_size: int) -> List[CompanyFromModels]:
        companies = await super().paginate_query(entity, page, page_size)
        visible_companies = [company for company in companies if company.visible]
        return visible_companies


class CompanyRepository(BaseEntityRepository):

    async def create(self, body: CompanyRequestModel, user: UserFromModels) -> CompanyFromModels:
        return await super().create(
            company_name=body.company_name,
            description=body.description,
            owner_id=user.id
        )
