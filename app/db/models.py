from sqlalchemy import Column, Integer, String, Boolean, func, ARRAY
from sqlalchemy.sql.sqltypes import DateTime

from .connect import Base
from constants import USERNAME_MAXLENGTH, EMAIl_MAXLENGTH, USERSTATUS_MAXLENGTH


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(USERNAME_MAXLENGTH), nullable=False)
    email = Column(String(EMAIl_MAXLENGTH), nullable=False, unique=True)
    phones = Column(ARRAY(String), default=list)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    status = Column(String(USERSTATUS_MAXLENGTH), default="registered")
    created = Column(DateTime, default=func.now())
    updated = Column(DateTime, default=func.now(), onupdate=func.now())
