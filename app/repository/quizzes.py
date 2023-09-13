from typing import List

from sqlalchemy import select

from db.models import Quiz as QuizFromModels, Question as QuestionFromModel
from schemas.quiz import QuizRequestModel
from .answers import AnswerRepository
from .base import BaseEntitiesRepository, BaseEntityRepository
from .questions import QuestionRepository


class QuizRepository(BaseEntityRepository):

    async def create(self, quiz_body: QuizRequestModel, company_id: int, answers_repo: AnswerRepository,
                     question_repo: QuestionRepository) -> QuizFromModels:
        new_questions = []
        for question in quiz_body.questions:
            new_answers = []
            for answer in question.answers:
                new_answers.append(await answers_repo.create(text=answer.text, is_correct=answer.is_correct))
            new_questions.append(await question_repo.create(text=question.text, answers=new_answers))
        return await super().create(
            name=quiz_body.name,
            description=quiz_body.description,
            company_id=company_id,
            questions=new_questions
        )

    async def get_quiz_with_questions(self, quiz_id: int):
        quiz_with_load_questions = await self.get_entity_with_loading_field(QuizFromModels, quiz_id, 'questions')
        quiz_with_load_questions.questions = [
            await self.get_entity_with_loading_field(QuestionFromModel, question.id, 'answers') for question in
            quiz_with_load_questions.questions]
        return quiz_with_load_questions

    async def add_single_question(self, quiz_id: int, question: QuestionFromModel) -> QuizFromModels:
        quiz = await self.get_quiz_with_questions(quiz_id=quiz_id)
        quiz.questions.append(question)
        await self.async_session.commit()
        await self.async_session.refresh(quiz)
        return quiz

    async def validate(self, quiz_id: int) -> bool:
        quiz = await self.get_quiz_with_questions(quiz_id=quiz_id)
        return len(quiz.questions) > 2


class QuizzesRepository(BaseEntitiesRepository, QuizRepository):
    async def paginate_query(self, page: int, page_size: int, company_id: int) -> List[QuizFromModels]:
        stmt = select(self.entity).where(self.entity.company_id == company_id)
        stmt_with_pagination = self.apply_pagination(stmt, page, page_size)
        res = await self.async_session.execute(stmt_with_pagination)
        entities = res.scalars().all()
        return entities
