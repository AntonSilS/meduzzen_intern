import logging
from typing import Annotated
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.exc import NoResultFound

from core.log_config import LoggingConfig
from libs.auth import get_current_user
from repository.join_requests import JoinRequestRepository
from db.models import User as UserFromModels, StatusActionForResponse
from schemas.action import ActionDetailResponse
from schemas.auth import UserWithPermission
from routers.companies import user_permission_company
from schemas.action import convert_to_response_model
from repository.service_repo_instance import get_join_request_instance

router = APIRouter(prefix="/companies", tags=["join-requests"])

LoggingConfig.configure_logging()


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

    return ActionDetailResponse.convert_to_response_model(new_join_request)


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
