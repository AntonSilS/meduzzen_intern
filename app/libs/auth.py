from datetime import datetime, timedelta
from typing import Annotated, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from db.connect import get_session
from db.models import User as UserFromModels
from schemas.users import SignUpRequestModel
from utils.service_config import settings
from repository.users import UserRepository as UserFromRepository
from .tokens import VerifyCustomToken, VerifyAuth0Token

token_auth_scheme = HTTPBearer()


def create_access_token(data: Dict[str, str], expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.EXPIRE_TOKEN)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return encoded_jwt


def get_login(payload: Dict[str, str], token_mark: str, credentials_exception: HTTPException) -> str:
    if token_mark == "auth0_mark":
        login = payload.get("email")

    elif token_mark == "custom_token_mark":
        login = payload.get("sub")

    if login is None:
        raise credentials_exception
    return login


async def get_current_user(
        token: Annotated[str, Depends(token_auth_scheme)],
        async_session: AsyncSession = Depends(get_session)
) -> UserFromModels:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload_with_mark = VerifyCustomToken(token).verify()
    if payload_with_mark.get("status"):
        payload_with_mark = VerifyAuth0Token(token).verify()

        if payload_with_mark.get("status"):
            raise credentials_exception

    payload = payload_with_mark.get("payload")
    token_mark = payload_with_mark.get("mark")

    login = get_login(payload=payload, token_mark=token_mark, credentials_exception=credentials_exception)

    current_user: UserFromModels = await UserFromRepository(async_session, UserFromModels).get_user_by_login(login=login)
    if current_user is None and token_mark == "auth0_mark":
        user_model = SignUpRequestModel(username=login, email=login, password=login)
        current_user: UserFromModels = await UserFromRepository(async_session).create(body=user_model)
    elif current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user
