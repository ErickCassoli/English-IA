from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.repo import dao, models
from app.repo.db import get_db

router = APIRouter(prefix="/api/placement", tags=["placement"])

class Question(BaseModel):
    id: int
    text: str
    options: List[str]

class Submission(BaseModel):
    answers: dict[int, str] # Question ID -> User Answer

# Professional Question Set (25 Items)
QUESTIONS = [
    # A1 (Basic)
    {"id": 1, "text": "I ___ from Brazil.", "options": ["am", "is", "are", "be"], "answer": "am", "level": "A1"},
    {"id": 2, "text": "They ___ play soccer on Sundays.", "options": ["doesn't", "don't", "no", "not"], "answer": "don't", "level": "A1"},
    {"id": 3, "text": "___ is your name?", "options": ["Who", "What", "When", "Why"], "answer": "What", "level": "A1"},
    {"id": 4, "text": "This is my brother. ___ name is Paul.", "options": ["Her", "His", "He", "Him"], "answer": "His", "level": "A1"},
    
    # A2 (Elementary)
    {"id": 5, "text": "I ___ breakfast at 7 AM yesterday.", "options": ["eat", "eats", "ate", "eaten"], "answer": "ate", "level": "A2"},
    {"id": 6, "text": "She is ___ than her sister.", "options": ["tall", "taller", "more tall", "tallest"], "answer": "taller", "level": "A2"},
    {"id": 7, "text": "Do you like ___ movies?", "options": ["watch", "watching", "to watching", "watched"], "answer": "watching", "level": "A2"},
    {"id": 8, "text": "Is there ___ milk in the fridge?", "options": ["some", "any", "a", "many"], "answer": "any", "level": "A2"},

    # B1 (Intermediate)
    {"id": 9, "text": "I have been working here ___ three years.", "options": ["since", "for", "during", "ago"], "answer": "for", "level": "B1"},
    {"id": 10, "text": "If it rains, we ___ inside.", "options": ["will stay", "would stay", "stayed", "staying"], "answer": "will stay", "level": "B1"},
    {"id": 11, "text": "He told me that he ___ busy.", "options": ["is", "was", "were", "has been"], "answer": "was", "level": "B1"},
    {"id": 12, "text": "This book is ___ interesting than the other one.", "options": ["more", "much", "very", "too"], "answer": "more", "level": "B1"},
    {"id": 13, "text": "I'm looking forward to ___ you.", "options": ["see", "seeing", "saw", "seen"], "answer": "seeing", "level": "B1"},

    # B2 (Upper Intermediate)
    {"id": 14, "text": "If I ___ you, I would accept the offer.", "options": ["was", "am", "were", "had been"], "answer": "were", "level": "B2"},
    # New B2:
    {"id": 15, "text": "I wish I ___ harder for the exam.", "options": ["studied", "had studied", "study", "would study"], "answer": "had studied", "level": "B2"},
    {"id": 16, "text": "By this time next year, I ___ my degree.", "options": ["will finish", "will have finished", "finish", "finished"], "answer": "will have finished", "level": "B2"},
    {"id": 17, "text": "Despite ___ tired, he went to the gym.", "options": ["be", "being", "he was", "of being"], "answer": "being", "level": "B2"},
    {"id": 18, "text": "We need to look ___ the specific details.", "options": ["up", "into", "after", "for"], "answer": "into", "level": "B2"},

    # C1 (Advanced)
    {"id": 19, "text": "Rarely ___ such a beautiful sunset.", "options": ["I have seen", "have I seen", "I saw", "seen I have"], "answer": "have I seen", "level": "C1"},
    {"id": 20, "text": "It’s high time we ___ home.", "options": ["go", "went", "have gone", "had gone"], "answer": "went", "level": "C1"},
    {"id": 21, "text": "Select the synonym for 'Ubiquitous':", "options": ["Scarce", "Omnipresent", "Obsolete", "Hideous"], "answer": "Omnipresent", "level": "C1"},
    {"id": 22, "text": "He was accused ___ stealing the money.", "options": ["of", "for", "with", "about"], "answer": "of", "level": "C1"},

    # C2 (Proficiency - Vocabulary/Nuance)
    {"id": 23, "text": "The project was fraught ___ difficulties.", "options": ["with", "by", "in", "of"], "answer": "with", "level": "C2"},
    {"id": 24, "text": "I took exception ___ his remarks.", "options": ["of", "with", "to", "against"], "answer": "to", "level": "C2"},
    {"id": 25, "text": "Which word implies 'brief and to the point'?", "options": ["Loquacious", "Succinct", "Prolix", "Verbos"], "answer": "Succinct", "level": "C2"},
]

@router.get("/questions", response_model=List[Question])
def get_questions():
    return [
        Question(id=q["id"], text=q["text"], options=q["options"]) 
        for q in QUESTIONS
    ]

@router.post("/submit")
def submit_test(payload: Submission, db: Session = Depends(get_db)):
    user = dao.ensure_default_user(db)
    
    correct_count = 0
    total = len(QUESTIONS)
    
    # Calculate score
    for q in QUESTIONS:
        user_ans = payload.answers.get(q["id"])
        # Robust comparison
        if user_ans and user_ans.strip().lower() == q["answer"].strip().lower():
            correct_count += 1
            
    pct = (correct_count / total) * 100
    
    # Weighted Mapping (To get C2 you need near perfect score on hard set)
    if pct >= 92: cefr = models.CEFRLevel.C2 # 23-25 correct
    elif pct >= 80: cefr = models.CEFRLevel.C1 # 20-22 correct
    elif pct >= 64: cefr = models.CEFRLevel.B2 # 16-19
    elif pct >= 48: cefr = models.CEFRLevel.B1 # 12-15
    elif pct >= 24: cefr = models.CEFRLevel.A2 # 6-11
    else: cefr = models.CEFRLevel.A1 # 0-5
    
    # Check if placement session topic exists
    topic = dao.get_practice_topic_by_code(db, "placement_static")
    if not topic:
        topic = models.PracticeTopic(code="placement_static", label="Placement Quiz", description="Static assessment.")
        db.add(topic)
        db.commit()
        db.refresh(topic)
        
    session = dao.create_session(db, user, topic, "Static Test System")
    session.status = models.SessionStatus.FINISHED
    session.active_seconds = 600 # estimate 10 mins
    
    dao.record_metric_snapshot(
        db,
        user,
        session,
        words=0, 
        errors=total - correct_count,
        accuracy_pct=pct,
        cefr=cefr
    )
    
    db.commit()
    
    return {
        "score_pct": pct,
        "cefr_level": cefr.value,
        "correct": correct_count,
        "total": total
    }
