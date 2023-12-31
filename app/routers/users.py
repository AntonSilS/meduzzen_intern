import logging
from typing import List, Annotated
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.exc import IntegrityError, NoResultFound

from core.log_config import LoggingConfig
from db.models import User as UserFromModels
from repository.users import UsersRepository, UserRepository
from libs.auth import get_current_user
from schemas.users import UserUpdateRequestModel, UserStatus, UserDetailResponse, PaginationParams, UserBase, \
    UserResponseBase
from schemas.auth import UserWithPermission
from repository.service_repo_instance import get_user_instance, get_users_instance
from utils.service_permission import user_permission

router = APIRouter(prefix="/users", tags=["user"])
LoggingConfig.configure_logging()


@router.get("/", response_model=List[UserResponseBase])
async def get_users(
        current_user: Annotated[UserFromModels, Depends(get_current_user)],
        pagination: PaginationParams = Depends(),
        users_instance: UsersRepository = Depends(get_users_instance),

):
    all_users = await users_instance.paginate_query(entity=UserFromModels, page=pagination.page,
                                                    page_size=pagination.page_size)
    logging.info("Got all users")
    return all_users


@router.get("/{user_id}", response_model=UserDetailResponse)
async def get_user(
        current_user: Annotated[UserFromModels, Depends(get_current_user)],
        user_id: int,
        user_instance: UserRepository = Depends(get_user_instance)
):
    try:
        cur_user = await user_instance.get(entity_id=user_id)
        logging.info(f"Got users: {cur_user.username} (id: {cur_user.id})")
        return cur_user

    except NoResultFound:
        logging.error("Tried to get non-existent user")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found user")


@router.put("/{user_id}", response_model=UserDetailResponse)
async def update_user(
        user_id: int,
        user_req_body: UserUpdateRequestModel,
        current_user: UserWithPermission = Depends(user_permission),
        user_instance: UserRepository = Depends(get_user_instance)
):
    try:
        user = await user_instance.update(body=user_req_body, user_id=user_id)
        logging.info(f"Updated user: {user.username} (id: {user.id})")
        return user

    except NoResultFound:
        logging.error("Tried to get non-existent user")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found user")

    except IntegrityError:
        logging.error("Tried to change fields with non-unique name or email")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with such name or email already exists")


@router.patch("/{user_id}", response_model=UserDetailResponse)
async def update_status_user(
        user_id: int,
        user_req_body: UserStatus,
        current_user: UserWithPermission = Depends(user_permission),
        user_instance: UserRepository = Depends(get_user_instance)
):
    try:
        user = await user_instance.update_status(body=user_req_body, user_id=user_id)
        logging.info(f"Updated status of user: {user.username} (id: {user.id})")
        return user

    except NoResultFound:
        logging.error("Tried to get non-existent user")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found user")


@router.delete("/{user_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_user(
        user_id: int,
        current_user: UserWithPermission = Depends(user_permission),
        user_instance: UserRepository = Depends(get_user_instance),
):
    try:
        await user_instance.delete(entity_id=user_id)
        logging.info(f"User with user_id: {user_id} was deleted")
        return {f"User with id:{user_id} - deleted"}

    except NoResultFound:
        logging.error("Tried to get non-existent user")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found user")


@router.get("/me/", response_model=UserDetailResponse)
async def read_users_me(
        current_user: Annotated[UserFromModels, Depends(get_current_user)]
):
    return current_user
