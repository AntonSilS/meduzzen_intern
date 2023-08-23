from datetime import datetime
from pydantic import BaseModel

from db.models import StatusActionWithSent, TypeAction, Action as ActionFromModels


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

    @classmethod
    def convert_to_response_model(cls, db_model: ActionFromModels):
        return cls(
            type_action=db_model.type_action,
            id=db_model.id,
            company=db_model.company.company_name,
            sender=db_model.sender.username,
            status_action=db_model.status_action,
            created=db_model.created,
            updated=db_model.updated
        )


class ActionRequestModel(BaseModel):
    recipient_id: int


def convert_to_response_model(db_model: ActionFromModels) -> ActionDetailResponse:
    return ActionDetailResponse(
        type_action=db_model.type_action,
        id=db_model.id,
        company=db_model.company.company_name,
        sender=db_model.sender.username,
        status_action=db_model.status_action,
        created=db_model.created,
        updated=db_model.updated
    )
