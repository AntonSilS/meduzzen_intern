from sqlalchemy import Column, Integer, String, Boolean, func, ARRAY, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import DateTime

from .connect import Base
from constants import USERNAME_MAXLENGTH, EMAIl_MAXLENGTH, USERSTATUS_MAXLENGTH, \
    COMPANY_NAME_MAXLENGTH, DESCRIPTION_MAXLENGTH

user_company_association = Table(
    "user_company", Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("company_id", Integer, ForeignKey("company.id")))


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
    owner_of_companies = relationship("Company", back_populates="owner")
    member_of_companies = relationship("Company", secondary=user_company_association, back_populates="members")
    created = Column(DateTime, default=func.now())
    updated = Column(DateTime, default=func.now(), onupdate=func.now())


class Company(Base):
    __tablename__ = "company"
    id = Column(Integer, primary_key=True)
    company_name = Column(String(COMPANY_NAME_MAXLENGTH), nullable=False, unique=True)
    description = Column(String(DESCRIPTION_MAXLENGTH), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="owner_of_companies")
    members = relationship("User", secondary=user_company_association, back_populates="member_of_companies")
    visible = Column(Boolean, default=True)
    created = Column(DateTime, default=func.now())
    updated = Column(DateTime, default=func.now(), onupdate=func.now())
