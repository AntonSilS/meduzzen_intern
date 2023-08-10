import logging
from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from libs.auth import create_access_token
from libs.hash import Hash
from db.connect import get_session
from core.log_config import LoggingConfig
from routers.users import get_user_instance
from schemas.auth import Token
from schemas.users import SignInRequestModel, UserDetailResponse, SignUpRequestModel
from db.models import User as UserFromModels
from repository.users import UserRepository as UserFromRepository
from utils.service_config import settings


router = APIRouter(prefix="/auth", tags=["auth"])

LoggingConfig.configure_logging()


@router.post("/signin", response_model=Token)
async def sign_in(
        sign_in_body: Annotated[SignInRequestModel, Depends()],
        async_session: AsyncSession = Depends(get_session)
):
    credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    current_user: UserFromModels = await UserFromRepository(async_session, UserFromModels).get_user_by_login(sign_in_body.email)
    if not current_user:
        raise credentials_exception
    if not Hash.verify_password(sign_in_body.password, current_user.password):
        raise credentials_exception
    access_token_expires = timedelta(minutes=settings.EXPIRE_TOKEN)
    access_token = create_access_token(
        data={"sub": current_user.email},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/signup", response_model=UserDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
        user_req_body: SignUpRequestModel,
        user_instance: UserFromRepository = Depends(get_user_instance)
):
    try:
        new_user = await user_instance.create(body=user_req_body)
        logging.info(f"Created new user: {new_user.username} (id: {new_user.id})")
        return new_user

    except IntegrityError:
        logging.error("Tried to create an existing user")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
