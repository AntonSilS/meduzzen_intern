from datetime import datetime
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional

from app.constants import USERNAME_MAXLENGTH, EMAIl_MAXLENGTH, PASSWORD_MINLENGTH, USERSTATUS_MAXLENGTH


class User(BaseModel):
    username: str
    email: str


class UserDetailResponse(User):
    id: int
    phones: List[str] = []
    is_active: bool
    status: str
    created: datetime
    updated: datetime

    class Config:
        orm_mode = True


class UserUpdateRequestModel(BaseModel):
    username: Optional[str] = Field(None, max_length=USERNAME_MAXLENGTH)
    email: Optional[str] = Field(None, max_length=EMAIl_MAXLENGTH)
    phones: Optional[List[str]]
    password: Optional[str] = Field(None, min_length=PASSWORD_MINLENGTH)
    is_active: Optional[bool] = Field(True)
    status: Optional[str] = Field(None, max_length=USERSTATUS_MAXLENGTH)


class UsersListResponse(BaseModel):
    users: List[User]

    class Config:
        orm_mode = True


class SignInRequestModel(BaseModel):
    email: EmailStr = Field(max_length=EMAIl_MAXLENGTH)
    password: str = Field(min_length=PASSWORD_MINLENGTH)


class SignUpRequestModel(SignInRequestModel):
    username: str = Field(max_length=USERNAME_MAXLENGTH)



