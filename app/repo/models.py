from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.repo.db import Base
from app.utils import ids


def _uuid() -> str:
    return ids.new_id()


class LLMProvider(str, Enum):
    SIMPLE = "simple_mock"
    OLLAMA = "ollama"
    OPENAI = "openai"


class SessionStatus(str, Enum):
    ACTIVE = "active"
    FINISHED = "finished"


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


class ErrorCategory(str, Enum):
    GRAMMAR = "grammar"
    VOCAB = "vocab"
    FLUENCY = "fluency"


class QuizType(str, Enum):
    MCQ = "mcq"
    CLOZE = "cloze"


class CEFRLevel(str, Enum):
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"


def _now() -> datetime:
    return datetime.now(tz=UTC)


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    nickname: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, nullable=False)

    sessions: Mapped[List["Session"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class PracticeTopic(Base):
    __tablename__ = "practice_topics"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    label: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    sessions: Mapped[List["Session"]] = relationship(back_populates="topic")


class Settings(Base):
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    llm_provider: Mapped[LLMProvider] = mapped_column(
        SQLEnum(LLMProvider), default=LLMProvider.SIMPLE, nullable=False
    )
    llm_model: Mapped[str] = mapped_column(String(64), default="mock-1", nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, nullable=False)


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    topic_code: Mapped[str] = mapped_column(ForeignKey("practice_topics.code"), nullable=False)
    status: Mapped[SessionStatus] = mapped_column(
        SQLEnum(SessionStatus), default=SessionStatus.ACTIVE, nullable=False
    )
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, nullable=False)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    system_prompt: Mapped[str] = mapped_column(Text, nullable=False)

    user: Mapped["User"] = relationship(back_populates="sessions")
    topic: Mapped["PracticeTopic"] = relationship(back_populates="sessions")
    messages: Mapped[List["Message"]] = relationship(
        back_populates="session", cascade="all, delete-orphan", order_by="Message.ts"
    )
    quizzes: Mapped[List["Quiz"]] = relationship(back_populates="session", cascade="all, delete-orphan")
    metric_snapshots: Mapped[List["MetricSnapshot"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id"), nullable=False)
    role: Mapped[MessageRole] = mapped_column(SQLEnum(MessageRole), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, nullable=False)

    session: Mapped["Session"] = relationship(back_populates="messages")
    error_spans: Mapped[List["ErrorSpan"]] = relationship(
        back_populates="message", cascade="all, delete-orphan"
    )


class ErrorSpan(Base):
    __tablename__ = "error_spans"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    message_id: Mapped[str] = mapped_column(ForeignKey("messages.id"), nullable=False)
    start: Mapped[int] = mapped_column(Integer, nullable=False)
    end: Mapped[int] = mapped_column(Integer, nullable=False)
    category: Mapped[ErrorCategory] = mapped_column(SQLEnum(ErrorCategory), nullable=False)
    user_text: Mapped[str] = mapped_column(Text, nullable=False)
    corrected_text: Mapped[str] = mapped_column(Text, nullable=False)
    note: Mapped[str] = mapped_column(Text, nullable=False)

    message: Mapped["Message"] = relationship(back_populates="error_spans")
    flashcards: Mapped[List["Flashcard"]] = relationship(back_populates="source_error")


class Quiz(Base):
    __tablename__ = "quizzes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id"), nullable=False)
    type: Mapped[QuizType] = mapped_column(SQLEnum(QuizType), nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    choices_json: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, nullable=False)

    session: Mapped["Session"] = relationship(back_populates="quizzes")
    attempts: Mapped[List["QuizAttempt"]] = relationship(
        back_populates="quiz", cascade="all, delete-orphan"
    )


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    quiz_id: Mapped[str] = mapped_column(ForeignKey("quizzes.id"), nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    is_correct: Mapped[bool] = mapped_column(default=False, nullable=False)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, nullable=False)

    quiz: Mapped["Quiz"] = relationship(back_populates="attempts")
    user: Mapped["User"] = relationship()


class Flashcard(Base):
    __tablename__ = "flashcards"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    front: Mapped[str] = mapped_column(Text, nullable=False)
    back: Mapped[str] = mapped_column(Text, nullable=False)
    source_error_id: Mapped[Optional[str]] = mapped_column(ForeignKey("error_spans.id"))
    ease: Mapped[float] = mapped_column(Numeric(3, 2), default=2.5, nullable=False)
    interval: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reps: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, nullable=False)

    source_error: Mapped[Optional["ErrorSpan"]] = relationship(back_populates="flashcards")


class MetricSnapshot(Base):
    __tablename__ = "metric_snapshots"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id"), nullable=False)
    words: Mapped[int] = mapped_column(Integer, nullable=False)
    errors: Mapped[int] = mapped_column(Integer, nullable=False)
    accuracy_pct: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    cefr_estimate: Mapped[CEFRLevel] = mapped_column(SQLEnum(CEFRLevel), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, nullable=False)

    session: Mapped["Session"] = relationship(back_populates="metric_snapshots")
    user: Mapped["User"] = relationship()
