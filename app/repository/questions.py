from db.models import Question as QuestionFromModel, Answer as AnswerFromModel
from schemas.quiz import QuestionRequestModel
from .answers import AnswerRepository
from .base import BaseEntitiesRepository, BaseEntityRepository



class QuestionsRepository(BaseEntitiesRepository):
    pass


class QuestionRepository(BaseEntityRepository):

    async def create(self, quiz_id: int, question_body: QuestionRequestModel, answers_repo: AnswerRepository) -> QuestionFromModel:
        new_answers = []
        for answer in question_body.answers:
            new_answers.append(await answers_repo.create(text=answer.text, is_correct=answer.is_correct))
        return await super().create(
            text=question_body.text,
            quiz_id=quiz_id,
            answers=new_answers
        )

    async def add_single_answer(self, question_id: int, answer: AnswerFromModel) -> QuestionFromModel:
        question = await self.get_entity_with_loading_field(self.entity, question_id, "answers")
        question.answers.append(answer)
        await self.async_session.commit()
        await self.async_session.refresh(question)
        return question

    async def validate_sum_correct_answ(self, question_id: int) -> bool:
        question = await self.get_entity_with_loading_field(self.entity, question_id, "answers")
        return sum(answer.is_correct for answer in question.answers) > 1

    async def validate_sum_answers(self, question_id: int) -> bool:
        question = await self.get_entity_with_loading_field(self.entity, question_id, "answers")
        return len(question.answers) > 2




