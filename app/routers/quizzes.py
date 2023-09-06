import logging
from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.exc import NoResultFound

from core.log_config import LoggingConfig
from repository.answers import AnswerRepository

from repository.questions import QuestionRepository
from repository.quizzes import QuizRepository, QuizzesRepository
from schemas.auth import UserWithPermission

from repository.service_repo_instance import get_quiz_instance, get_answer_instance, get_question_instance, get_quizzes_instance
from schemas.quiz import QuizRequestModel, QuizUpdateRequestModel, QuestionUpdateRequestModel, AnswerUpdateRequestModel, \
    QuizResponseModel, AnswerResponseModel, QuestionResponseModel
from schemas.users import PaginationParams
from utils.service_permission import user_permission_admin_owner
from db.models import Question as QuestionFormModels, Quiz as QuizFromModels

router = APIRouter(prefix="/companies", tags=["quizzes"])

LoggingConfig.configure_logging()


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


@router.put("/{company_id}/quizzes/{quiz_id}/questions/{question_id}/answers/{answer_id}",
            response_model=AnswerResponseModel)
async def update_answer(
        company_id: int,
        quiz_id: int,
        question_id: int,
        answer_id: int,
        answer_update_body: AnswerUpdateRequestModel,
        current_user: UserWithPermission = Depends(user_permission_admin_owner),
        answer_instance: AnswerRepository = Depends(get_answer_instance)
):
    try:
        updated_answer = await answer_instance.update(entity_id=answer_id, body=answer_update_body)
        logging.info(f"Updated answer with id: {answer_id} in question with id: {question_id}")
        return AnswerResponseModel.convert_answer_db_to_response(updated_answer)

    except NoResultFound:
        logging.error("Tried to get non-existent answer")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found answer")


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


@router.delete("/{company_id}/quizzes/{quiz_id}/questions/{question_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_question(
        company_id: int,
        quiz_id: int,
        question_id: int,
        current_user: UserWithPermission = Depends(user_permission_admin_owner),
        question_instance: QuestionRepository = Depends(get_question_instance)
):
    try:
        await question_instance.delete(entity_id=question_id)
        logging.info(f"Deleted question with id: {question_id}")
        return {f"Deleted question with id: {question_id}"}
    except NoResultFound:
        logging.error("Tried to get non-existent question")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found question")


@router.delete("/{company_id}/quizzes/{quiz_id}/questions/{question_id}/answers/{answer_id}",
               status_code=status.HTTP_202_ACCEPTED)
async def delete_answer(
        company_id: int,
        quiz_id: int,
        question_id: int,
        answer_id: int,
        current_user: UserWithPermission = Depends(user_permission_admin_owner),
        answer_instance: AnswerRepository = Depends(get_answer_instance)
):
    try:
        await answer_instance.delete(entity_id=answer_id)
        logging.info(f"Deleted answer with id: {answer_id}")
        return {f"Deleted answer with id: {answer_id}"}
    except NoResultFound:
        logging.error("Tried to get non-existent answer")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found answer")


@router.get("/{company_id}/quizzes", response_model=List[QuizResponseModel])
async def get_quizzes(
        company_id: int,
        current_user: UserWithPermission = Depends(user_permission_admin_owner),
        pagination: PaginationParams = Depends(),
        quizzes_instance: QuizzesRepository = Depends(get_quizzes_instance)
):
    all_quizzes = await quizzes_instance.paginate_query(entity=QuizFromModels, page=pagination.page,
                                                        page_size=pagination.page_size)
    load_all_quizzes = [await quizzes_instance.get_quiz_with_questions(quiz_id=quiz.id) for quiz in all_quizzes]
    all_quizzes_response = [QuizResponseModel.convert_quiz_db_to_response(quiz_db_model=load_quiz) for load_quiz in load_all_quizzes]
    logging.info(f"Got all quizzes by user id: {current_user.id} in company with id: {company_id}")
    return all_quizzes_response
