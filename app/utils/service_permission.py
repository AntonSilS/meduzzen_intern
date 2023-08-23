import logging
from typing import Annotated
from fastapi import Depends, HTTPException

from db.models import User as UserFromModels
from libs.auth import get_current_user


def is_superuser(current_user: UserFromModels) -> bool:
    return current_user.is_superuser


def user_permission(current_user: Annotated[UserFromModels, Depends(get_current_user)], user_id: int) -> UserFromModels:
    if is_superuser(current_user) or current_user.id == user_id:
        logging.error(f"User with: user_id - {current_user.id} and name - {current_user.username} got permission")
        return current_user
    else:
        raise HTTPException(status_code=403, detail="Forbidden action")


def user_permission_company(current_user: Annotated[UserFromModels, Depends(get_current_user)],
                            company_id: int) -> UserFromModels:
    if is_superuser(current_user) or company_id in [comp.id for comp in current_user.owner_of_companies]:
        logging.error(f"User with: user_id - {current_user.id} and name - {current_user.username} got permission")
        return current_user
    else:
        raise HTTPException(status_code=403, detail="Forbidden action")


def user_permission_member(current_user: Annotated[UserFromModels, Depends(get_current_user)],
                           company_id: int) -> UserFromModels:
    if is_superuser(current_user) or company_id in [comp.id for comp in current_user.member_of_companies]:
        logging.error(f"User with: user_id - {current_user.id} and name - {current_user.username} got permission")
        return current_user
    else:
        raise HTTPException(status_code=403, detail="Forbidden action")
