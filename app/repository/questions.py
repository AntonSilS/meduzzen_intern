from db.models import Question as QuestionFromModel, Answer as AnswerFromModel
from .base import BaseEntitiesRepository, BaseEntityRepository



class QuestionsRepository(BaseEntitiesRepository):
    pass


class QuestionRepository(BaseEntityRepository):
    async def add_single_answer(self, question_id: int, answer: AnswerFromModel) -> QuestionFromModel:
        question = await self.get_entity_with_loading_field(QuestionFromModel, question_id, "answers")
        question.answers.append(answer)
        await self.async_session.commit()
        await self.async_session.refresh(question)
        return question



