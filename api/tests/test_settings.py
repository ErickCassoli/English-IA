from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.repo import dao, models
from app.repo.db import Base


def test_update_settings_persists_choice():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, future=True)
    session = Session()
    try:
        settings = dao.update_settings(session, models.LLMProvider.OPENAI, "gpt-4o-mini")
        session.commit()
        assert settings.llm_provider == models.LLMProvider.OPENAI
        assert settings.llm_model == "gpt-4o-mini"
    finally:
        session.close()
