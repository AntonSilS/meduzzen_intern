from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

from constants import COMPANY_NAME_MAXLENGTH, DESCRIPTION_MAXLENGTH


class CompanyBase(BaseModel):
    id: int
    company_name: str


class CompanyResponseBase(CompanyBase):
    id: int
    company_name: str
    created: datetime

    class Config:
        orm_mode = True


class CompanyDetailResponse(CompanyResponseBase):
    description: str
    owner_id: int
    visible: bool
    updated: datetime


class CompanyRequestModel(BaseModel):
    company_name: str = Field(max_length=COMPANY_NAME_MAXLENGTH)
    description: str = Field(max_length=DESCRIPTION_MAXLENGTH)


class CompanyUpdateRequestModel(BaseModel):
    company_name: Optional[str] = Field(None, max_length=COMPANY_NAME_MAXLENGTH)
    description: Optional[str] = Field(None, max_length=DESCRIPTION_MAXLENGTH)
    visible: Optional[bool] = None
