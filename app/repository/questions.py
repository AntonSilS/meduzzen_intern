from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import joinedload, subqueryload

from db.models import Answer as AnswerFromModel, Question as QuestionFromModel, User as UserFromModels, \
    Quiz as QuizFromModels, TypeAction
from schemas.quiz import QuizRequestModel, AnswerRequestModel, QuestionRequestModel, QuizUpdateRequestModel
from .base import BaseEntitiesRepository, BaseEntityRepository


class QuestionsRepository(BaseEntitiesRepository):
    pass


class QuestionRepository(BaseEntityRepository):
    pass