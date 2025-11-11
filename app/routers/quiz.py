from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.repo import dao
from app.services import llm, parser, poml_runtime
from app.utils import ids
from app.utils.config import get_settings

router = APIRouter(prefix="/api/quiz", tags=["quiz"])
settings = get_settings()


class QuizQuestionContract(BaseModel):
    id: str
    prompt: str
    options: list[str] = Field(min_length=2)
    answer: str
    rationale: str


class QuizContract(BaseModel):
    questions: list[QuizQuestionContract]


class QuizGenerateRequest(BaseModel):
    topic: str = Field(..., min_length=3)
    num_questions: int = Field(default=3, ge=1, le=5)
    learner_level: str = Field(default="B1", min_length=2, max_length=3)


class QuizQuestion(BaseModel):
    id: str
    prompt: str
    options: list[str]


class QuizGenerateResponse(BaseModel):
    trace_id: str
    quiz_id: str
    questions: list[QuizQuestion]


class QuizAnswer(BaseModel):
    question_id: str
    choice: str


class QuizAnswerRequest(BaseModel):
    quiz_id: str
    answers: list[QuizAnswer]


class QuizAnswerBreakdown(BaseModel):
    question_id: str
    choice: str | None
    correct_answer: str
    is_correct: bool
    rationale: str


class QuizAnswerResponse(BaseModel):
    trace_id: str
    quiz_id: str
    score: float
    correct: int
    total: int
    breakdown: list[QuizAnswerBreakdown]


@router.post("/generate", response_model=QuizGenerateResponse)
async def generate_quiz(payload: QuizGenerateRequest) -> QuizGenerateResponse:
    trace_id = ids.new_trace_id()
    prompt = poml_runtime.render_prompt(
        "quiz-gen",
        {
            "topic": payload.topic,
            "num_questions": payload.num_questions,
            "learner_level": payload.learner_level,
        },
    )
    fallback = QuizContract(
        questions=[
            QuizQuestionContract(
                id=ids.new_id(),
                prompt=f"Which sentence fits the topic '{payload.topic}'?",
                options=["I go", "I goes", "I going"],
                answer="I go",
                rationale="First person singular uses 'go'.",
            )
        ]
    )
    raw = await llm.generate_prompt(
        prompt=prompt,
        trace_id=trace_id,
        settings=settings,
        fallback=fallback.model_dump(),
    )
    parsed = parser.parse_contract(raw, QuizContract)
    quiz_id = dao.create_quiz(
        trace_id=trace_id,
        topic=payload.topic,
        questions=[q.model_dump() for q in parsed.questions],
    )
    public_questions = [
        QuizQuestion(id=q.id, prompt=q.prompt, options=q.options) for q in parsed.questions
    ]
    return QuizGenerateResponse(trace_id=trace_id, quiz_id=quiz_id, questions=public_questions)


@router.post("/answer", response_model=QuizAnswerResponse)
def answer_quiz(payload: QuizAnswerRequest) -> QuizAnswerResponse:
    trace_id = ids.new_trace_id()
    quiz = dao.get_quiz(payload.quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    answer_map = {answer.question_id: answer.choice for answer in payload.answers}
    breakdown: list[QuizAnswerBreakdown] = []
    correct = 0
    for question in quiz["questions"]:
        user_choice = answer_map.get(question["id"])
        is_correct = user_choice == question["answer"]
        if is_correct:
            correct += 1
        breakdown.append(
            QuizAnswerBreakdown(
                question_id=question["id"],
                choice=user_choice,
                correct_answer=question["answer"],
                is_correct=is_correct,
                rationale=question["rationale"],
            )
        )
    total = len(quiz["questions"])
    score = round(correct / total, 2) if total else 0.0
    return QuizAnswerResponse(
        trace_id=trace_id,
        quiz_id=payload.quiz_id,
        score=score,
        correct=correct,
        total=total,
        breakdown=breakdown,
    )
