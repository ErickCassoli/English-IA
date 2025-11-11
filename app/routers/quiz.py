from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/quiz", tags=["quiz"])


class QuizGenerateRequest(BaseModel):
    topic: str
    difficulty: str = "B1"
    questions: int = 3


class QuizQuestion(BaseModel):
    id: str
    prompt: str
    options: list[str]


class QuizGenerateResponse(BaseModel):
    quiz_id: str
    questions: list[QuizQuestion]


@router.post("/generate", response_model=QuizGenerateResponse)
async def generate_quiz(_: QuizGenerateRequest) -> QuizGenerateResponse:
    return QuizGenerateResponse(quiz_id="stub", questions=[])


class QuizAnswerRequest(BaseModel):
    quiz_id: str
    answers: list[str]


class QuizAnswerResponse(BaseModel):
    quiz_id: str
    score: float


@router.post("/answer", response_model=QuizAnswerResponse)
async def answer_quiz(_: QuizAnswerRequest) -> QuizAnswerResponse:
    return QuizAnswerResponse(quiz_id="stub", score=0.0)
