from sqlalchemy import Column, Integer, String, Boolean, func, ARRAY, ForeignKey, Table, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import DateTime
from enum import Enum as PyEnum

from .connect import Base
from constants import USERNAME_MAXLENGTH, EMAIl_MAXLENGTH, USERSTATUS_MAXLENGTH, \
    COMPANY_NAME_MAXLENGTH, DESCRIPTION_MAXLENGTH, QUIZ_DESCRIPTION_MAXLENGTH, QUIZ_NAME_MAXLENGTH, \
    QUESTION_TEXT_MAXLENGTH, ANSWER_TEXT_MAXLENGTH

member_company_association = Table(
    "user_company", Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("company_id", Integer, ForeignKey("company.id")))

admin_company_association = Table(
    "admin_company", Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("company_id", Integer, ForeignKey("company.id")))


class StatusActionForResponse(str, PyEnum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class StatusActionWithSent(str, PyEnum):
    SENT = "sent"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class TypeAction(str, PyEnum):
    INVITE = "invite"
    JOIN_REQUEST = "join_request"


class Action(Base):
    __tablename__ = 'actions'

    id = Column(Integer, primary_key=True, index=True)
    type_action = Column(Enum(TypeAction))
    company_id = Column(Integer, ForeignKey('company.id'))
    sender_id = Column(Integer, ForeignKey('users.id'))
    recipient_id = Column(Integer, ForeignKey('users.id'))
    status_action = Column(Enum(StatusActionWithSent), default=StatusActionWithSent.SENT)
    company = relationship("Company", back_populates="actions")
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_actions")
    recipient = relationship("User", foreign_keys=[recipient_id], back_populates="received_actions")
    created = Column(DateTime, default=func.now())
    updated = Column(DateTime, default=func.now(), onupdate=func.now())


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(USERNAME_MAXLENGTH), nullable=False)
    email = Column(String(EMAIl_MAXLENGTH), nullable=False, unique=True)
    phones = Column(ARRAY(String), default=list)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    admin_of_companies = relationship("Company", secondary=admin_company_association, back_populates="admins",
                                      cascade="save-update, merge")
    status = Column(String(USERSTATUS_MAXLENGTH), default="registered")
    owner_of_companies = relationship("Company", back_populates="owner")
    member_of_companies = relationship("Company", secondary=member_company_association, back_populates="members",
                                       cascade="save-update, merge")
    sent_actions = relationship("Action", foreign_keys=[Action.sender_id], back_populates="sender")
    received_actions = relationship("Action", foreign_keys=[Action.recipient_id],
                                    back_populates="recipient")
    created = Column(DateTime, default=func.now())
    updated = Column(DateTime, default=func.now(), onupdate=func.now())


class Company(Base):
    __tablename__ = "company"
    id = Column(Integer, primary_key=True)
    company_name = Column(String(COMPANY_NAME_MAXLENGTH), nullable=False, unique=True)
    description = Column(String(DESCRIPTION_MAXLENGTH), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="owner_of_companies")
    members = relationship("User", secondary=member_company_association, back_populates="member_of_companies",
                           cascade="save-update, merge")
    admins = relationship("User", secondary=admin_company_association, back_populates="admin_of_companies",
                          cascade="save-update, merge")
    actions = relationship("Action", back_populates="company", cascade="all, delete-orphan")
    visible = Column(Boolean, default=True)
    quizzes = relationship("Quiz", back_populates="company", cascade="all, delete-orphan")
    created = Column(DateTime, default=func.now())
    updated = Column(DateTime, default=func.now(), onupdate=func.now())


class Quiz(Base):
    __tablename__ = 'quizzes'
    id = Column(Integer, primary_key=True)
    name = Column(String(QUIZ_NAME_MAXLENGTH), nullable=False)
    description = Column(String(QUIZ_DESCRIPTION_MAXLENGTH))
    frequency = Column(Integer, default=0)
    company_id = Column(Integer, ForeignKey('company.id'))
    company = relationship('Company', back_populates='quizzes')
    questions = relationship('Question', back_populates='quiz', cascade="all, delete-orphan")
    created = Column(DateTime, default=func.now())
    updated = Column(DateTime, default=func.now(), onupdate=func.now())


class Question(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True)
    text = Column(String(QUESTION_TEXT_MAXLENGTH))
    quiz_id = Column(Integer, ForeignKey('quizzes.id'))
    quiz = relationship('Quiz', back_populates='questions')
    answers = relationship('Answer', back_populates='question', cascade="all, delete-orphan")
    created = Column(DateTime, default=func.now())
    updated = Column(DateTime, default=func.now(), onupdate=func.now())


class Answer(Base):
    __tablename__ = 'answers'
    id = Column(Integer, primary_key=True)
    text = Column(String(ANSWER_TEXT_MAXLENGTH))
    is_correct = Column(Boolean, default=False)
    question_id = Column(Integer, ForeignKey('questions.id'))
    question = relationship('Question', back_populates='answers')
    created = Column(DateTime, default=func.now())
    updated = Column(DateTime, default=func.now(), onupdate=func.now())
