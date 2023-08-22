import logging
from typing import List, Annotated
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound

from core.log_config import LoggingConfig
from libs.auth import get_current_user
from repository.invites import InviteRepository, InvitesRepository
from db.connect import get_session
from db.models import Action as ActionFromModels, User as UserFromModels, StatusActionForResponse
from schemas.users import PaginationParams
from schemas.auth import UserWithPermission
from schemas.action import ActionDetailResponse, ActionRequestModel
from routers.companies import user_permission_company
from routers.users import user_permission
from routers.join_requests import convert_to_response_model

router = APIRouter(prefix="/companies", tags=["invites"])
router_2 = APIRouter(prefix="/user-action", tags=["invites"])

LoggingConfig.configure_logging()


def get_invite_instance(async_session: AsyncSession = Depends(get_session)) -> InviteRepository:
    return InviteRepository(async_session, ActionFromModels)


def get_invites_instance(async_session: AsyncSession = Depends(get_session)) -> InvitesRepository:
    return InvitesRepository(async_session, ActionFromModels)


@router.post("/{company_id}/invitations", response_model=ActionDetailResponse,
             status_code=status.HTTP_201_CREATED)
async def send_invitation(
        company_id: int,
        invite_req_body: ActionRequestModel,
        current_user: Annotated[UserFromModels, Depends(get_current_user)],
        invite_instance: InviteRepository = Depends(get_invite_instance)
):
    new_invitation = await invite_instance.create(company_id=company_id, body=invite_req_body, user=current_user)
    logging.info(f"Created new new_invitation: {new_invitation.id})")
    invite_response_model = convert_to_response_model(new_invitation)
    return invite_response_model


@router.delete("/{company_id}/invitations/{invitation_id}", status_code=status.HTTP_202_ACCEPTED)
async def cancel_invitation(
        company_id: int,
        invitation_id: int,
        current_user: UserWithPermission = Depends(user_permission_company),
        invite_instance: InviteRepository = Depends(get_invite_instance)

):
    try:
        await invite_instance.delete(entity_id=invitation_id)
        logging.info(f"Invite with invite_id: {invitation_id} was deleted by user {current_user.username}")
        return {f"Invite with invite_id: {invitation_id} - deleted by user {current_user.username}"}

    except NoResultFound:
        logging.error("Tried to cancel non-existent invite")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found invite")


@router.patch("/{company_id}/invitations/{invitation_id}/response/{response_type}")
async def response_invitation(
        company_id: int,
        response_type: StatusActionForResponse,
        invitation_id: int,
        current_user: UserWithPermission = Depends(user_permission_company),
        invite_instance: InviteRepository = Depends(get_invite_instance)
):
    try:
        await invite_instance.response(action_id=invitation_id, body=response_type, company_id=company_id)
        logging.info(
            f"Invite with invite_id: {invitation_id} was {response_type.value} by member {current_user.username}")
        return {f"Invite with invite_id: {invitation_id} - {response_type.value} by member {current_user.username}"}
    except NoResultFound:
        logging.error("Tried to get non-existent invitation")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found invite")


@router_2.get("/user_id/me/invitations", response_model=List[ActionDetailResponse])
async def list_invites(
        user_id: int,
        current_user: UserWithPermission = Depends(user_permission),
        pagination: PaginationParams = Depends(),
        invites_instance: InvitesRepository = Depends(get_invites_instance)
):
    all_invites_response = []
    all_invites = await invites_instance.paginate_query(user_id=user_id, page=pagination.page,
                                                        page_size=pagination.page_size)
    for invite in all_invites:
        all_invites_response.append(convert_to_response_model(invite))

    logging.info("Got all invites by user {current_user.username}")
    return all_invites_response


@router.get("/{company_id}/invited-users", response_model=ActionDetailResponse,
             status_code=status.HTTP_201_CREATED)
async def get_invited_users(
        company_id: int,
        current_user: UserWithPermission = Depends(user_permission_company),
        invite_instance: InviteRepository = Depends(get_invite_instance)
):
    pass
    # new_invitation = await invite_instance.get(company_id=company_id, body=invite_req_body, user=current_user)
    # logging.info(f"Created new new_invitation: {new_invitation.id})")
    # invite_response_model = convert_to_response_model(new_invitation)
    # return invite_response_model
