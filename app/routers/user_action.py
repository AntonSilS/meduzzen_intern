import logging
from typing import List
from fastapi import Depends

from repository.invites import InvitesRepository
from repository.join_requests import JoinRequestsRepository
from schemas.action import ActionDetailResponse
from schemas.users import PaginationParams
from schemas.auth import UserWithPermission
from utils.service_permission import user_permission
from repository.service_repo_instance import get_join_requests_instance, get_invites_instance

from fastapi import APIRouter

router = APIRouter(prefix="/user-action", tags=["user-action"])


@router.get("/user_id/me/join-requests", response_model=List[ActionDetailResponse])
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
        action_response = ActionDetailResponse.convert_to_response_model(request)
        all_requests_response.append(action_response)

    logging.info("Got all join requests by user {current_user.username}")
    return all_requests_response


@router.get("/user_id/me/invitations", response_model=List[ActionDetailResponse])
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
        all_invites_response.append(ActionDetailResponse.convert_to_response_model(invite))

    logging.info("Got all invites by user {current_user.username}")
    return all_invites_response


