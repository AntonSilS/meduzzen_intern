from db.models import Quiz as QuizFromModels, Question as QuestionFormModels
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
            await self.get_entity_with_loading_field(QuestionFormModels, question.id, 'answers') for question in
            quiz_with_load_questions.questions]
        return quiz_with_load_questions


class QuizzesRepository(BaseEntitiesRepository, QuizRepository):
    pass
