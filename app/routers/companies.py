import logging
from typing import List, Annotated
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, NoResultFound

from core.log_config import LoggingConfig
from libs.auth import get_current_user
from repository.companies import CompaniesRepository, CompanyRepository
from db.connect import get_session
from db.models import Company as CompanyFromModels, User as UserFromModels
from schemas.companies import CompanyUpdateRequestModel, CompanyDetailResponse, CompanyRequestModel
from schemas.users import PaginationParams
from schemas.auth import UserWithPermission


router = APIRouter(prefix="/companies", tags=["company"])
LoggingConfig.configure_logging()


def is_superuser(current_user: UserFromModels) -> bool:
    return current_user.is_superuser


def user_permission_company(current_user: Annotated[UserFromModels, Depends(get_current_user)],
                            company_id: int) -> UserFromModels:
    if is_superuser(current_user) or company_id in [comp.id for comp in current_user.owner_of_companies]:
        logging.error(f"User with: user_id - {current_user.id} and name - {current_user.username} got permission")
        return current_user
    else:
        raise HTTPException(status_code=403, detail="Forbidden action")


def user_permission_member(current_user: Annotated[UserFromModels, Depends(get_current_user)],
                            company_id: int) -> UserFromModels:
    if is_superuser(current_user) or company_id in [comp.id for comp in current_user.member_of_companies]:
        logging.error(f"User with: user_id - {current_user.id} and name - {current_user.username} got permission")
        return current_user
    else:
        raise HTTPException(status_code=403, detail="Forbidden action")


def get_company_instance(async_session: AsyncSession = Depends(get_session)) -> CompanyRepository:
    return CompanyRepository(async_session, CompanyFromModels)


def get_companies_instance(async_session: AsyncSession = Depends(get_session)) -> CompaniesRepository:
    return CompaniesRepository(async_session, CompanyFromModels)


@router.get("/", response_model=List[CompanyDetailResponse])
async def get_companies(
        current_user: Annotated[UserFromModels, Depends(get_current_user)],
        pagination: PaginationParams = Depends(),
        companies_instance: CompaniesRepository = Depends(get_companies_instance),
):
    all_companies = await companies_instance.paginate_query(entity=CompanyFromModels, page=pagination.page,
                                                            page_size=pagination.page_size)
    logging.info("Got all companies")
    return all_companies


@router.get("/{company_id}", response_model=CompanyDetailResponse)
async def get_company(
        current_user: Annotated[UserFromModels, Depends(get_current_user)],
        company_id: int,
        company_instance: CompanyRepository = Depends(get_company_instance)
):
    try:
        cur_company = await company_instance.get(entity_id=company_id)
        logging.info(
            f"Got companies: {cur_company.company_name} (id: {cur_company.id})")
        return cur_company

    except NoResultFound:
        logging.error("Tried to get non-existent company")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found company")


@router.put("/{company_id}", response_model=CompanyDetailResponse)
async def update_company(
        company_id: int,
        company_req_body: CompanyUpdateRequestModel,
        current_user: UserWithPermission = Depends(user_permission_company),
        company_instance: CompanyRepository = Depends(get_company_instance)
):
    try:
        company = await company_instance.update(body=company_req_body, entity_id=company_id)
        logging.info(f"Updated company: {company.company_name} (id: {company.id})")
        return company

    except NoResultFound:
        logging.error("Tried to get non-existent company")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found company")

    except IntegrityError:
        logging.error("Tried to change fields with non-unique name or email")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Company with such name or email already exists")


@router.post("/", response_model=CompanyDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_company(
        company_req_body: CompanyRequestModel,
        current_user: Annotated[UserFromModels, Depends(get_current_user)],
        company_instance: CompanyRepository = Depends(get_company_instance)
):
    try:
        new_company = await company_instance.create(body=company_req_body, user=current_user)
        logging.info(f"Created new company: {new_company.company_name} (id: {new_company.id})")
        return new_company

    except IntegrityError:
        logging.error("Tried to create with existing name")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Company already exists")


@router.delete("/{company_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_company(
        company_id: int,
        current_user: UserWithPermission = Depends(user_permission_company),
        company_instance: CompanyRepository = Depends(get_company_instance),
):
    try:
        await company_instance.delete(entity_id=company_id)
        logging.info(f"Company with company_id: {company_id} was deleted by user {current_user.username}")
        return {f"Company with id:{company_id} - deleted by user {current_user.username}"}

    except NoResultFound:
        logging.error("Tried to get non-existent company")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found company")


@router.delete("/{company_id}/members/{member_id}")
async def remove_member(
        company_id: int,
        member_id: int,
        current_user: UserWithPermission = Depends(user_permission_company),
        company_instance: CompanyRepository = Depends(get_company_instance),
):
    try:
        await company_instance.delete_member(company_id=company_id, member_id=member_id)
        logging.info(f"Member with id: {member_id} was deleted by user {current_user.username} from company {company_id}")
        return {f"Member with id: {member_id} - deleted by user {current_user.username} from company {company_id}"}

    except NoResultFound:
        logging.error("Tried to delete from non-existent company or member")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found company or memer")


@router.delete("/{company_id}/leave")
async def leave_company(
        company_id: int,
        current_user: UserWithPermission = Depends(user_permission_member),
        company_instance: CompanyRepository = Depends(get_company_instance),
):
    try:
        await company_instance.delete_member(company_id=company_id, member_id=current_user.id)
        logging.info(
            f"User with id: {current_user.id} left company {company_id}")
        return {f"User with id: {current_user.id} left company {company_id}"}

    except NoResultFound:
        logging.error("Tried to delete from non-existent company")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found company")
