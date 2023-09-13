import logging
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.exc import NoResultFound

from core.log_config import LoggingConfig
from repository.answers import AnswerRepository

from repository.questions import QuestionRepository
from repository.quizzes import QuizRepository
from schemas.auth import UserWithPermission

from repository.service_repo_instance import get_quiz_instance, get_answer_instance, get_question_instance
from schemas.quiz import QuestionUpdateRequestModel, QuestionResponseModel, QuestionRequestModel

from utils.service_permission import user_permission_admin_owner
from db.models import Question as QuestionFormModels

router = APIRouter(prefix="/companies", tags=["questions"])

LoggingConfig.configure_logging()


@router.post("/{company_id}/quizzes/{quiz_id}/questions", response_model=QuestionResponseModel,
             status_code=status.HTTP_201_CREATED)
async def create_question(
        company_id: int,
        quiz_id: int,
        question_body: QuestionRequestModel,
        current_user: UserWithPermission = Depends(user_permission_admin_owner),
        answer_instance: AnswerRepository = Depends(get_answer_instance),
        question_instance: QuestionRepository = Depends(get_question_instance),
        quiz_instance: QuizRepository = Depends(get_quiz_instance)
):

    new_question = await question_instance.create(quiz_id=quiz_id, question_body=question_body, answers_repo=answer_instance)

    updated_quiz = await quiz_instance.add_single_question(quiz_id=quiz_id, question=new_question)
    logging.info(f"Created new question with id: {new_question.id} in quiz with id: {quiz_id}")
    load_question = await question_instance.get_entity_with_loading_field(QuestionFormModels, new_question.id,
                                                                          "answers")
    question_response = QuestionResponseModel.convert_question_db_to_response(question_db_model=load_question)
    return question_response


@router.put("/{company_id}/quizzes/{quiz_id}/questions/{question_id}", response_model=QuestionResponseModel)
async def update_question(
        company_id: int,
        quiz_id: int,
        question_id: int,
        question_update_body: QuestionUpdateRequestModel,
        current_user: UserWithPermission = Depends(user_permission_admin_owner),
        question_instance: QuestionRepository = Depends(get_question_instance)
):
    try:
        updated_question = await question_instance.update(entity_id=question_id, body=question_update_body)

        logging.info(f"Updated question with id: {question_id} in quiz with id: {quiz_id}")
        load_question = await question_instance.get_entity_with_loading_field(QuestionFormModels, updated_question.id,
                                                                              "answers")
        question_response = QuestionResponseModel.convert_question_db_to_response(question_db_model=load_question)
        return question_response

    except NoResultFound:
        logging.error("Tried to get non-existent question")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found question")


@router.delete("/{company_id}/quizzes/{quiz_id}/questions/{question_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_question(
        company_id: int,
        quiz_id: int,
        question_id: int,
        current_user: UserWithPermission = Depends(user_permission_admin_owner),
        question_instance: QuestionRepository = Depends(get_question_instance),
        quiz_instance: QuizRepository = Depends(get_quiz_instance)
):
    try:
        if await quiz_instance.validate(quiz_id=quiz_id):
            await question_instance.delete(entity_id=question_id)
            logging.info(f"Deleted question with id: {question_id}")
            return {f"Deleted question with id: {question_id}"}
        else:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Quiz should have at least two questions. Deleting this question is forbidden")

    except NoResultFound:
        logging.error("Tried to get non-existent question")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found question")
