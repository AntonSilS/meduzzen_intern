from datetime import datetime
from pydantic import BaseModel, Field, root_validator
from typing import List, Optional, Dict

from sqlalchemy import inspect

from constants import ANSWER_TEXT_MAXLENGTH, QUESTION_TEXT_MAXLENGTH, QUIZ_NAME_MAXLENGTH, QUIZ_DESCRIPTION_MAXLENGTH
from db.models import Quiz as QuizFromModels, Base as BaseFromModels, Question as QuestionFromModel, \
    Answer as AnswerFromModel


class ResponseConverter:
    @staticmethod
    def get_attrs_sqlalchemy(sqlalchemy_obj: BaseFromModels) -> Dict:
        sqlalchemy_attrs = {c.key: getattr(sqlalchemy_obj, c.key) for c in inspect(sqlalchemy_obj).mapper.column_attrs}
        return sqlalchemy_attrs

    @classmethod
    def convert(cls, sqlalchemy_attrs: Dict) -> BaseModel:
        instance = cls(**sqlalchemy_attrs)
        return instance


class AnswerRequestModel(BaseModel):
    text: str = Field(max_length=ANSWER_TEXT_MAXLENGTH)
    is_correct: bool = Field(default=False)


class QuestionRequestModel(BaseModel):
    text: str = Field(max_length=QUESTION_TEXT_MAXLENGTH)
    answers: List[AnswerRequestModel]

    @root_validator(skip_on_failure=True)
    def check_valid_question(cls, values):
        answers = values.get('answers', [])
        if len(answers) < 2:
            raise ValueError("A question should have at least 2 answers")
        if sum(answer.is_correct for answer in answers) < 1:
            raise ValueError("There should be at least 1 correct answer")
        return values


class QuizRequestModel(BaseModel):
    name: str = Field(max_length=QUIZ_NAME_MAXLENGTH)
    description: str = Field(max_length=QUIZ_DESCRIPTION_MAXLENGTH)
    questions: List[QuestionRequestModel]

    @root_validator(skip_on_failure=True)
    def check_valid_quiz(cls, values):
        questions = values.get('questions', [])
        if len(questions) < 2:
            raise ValueError("A quiz should have at least 2 questions")
        return values


class AnswerResponseModel(BaseModel, ResponseConverter):
    id: int
    text: str
    is_correct: bool
    created: datetime
    updated: datetime

    class Config:
        orm_mode = True

    @classmethod
    def convert_answer_db_to_response(cls, answer_db_model: AnswerFromModel):
        attrs_answers_db = cls.get_attrs_sqlalchemy(sqlalchemy_obj=answer_db_model)
        return AnswerResponseModel.convert(sqlalchemy_attrs=attrs_answers_db)


class QuestionResponseModel(BaseModel, ResponseConverter):
    id: int
    text: str
    created: datetime
    updated: datetime
    answers: List[AnswerResponseModel]

    class Config:
        orm_mode = True

    @classmethod
    def convert_question_db_to_response(cls, question_db_model: QuestionFromModel):
        answers_pydantic = []
        for answer in question_db_model.answers:
            attrs_answers_db = cls.get_attrs_sqlalchemy(sqlalchemy_obj=answer)
            answers_pydantic.append(AnswerResponseModel.convert(sqlalchemy_attrs=attrs_answers_db))
        attrs_question_db = cls.get_attrs_sqlalchemy(sqlalchemy_obj=question_db_model)
        attrs_question_db["answers"] = answers_pydantic
        question_response = QuestionResponseModel.convert(sqlalchemy_attrs=attrs_question_db)
        return question_response


class QuizBaseResponse(BaseModel):
    id: int
    name: str
    frequency: int = Field(default=0)
    company_id: int
    created: datetime

    class Config:
        orm_mode = True


class QuizResponseModel(QuizBaseResponse, ResponseConverter):
    description: str
    updated: datetime
    questions: List[QuestionResponseModel]

    @classmethod
    def convert_quiz_db_to_response(cls, quiz_db_model: QuizFromModels):
        questions_pydantic = []
        for question in quiz_db_model.questions:
            answers_pydantic = []
            for answer in question.answers:
                answers_pydantic.append(AnswerResponseModel.convert_answer_db_to_response(answer_db_model=answer))
            attrs_question_db = cls.get_attrs_sqlalchemy(sqlalchemy_obj=question)
            attrs_question_db["answers"] = answers_pydantic
            question_response = QuestionResponseModel.convert(sqlalchemy_attrs=attrs_question_db)
            questions_pydantic.append(question_response)
        attrs_quiz_db = cls.get_attrs_sqlalchemy(sqlalchemy_obj=quiz_db_model)
        attrs_quiz_db["questions"] = questions_pydantic
        quiz_response = cls.convert(attrs_quiz_db)
        quiz_response.questions = questions_pydantic
        return quiz_response


class QuizUpdateRequestModel(BaseModel):
    name: Optional[str] = Field(None, max_length=QUIZ_NAME_MAXLENGTH)
    description: Optional[str] = Field(None, max_length=QUIZ_DESCRIPTION_MAXLENGTH)


class QuestionUpdateRequestModel(BaseModel):
    text: Optional[str] = Field(None, max_length=QUESTION_TEXT_MAXLENGTH)


class AnswerUpdateRequestModel(BaseModel):
    text: Optional[str] = Field(None, max_length=QUESTION_TEXT_MAXLENGTH)
    is_correct: Optional[bool] = None
