from datetime import datetime
from pydantic import BaseModel

from db.models import StatusActionWithSent, TypeAction


class ActionBase(BaseModel):
    id: int


class ActionDetailResponse(ActionBase):
    type_action: TypeAction
    company: str
    sender: str
    status_action: StatusActionWithSent
    created: datetime
    updated: datetime

    class Config:
        orm_mode = True


class ActionRequestModel(BaseModel):
    recipient_id: int

