import logging
from typing import List, Annotated
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound

from core.log_config import LoggingConfig
from libs.auth import get_current_user
from repository.join_requests import JoinRequestRepository, JoinRequestsRepository
from db.connect import get_session
from db.models import User as UserFromModels, StatusActionForResponse, Action as ActionFromModels
from schemas.action import ActionDetailResponse
from schemas.users import PaginationParams
from schemas.auth import UserWithPermission

from routers.companies import user_permission_company
from routers.users import user_permission

router = APIRouter(prefix="/companies", tags=["join-requests"])
router_2 = APIRouter(prefix="/user-action", tags=["join-requests"])

LoggingConfig.configure_logging()


def convert_to_response_model(db_model: ActionFromModels) -> ActionDetailResponse:
    return ActionDetailResponse(
        type_action=db_model.type_action,
        id=db_model.id,
        company=db_model.company.company_name,
        sender=db_model.sender.username,
        status_action=db_model.status_action,
        created=db_model.created,
        updated=db_model.updated
    )


def get_join_request_instance(async_session: AsyncSession = Depends(get_session)) -> JoinRequestRepository:
    return JoinRequestRepository(async_session, ActionFromModels)


def get_join_requests_instance(async_session: AsyncSession = Depends(get_session)) -> JoinRequestsRepository:
    return JoinRequestsRepository(async_session, ActionFromModels)


@router.post("/{company_id}/join-requests", response_model=ActionDetailResponse,
             status_code=status.HTTP_201_CREATED)
async def send_join_request(
        company_id: int,
        # join_request_req_body: ActionRequestModel,
        current_user: Annotated[UserFromModels, Depends(get_current_user)],
        join_request_instance: JoinRequestRepository = Depends(get_join_request_instance)
):
    new_join_request = await join_request_instance.create(company_id=company_id, user=current_user)
    logging.info(f"Created new join request: {new_join_request.id})")

    return convert_to_response_model(new_join_request)



@router.delete("/{company_id}/join-requests/{join_requests_id}")
async def cancel_request(
        company_id: int,
        join_requests_id: int,
        current_user: UserWithPermission = Depends(user_permission_company),
        join_request_instance: JoinRequestRepository = Depends(get_join_request_instance)

):
    try:
        await join_request_instance.delete(entity_id=join_requests_id)
        logging.info(f"Join request with id: {join_requests_id} was deleted by user {current_user.username}")
        return {f"Join request with id: {join_requests_id} - deleted by user {current_user.username}"}

    except NoResultFound:
        logging.error("Tried to cancel non-existent join request")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found invite")


@router.post("/{company_id}/join-requests/{join_requests_id}/response")
async def response_request(
        company_id: int,
        response_type: StatusActionForResponse,
        join_requests_id: int,
        current_user: UserWithPermission = Depends(user_permission_company),
        join_request_instance: JoinRequestRepository = Depends(get_join_request_instance)
):
    try:
        await join_request_instance.response(action_id=join_requests_id, body=response_type, company_id=company_id)
        logging.info(
            f"Join request with id: {join_requests_id} was {response_type.value} by member {current_user.username}")
        return {f"Join request with id: {join_requests_id} - {response_type.value} by member {current_user.username}"}
    except NoResultFound:
        logging.error("Tried to get non-existent join request")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found invite")


@router_2.get("/user_id/me/join-requests", response_model=List[ActionDetailResponse])
async def list_requests(
        user_id: int,
        current_user: UserWithPermission = Depends(user_permission),
        pagination: PaginationParams = Depends(),
        join_requests_instance: JoinRequestsRepository = Depends(get_join_requests_instance)
):
    all_requests_response = []
    all_requests = await join_requests_instance.paginate_query(user_id=user_id, page=pagination.page,
                                                               page_size=pagination.page_size)
    for request in all_requests:
        action_response = convert_to_response_model(request)
        all_requests_response.append(action_response)

    logging.info("Got all join requests by user {current_user.username}")
    return all_requests_response
