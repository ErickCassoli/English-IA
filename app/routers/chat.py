from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.repo import dao
from app.services import llm, parser, poml_runtime
from app.utils import ids, logger
from app.utils.config import get_settings

router = APIRouter(prefix="/api/chat", tags=["chat"])
settings = get_settings()
log = logger.get_logger(__name__)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    learner_level: str | None = Field(default=None, max_length=16)
    focus: list[str] = Field(default_factory=list)


class Highlight(BaseModel):
    from_index: int = Field(ge=0)
    to_index: int = Field(ge=0)
    note: str


class ChatContract(BaseModel):
    corrected: str
    explanation: str
    highlights: list[Highlight] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class ChatResponse(ChatContract):
    trace_id: str


@router.post("/correct", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def correct_message(payload: ChatRequest) -> ChatResponse:
    trace_id = ids.new_trace_id()
    try:
        prompt = poml_runtime.render_prompt(
            "chat-correct",
            {
                "message": payload.message,
                "learner_level": payload.learner_level or "B1",
                "focus_tags": ", ".join(payload.focus) if payload.focus else "general fluency",
            },
        )
        fallback = ChatContract(
            corrected=payload.message,
            explanation="No corrections were applied; returning fallback response.",
            highlights=[],
            tags=["fallback"],
        )
        raw = await llm.generate_prompt(
            prompt=prompt,
            trace_id=trace_id,
            settings=settings,
            fallback=fallback.model_dump(),
        )
        parsed = parser.parse_contract(raw, ChatContract)
        dao.record_chat_message(
            trace_id=trace_id,
            user_input=payload.message,
            corrected=parsed.corrected,
            metadata={"tags": parsed.tags, "focus": payload.focus},
        )
        return ChatResponse(trace_id=trace_id, **parsed.model_dump())
    except HTTPException as exc:
        dao.record_error(
            trace_id=trace_id,
            location="chat.correct",
            payload=payload.model_dump(),
            detail=exc.detail if isinstance(exc.detail, str) else "contract violation",
        )
        raise
    except Exception as exc:  # pragma: no cover - defensive logging
        dao.record_error(
            trace_id=trace_id,
            location="chat.correct",
            payload=payload.model_dump(),
            detail=str(exc),
        )
        log.error("chat correction failed", extra={"trace_id": trace_id, "error": str(exc)})
        raise HTTPException(status_code=500, detail="Chat correction failed") from exc
