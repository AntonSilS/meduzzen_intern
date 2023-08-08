from datetime import datetime
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional

from constants import USERNAME_MAXLENGTH, PASSWORD_MINLENGTH, USERSTATUS_MAXLENGTH


class PaginationParams(BaseModel):
    page: int = 1
    page_size: int = 5


class UserBase(BaseModel):
    id: int
    username: str
    email: str


class UserDetailResponse(UserBase):
    phones: List[str] = []
    status: str = Field(default="registered")
    is_active: bool = Field(alias="active", default=False)
    created: datetime
    updated: datetime

    class Config:
        orm_mode = True


class UserStatus(BaseModel):
    status: str = Field(max_length=USERSTATUS_MAXLENGTH, default="registered")


class UserUpdateRequestModel(BaseModel):
    username: Optional[str] = Field(None, max_length=USERNAME_MAXLENGTH)
    phones: Optional[List[str]] = None
    password: Optional[str] = Field(None, min_length=PASSWORD_MINLENGTH)
    is_active: Optional[bool] = None
    status: Optional[str] = Field(None, max_length=USERSTATUS_MAXLENGTH)


class SignInRequestModel(BaseModel):
    email: EmailStr
    password: str = Field(min_length=PASSWORD_MINLENGTH)


class SignUpRequestModel(SignInRequestModel):
    username: str = Field(max_length=USERNAME_MAXLENGTH)