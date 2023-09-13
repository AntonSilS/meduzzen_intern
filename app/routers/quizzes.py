import logging
from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.exc import NoResultFound

from core.log_config import LoggingConfig
from repository.answers import AnswerRepository

from repository.questions import QuestionRepository
from repository.quizzes import QuizRepository, QuizzesRepository
from schemas.auth import UserWithPermission

from repository.service_repo_instance import get_quiz_instance, get_answer_instance, get_question_instance, \
    get_quizzes_instance
from schemas.quiz import QuizRequestModel, QuizUpdateRequestModel, QuizResponseModel, QuizBaseResponse
from schemas.users import PaginationParams
from utils.service_permission import user_permission_admin_owner
from db.models import Quiz as QuizFromModels

router = APIRouter(prefix="/companies", tags=["quizzes"])

LoggingConfig.configure_logging()


@router.get("/{company_id}/quizzes", response_model=List[QuizBaseResponse])
async def get_quizzes(
        company_id: int,
        current_user: UserWithPermission = Depends(user_permission_admin_owner),
        pagination: PaginationParams = Depends(),
        quizzes_instance: QuizzesRepository = Depends(get_quizzes_instance)
):
    all_quizzes = await quizzes_instance.paginate_query(company_id=company_id, page=pagination.page, page_size=pagination.page_size)

    logging.info(f"Got all quizzes by user id: {current_user.id} in company with id: {company_id}")
    return all_quizzes


@router.get("/{company_id}/quizzes/{quiz_id}", response_model=QuizResponseModel)
async def get_quiz(
        company_id: int,
        quiz_id: int,
        # quiz_update_body: QuizRequestModel,
        current_user: UserWithPermission = Depends(user_permission_admin_owner),
        quiz_instance: QuizRepository = Depends(get_quiz_instance)
):
    quiz = await quiz_instance.get(entity_id=quiz_id)
    quiz_with_loaded_field = await quiz_instance.get_quiz_with_questions(quiz_id=quiz_id)
    logging.info(f"Got quiz with id: {quiz_id} by user with id {current_user}")
    quiz_response = QuizResponseModel.convert_quiz_db_to_response(quiz_db_model=quiz_with_loaded_field)
    return quiz_response

@router.post("/{company_id}/quizzes", response_model=QuizResponseModel,
             status_code=status.HTTP_201_CREATED)
async def create_quiz(
        company_id: int,
        quiz_req_body: QuizRequestModel,
        current_user: UserWithPermission = Depends(user_permission_admin_owner),
        quiz_instance: QuizRepository = Depends(get_quiz_instance),
        answer_instance: AnswerRepository = Depends(get_answer_instance),
        question_instance: QuestionRepository = Depends(get_question_instance)
):
    new_quiz = await quiz_instance.create(company_id=company_id, quiz_body=quiz_req_body,
                                          answers_repo=answer_instance, question_repo=question_instance)
    logging.info(f"Created new quiz with id: {new_quiz.id}")
    load_quiz = await quiz_instance.get_quiz_with_questions(quiz_id=new_quiz.id)
    quiz_response = QuizResponseModel.convert_quiz_db_to_response(quiz_db_model=load_quiz)
    return quiz_response


@router.put("/{company_id}/quizzes/{quiz_id}", response_model=QuizResponseModel)
async def update_quiz(
        company_id: int,
        quiz_id: int,
        quiz_update_body: QuizUpdateRequestModel,
        current_user: UserWithPermission = Depends(user_permission_admin_owner),
        quiz_instance: QuizRepository = Depends(get_quiz_instance)
):
    try:
        updated_quiz = await quiz_instance.update(entity_id=quiz_id, body=quiz_update_body)
        logging.info(f"Updated quiz with id: {quiz_id}")
        load_quiz = await quiz_instance.get_quiz_with_questions(quiz_id=updated_quiz.id)
        quiz_response = QuizResponseModel.convert_quiz_db_to_response(quiz_db_model=load_quiz)
        return quiz_response

    except NoResultFound:
        logging.error("Tried to get non-existent question")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found question")


@router.delete("/{company_id}/quizzes/{quiz_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_quiz(
        company_id: int,
        quiz_id: int,
        current_user: UserWithPermission = Depends(user_permission_admin_owner),
        quiz_instance: QuizRepository = Depends(get_quiz_instance)
):
    await quiz_instance.delete(entity_id=quiz_id)
    logging.info(f"Deleted quiz with id: {quiz_id}")
    return {f"Deleted quiz with id: {quiz_id}"}



