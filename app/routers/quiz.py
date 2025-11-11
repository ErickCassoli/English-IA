from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.repo import dao
from app.services import llm, parser, poml_runtime
from app.utils import ids

router = APIRouter(prefix="/api/quiz", tags=["quiz"])


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
    difficulty: str = Field(default="B1", min_length=2, max_length=3)
    questions: int = Field(default=3, ge=1, le=5)


class QuizQuestionPublic(BaseModel):
    id: str
    prompt: str
    options: list[str]


class QuizGenerateResponse(BaseModel):
    trace_id: str
    quiz_id: str
    questions: list[QuizQuestionPublic]


@router.post("/generate", response_model=QuizGenerateResponse)
async def generate_quiz(payload: QuizGenerateRequest) -> QuizGenerateResponse:
    trace_id = ids.new_trace_id()
    prompt = poml_runtime.render_prompt(
        "quiz-gen",
        {
            "topic": payload.topic,
            "difficulty": payload.difficulty,
            "questions": payload.questions,
        },
    )
    fallback = QuizContract(
        questions=[
            QuizQuestionContract(
                id=ids.new_id(),
                prompt=f"Which sentence talks about {payload.topic}?",
                options=["I go", "I goes", "I going"],
                answer="I go",
                rationale="First person singular",
            )
        ]
    )
    raw = await llm.generate(prompt=prompt, trace_id=trace_id, fallback=fallback.model_dump())
    parsed = parser.parse_contract(raw, QuizContract)
    quiz_id = dao.create_quiz(
        trace_id=trace_id,
        topic=payload.topic,
        difficulty=payload.difficulty,
        questions=[question.model_dump() for question in parsed.questions],
    )
    public_questions = [
        QuizQuestionPublic(id=question.id, prompt=question.prompt, options=question.options)
        for question in parsed.questions
    ]
    return QuizGenerateResponse(trace_id=trace_id, quiz_id=quiz_id, questions=public_questions)


class QuizAnswer(BaseModel):
    question_id: str
    answer: str


class QuizAnswerRequest(BaseModel):
    quiz_id: str
    answers: list[QuizAnswer]


class QuizAnswerDetail(BaseModel):
    question_id: str
    answer: str | None
    correct_answer: str
    is_correct: bool
    rationale: str


class QuizAnswerResponse(BaseModel):
    trace_id: str
    quiz_id: str
    score: float
    details: list[QuizAnswerDetail]


@router.post("/answer", response_model=QuizAnswerResponse)
def answer_quiz(payload: QuizAnswerRequest) -> QuizAnswerResponse:
    trace_id = ids.new_trace_id()
    quiz = dao.get_quiz(payload.quiz_id)
    if not quiz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")
    answer_map = {item.question_id: item.answer for item in payload.answers}
    details: list[QuizAnswerDetail] = []
    correct = 0
    for question in quiz["questions"]:
        selected = answer_map.get(question["id"])
        is_correct = selected == question["answer"]
        if is_correct:
            correct += 1
        details.append(
            QuizAnswerDetail(
                question_id=question["id"],
                answer=selected,
                correct_answer=question["answer"],
                is_correct=is_correct,
                rationale=question["rationale"],
            )
        )
    total = len(quiz["questions"])
    score = round(correct / total, 2) if total else 0.0
    dao.bump_daily_stats(minutes=5, accuracy=score, error_tag="quiz")
    return QuizAnswerResponse(
        trace_id=trace_id,
        quiz_id=payload.quiz_id,
        score=score,
        details=details,
    )
