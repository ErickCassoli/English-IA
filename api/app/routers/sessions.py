from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.repo import dao, models
from app.repo.db import get_db
from app.schemas.session import SessionCreateRequest, SessionFinishResponse, SessionResponse
from app.services.evaluation import quizgen
from app.services.llm import registry
from app.utils.config import get_settings

router = APIRouter(prefix="/api/sessions", tags=["sessions"])
runtime_config = get_settings()
# Trigger reload for prompt update


@lru_cache(maxsize=1)
def _base_system_prompt() -> str:
    prompt_path = Path(__file__).resolve().parents[2] / "prompts" / "tutor_roleplay.poml"
    if prompt_path.exists():
        return prompt_path.read_text(encoding="utf-8").strip()
    return "You are a patient English tutor helping the learner practice real-life conversations."


def _build_prompt(topic: models.PracticeTopic) -> str:
    if topic.code == "placement_test":
        prompt_path = Path(__file__).resolve().parents[2] / "prompts" / "placement_test.poml"
        if prompt_path.exists():
            return prompt_path.read_text(encoding="utf-8").strip()
    
    base = _base_system_prompt()
    return (
        f"{base}\n\n"
        f"Conversation theme: {topic.label}.\n"
        f"Context: {topic.description}\n"
        "Keep the dialogue in English, ask follow-up questions. "
        "Do NOT correct the user's grammar in your text response. "
        "Just conversation."
    )


def _to_response(session: models.Session, topic: models.PracticeTopic) -> SessionResponse:
    return SessionResponse(
        session_id=session.id,
        topic_code=topic.code,
        topic_label=topic.label,
        topic_description=topic.description,
        system_prompt=session.system_prompt,
        status=session.status.value,
        started_at=session.started_at,
        ended_at=session.ended_at,
        active_minutes=round((session.active_seconds or 0) / 60, 2),
        last_interaction_at=session.last_interaction_at,
    )


@router.post("", response_model=SessionResponse)
def create_session(payload: SessionCreateRequest, db: Session = Depends(get_db)):
    user = dao.ensure_default_user(db)
    topic = None
    if payload.topic_code:
        requested_code = payload.topic_code.strip().lower()
        topic = dao.get_practice_topic_by_code(db, requested_code)
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")
    elif payload.custom_topic:
        import uuid
        # Create ad-hoc topic with unique code to avoid collision and support recents
        uid = uuid.uuid4().hex[:8]
        topic = models.PracticeTopic(
            code=f"custom_{uid}",
            label=payload.custom_topic.strip(),
            description=f"User defined topic: {payload.custom_topic}"
        )
        db.add(topic) # Ensure it's added
        db.commit()
        db.refresh(topic)
    
    if not topic:
        # Fallback to random is likely NOT wanted if we require selection
        # But for backward compatibility with 'Practice' page shuffle, we keep it? 
        # The user said "must choose topic". But the Practice page might still send random?
        # Let's keep random fallback ONLY if no strict param was passed, but Practice page sends codes.
        # If the frontend is blocked, it won't send empty.
        topic = dao.get_random_practice_topic(db)
    
    if not topic:
        raise HTTPException(status_code=500, detail="No practice topics configured")
    
    # Enforce Placement Test
    if topic.code != "placement_test":
        # Check if user has ANY completion metrics
        has_metrics = db.scalar(
            dao.select(dao.func.count(models.MetricSnapshot.id))
            .where(models.MetricSnapshot.user_id == user.id)
        ) or 0
        
        if has_metrics == 0:
             raise HTTPException(status_code=403, detail="Placement Test Required")

    system_prompt = _build_prompt(topic)
    system_prompt = _build_prompt(topic)
    session = dao.create_session(db, user, topic, system_prompt)
    db.commit()
    db.refresh(session)
    return _to_response(session, topic)


