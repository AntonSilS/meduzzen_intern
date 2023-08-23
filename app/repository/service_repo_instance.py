from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.connect import get_session
from db.models import Action as ActionFromModels, Company as CompanyFromModels, User as UserFromModels
from repository.users import UsersRepository, UserRepository
from repository.join_requests import JoinRequestRepository, JoinRequestsRepository
from repository.invites import InviteRepository, InvitesRepository
from repository.companies import CompaniesRepository, CompanyRepository


def get_user_instance(async_session: AsyncSession = Depends(get_session)) -> UserRepository:
    return UserRepository(async_session, UserFromModels)


def get_users_instance(async_session: AsyncSession = Depends(get_session)) -> UsersRepository:
    return UsersRepository(async_session, UserFromModels)


def get_join_request_instance(async_session: AsyncSession = Depends(get_session)) -> JoinRequestRepository:
    return JoinRequestRepository(async_session, ActionFromModels)


def get_join_requests_instance(async_session: AsyncSession = Depends(get_session)) -> JoinRequestsRepository:
    return JoinRequestsRepository(async_session, ActionFromModels)


def get_invite_instance(async_session: AsyncSession = Depends(get_session)) -> InviteRepository:
    return InviteRepository(async_session, ActionFromModels)


def get_invites_instance(async_session: AsyncSession = Depends(get_session)) -> InvitesRepository:
    return InvitesRepository(async_session, ActionFromModels)


def get_company_instance(async_session: AsyncSession = Depends(get_session)) -> CompanyRepository:
    return CompanyRepository(async_session, CompanyFromModels)


def get_companies_instance(async_session: AsyncSession = Depends(get_session)) -> CompaniesRepository:
    return CompaniesRepository(async_session, CompanyFromModels)
