import logging
from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, NoResultFound

from core.log_config import LoggingConfig
from repository.users import Users, User
from db.connect import get_session
from schemas.users import SignUpRequestModel, UserUpdateRequestModel, UserStatus, UserDetailResponse, PaginationParams
from db.models import User as UserFromModels

router = APIRouter(prefix="/users")

LoggingConfig.configure_logging()


@router.get("/", response_model=List[UserDetailResponse])
async def get_users(pagination: PaginationParams = Depends(), async_session: AsyncSession = Depends(get_session)):
    all_users = await Users.paginate_query(UserFromModels, pagination.page, pagination.page_size, async_session)
    logging.info("Got all users")
    return all_users


@router.get("/{user_id}", response_model=UserDetailResponse)
async def get_user(user_id: int, async_session: AsyncSession = Depends(get_session)):
    try:
        cur_user = await User.get(async_session, user_id)
        logging.info(f"Got users: {cur_user.username} (id: {cur_user.id})")
        return cur_user

    except NoResultFound:
        logging.error("Tried to get non-existent user")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found user")


@router.post("/", response_model=UserDetailResponse,
             status_code=status.HTTP_201_CREATED)
async def create_user(user_req_body: SignUpRequestModel, async_session: AsyncSession = Depends(get_session)):
    try:
        new_user = await User.create(async_session, user_req_body)
        logging.info(f"Created new user: {new_user.username} (id: {new_user.id})")
        return new_user

    except IntegrityError:
        logging.error("Tried to create existent user")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")


@router.put("/{user_id}", response_model=UserDetailResponse)
async def update_user(user_id: int, user_req_body: UserUpdateRequestModel,
                      async_session: AsyncSession = Depends(get_session)):
    try:
        user = await User.update(async_session, user_req_body, user_id)
        logging.info(f"Updated user: {user.username} (id: {user.id})")
        return user

    except NoResultFound:
        logging.error("Tried to get non-existent user")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found user")

    except IntegrityError:
        logging.error("Tried to change fields with non-unique name or email")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="User with such name or email is already exist")


@router.patch("/{user_id}", response_model=UserDetailResponse)
async def update_status_user(user_id: int, user_req_body: UserStatus,
                             async_session: AsyncSession = Depends(get_session)):
    try:
        user = await User.update(async_session, user_req_body, user_id)
        logging.info(f"Updated status of user: {user.username} (id: {user.id})")
        return user

    except NoResultFound:
        logging.error("Tried to get non-existent user")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found user")


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, async_session: AsyncSession = Depends(get_session)):
    try:
        logging.info(f"User with user_id: {user_id} was deleted")
        await User.delete(async_session, user_id)
        return {f"{user_id}": "deleted"}

    except NoResultFound:
        logging.error("Tried to get non-existent user")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found user")