@router.post("/{session_id}/finish", response_model=SessionFinishResponse)
def finish_session(session_id: str, db: Session = Depends(get_db)):
    session = dao.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # If already pending quiz or finished, just return status
    if session.status in (models.SessionStatus.PENDING_QUIZ, models.SessionStatus.FINISHED):
        quizzes = dao.list_quizzes_by_session(db, session_id)
        return SessionFinishResponse(
            quizzes_created=len(quizzes),
            flashcards_created=0,
            report_ready=session.status == models.SessionStatus.FINISHED,
            quizzes=[
                {"id": q.id, "type": q.type.value, "prompt": q.prompt, "choices_json": q.choices_json, "answer": q.answer}
                for q in quizzes
            ]
        )

    messages = dao.list_session_messages(db, session_id)
    errors = dao.list_session_errors(db, session_id)

    # CHECK FOR PLACEMENT TEST
    if session.topic_code == "placement_test":
        from app.services.evaluation import placement
        from app.repo.models import CEFRLevel
        
        settings_row = dao.get_settings(db)
        llm_client = registry.get_llm(settings_row, config=runtime_config)
        
        result = placement.evaluate_session(llm_client, messages)
        
        # Save Snapshot
        est_level = CEFRLevel(result.get("cefr_level", "A1"))
        # Using the raw score as 'accuracy' proxy for simplicity or visualization
        score = float(result.get("score_0_100", 0))
        
        dao.record_metric_snapshot(
            db, 
            session.user, 
            session, 
            words=len(messages), # rough count needed? or irrelevant
            errors=0, # Errors not counted in placement
            accuracy_pct=score,
            cefr=est_level
        )
        
        dao.mark_session_finished(db, session)
        db.commit()
        
        return SessionFinishResponse(
            quizzes_created=0,
            flashcards_created=0,
            report_ready=True,
            quizzes=[]
        )

    try:
        # Initialize LLM Client
        settings_row = dao.get_settings(db)
        llm_client = registry.get_llm(settings_row, config=runtime_config)

        topic_label = session.topic.label if session.topic else session.topic_code
        
        # Try LLM-based generation first
        print(f"[INFO] Attempting LLM quiz generation for session {session_id}")
        quiz_items, flashcard_items = quizgen.generate_quiz_with_llm(llm_client, topic_label, errors, messages)
        
        # Fallback to deterministic if LLM returned empty
        if not quiz_items or len(quiz_items) == 0:
            print(f"[WARN] LLM returned no quizzes, falling back to deterministic generation")
            quiz_items = quizgen.generate_quiz(topic_label, errors, messages)
            flashcard_items = []
        
        # Save Quizzes
        created_quizzes = dao.create_quizzes(db, session, quiz_items)
        
        # Save Flashcards
        flashcards_created = 0
        for f in flashcard_items:
            dao.create_manual_flashcard(db, f.front, f.back)
            flashcards_created += 1

        session.status = models.SessionStatus.PENDING_QUIZ
        db.add(session)
        db.commit()

        return SessionFinishResponse(
            quizzes_created=len(created_quizzes),
            flashcards_created=flashcards_created,
            report_ready=False,
            quizzes=[
                {"id": q.id, "type": q.type.value, "prompt": q.prompt, "choices_json": q.choices_json, "answer": q.answer}
                for q in created_quizzes
            ]
        )
    except Exception as e:
        import traceback
        print(f"[ERROR] Quiz generation failed: {e}")
        traceback.print_exc()
        # Complete fallback to deterministic
        topic_label = session.topic.label if session.topic else session.topic_code
        quiz_items = quizgen.generate_quiz(topic_label, errors, messages)
        created_quizzes = dao.create_quizzes(db, session, quiz_items)
        
        session.status = models.SessionStatus.PENDING_QUIZ
        db.add(session)
        db.commit()
        
        return SessionFinishResponse(
            quizzes_created=len(created_quizzes),
            flashcards_created=0,
            report_ready=False,
            quizzes=[
                {"id": q.id, "type": q.type.value, "prompt": q.prompt, "choices_json": q.choices_json, "answer": q.answer}
                for q in created_quizzes
            ]
        )


@router.post("/{session_id}/submit_quiz", response_model=SessionFinishResponse)
def submit_quiz(session_id: str, answers: dict[str, str], db: Session = Depends(get_db)):
    session = dao.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.status == models.SessionStatus.FINISHED:
        return SessionFinishResponse(quizzes_created=0, flashcards_created=0, report_ready=True)

    # Process answers
    current_quizzes = dao.list_quizzes_by_session(db, session_id)
    quiz_map = {q.id: q for q in current_quizzes}
    
    for q_id, user_answer in answers.items():
        if q_id in quiz_map:
            quiz = quiz_map[q_id]
            is_correct = (user_answer.strip().lower() == quiz.answer.strip().lower())
            dao.record_quiz_attempt(db, quiz, session.user, is_correct, latency_ms=0)

    # Generate Flashcards & Finalize
    errors = dao.list_session_errors(db, session_id)
    flashcards_created = 0
    for error in errors:
        _, created = dao.ensure_flashcard_from_error(db, error, error.user_text, error.corrected_text)
        if created:
            flashcards_created += 1

    dao.mark_session_finished(db, session)
    db.commit()

    return SessionFinishResponse(
        quizzes_created=len(current_quizzes),
        flashcards_created=flashcards_created,
        report_ready=True
    )

@router.get("/recent-topics")
def get_recent_topics(db: Session = Depends(get_db)):
    user = dao.ensure_default_user(db)
    topics = dao.get_recent_topics(db, user, limit=3)
    
    # Map to simple dict
    result = [
        {"code": t.code, "label": t.label, "description": t.description}
        for t in topics
    ]
    
    # If fewer than 3, fill with defaults
    if len(result) < 3:
        defaults = [
            {"code": "daily_life", "label": "Daily Life", "description": "Chat about routine activities."},
            {"code": "travel", "label": "Travel", "description": "Discuss trips and cultures."},
            {"code": "hobbies", "label": "Hobbies", "description": "Talk about interests and fun."}
        ]
        # Append defaults if not already present
        existing_codes = {r["code"] for r in result}
        for d in defaults:
            if d["code"] not in existing_codes:
                result.append(d)
                if len(result) >= 3:
                    break
                    
    return result[:3]
