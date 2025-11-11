from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.repo import dao
from app.services import llm, parser, poml_runtime
from app.utils import ids, logger

router = APIRouter(prefix="/api/chat", tags=["chat"])
log = logger.get_logger(__name__)


class Highlight(BaseModel):
    from_index: int = Field(ge=0)
    to_index: int = Field(ge=0)
    note: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    learner_level: str | None = None
    focus: list[str] = Field(default_factory=list)


class ChatContract(BaseModel):
    corrected: str
    explanation: str
    highlights: list[Highlight]
    tags: list[str]


class ChatResponse(ChatContract):
    trace_id: str


@router.post("/correct", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def correct_message(payload: ChatRequest) -> ChatResponse:
    trace_id = ids.new_trace_id()
    focus = ", ".join(payload.focus) if payload.focus else "general fluency"
    try:
        prompt = poml_runtime.render_prompt(
            "chat-correct",
            {
                "message": payload.message,
                "learner_level": payload.learner_level or "B1",
                "focus": focus,
                "trace_id": trace_id,
            },
        )
        fallback = {
            "corrected": payload.message,
            "explanation": "Fallback response while LLM is offline.",
            "highlights": [],
            "tags": ["fallback"],
        }
        raw = await llm.generate(prompt=prompt, trace_id=trace_id, fallback=fallback)
        parsed = parser.parse_contract(raw, ChatContract)
        dao.record_message(
            trace_id=trace_id,
            user_input=payload.message,
            corrected=parsed.corrected,
            metadata={"tags": parsed.tags, "focus": payload.focus},
        )
        dao.bump_daily_stats(
            minutes=3,
            accuracy=0.8,
            error_tag=(parsed.tags[0] if parsed.tags else None),
        )
        return ChatResponse(trace_id=trace_id, **parsed.model_dump())
    except HTTPException:
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
