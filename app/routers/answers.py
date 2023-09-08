import logging
from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.exc import NoResultFound

from core.log_config import LoggingConfig
from repository.answers import AnswerRepository

from repository.questions import QuestionRepository
from schemas.auth import UserWithPermission

from repository.service_repo_instance import get_answer_instance, get_question_instance
from schemas.quiz import AnswerUpdateRequestModel, AnswerResponseModel, QuestionResponseModel, AnswerRequestModel
from utils.service_permission import user_permission_admin_owner

router = APIRouter(prefix="/companies", tags=["answers"])

LoggingConfig.configure_logging()


@router.post("/{company_id}/quizzes/{quiz_id}/questions/{question_id}/answers", response_model=AnswerResponseModel,
             status_code=status.HTTP_201_CREATED)
async def create_answer(
        company_id: int,
        quiz_id: int,
        question_id: int,
        answer_body: AnswerRequestModel,
        current_user: UserWithPermission = Depends(user_permission_admin_owner),
        answer_instance: AnswerRepository = Depends(get_answer_instance),
        question_instance: QuestionRepository = Depends(get_question_instance)
):
    new_answer = await answer_instance.create(text=answer_body.text, is_correct=answer_body.is_correct)
    updated_question = await question_instance.add_single_answer(question_id=question_id, answer=new_answer)
    logging.info(f"Created new answer with id: {new_answer.id} in question with id: {question_id}")
    return new_answer


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
