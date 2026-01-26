from __future__ import annotations

from sqlalchemy.orm import Session

from app.repo import dao, models

DEFAULT_TOPICS = [
    ("travel", "Travel", "Discuss trips, cultures, packing tips, and directions."),
    ("technology", "Technology", "Talk about gadgets, software, AI, and future trends."),
    ("food", "Food", "Describe meals, flavors, restaurants, and cooking habits."),
    ("work", "Work", "Practice workplace scenarios, meetings, and career goals."),
    ("entertainment", "Entertainment", "Chat about music, movies, books, and hobbies."),
    ("gaming", "Gaming", "Discuss video games, esports, mechanics, and lore."),
    ("daily_life", "Daily Life", "Cover routines, family, errands, and local life."),
    ("health", "Health & Fitness", "Talk about exercise, diet, mental health, and medical visits."),
    ("shopping", "Shopping", "Discuss fashion, sales, bargaining, and online stores."),
    ("nature", "Nature & Environment", "Describe landscapes, wildlife, weather, and sustainability."),
    ("history", "History & Culture", "Explore past events, traditions, and historical figures."),
    ("job_interview", "Job Interview", "Practice answers for common interview questions."),
    ("social_media", "Social Media", "Debate trends, influencers, and digital impact."),
    ("relationships", "Relationships", "Discuss friendships, dating, family dynamics, and advice."),
    ("education", "Education", "Talk about schools, degrees, learning methods, and teachers."),
]


def seed_defaults(db: Session) -> None:
    """Ensure a default user, settings row, and practice topics exist."""
    dao.ensure_default_user(db)
    dao.get_settings(db)

    existing_codes = {topic.code for topic in dao.list_practice_topics(db)}
    for code, label, description in DEFAULT_TOPICS:
        if code in existing_codes:
            continue
        db.add(models.PracticeTopic(code=code, label=label, description=description))
    db.flush()


if __name__ == "__main__":  # pragma: no cover - manual utility
    from app.repo.db import session_scope

    with session_scope() as session:
        seed_defaults(session)
    print("Seed data applied.")
