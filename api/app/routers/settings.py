from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.repo import dao, models
from app.repo.db import get_db
from app.schemas.settings import SettingsResponse, SettingsUpdateRequest

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("", response_model=SettingsResponse)
def read_settings(db: Session = Depends(get_db)):
    settings = dao.get_settings(db)
    return SettingsResponse(
        llm_provider=settings.llm_provider.value, 
        llm_model=settings.llm_model,
        native_language=settings.native_language,
        target_language=settings.target_language
    )


@router.post("", response_model=SettingsResponse)
def update_settings(payload: SettingsUpdateRequest, db: Session = Depends(get_db)):
    try:
        provider = models.LLMProvider(payload.llm_provider)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid provider")
    model_name = payload.llm_model.strip()
    if not model_name:
        raise HTTPException(status_code=400, detail="llm_model is required")
    
    # Update languages if provided
    native_lang = payload.native_language if hasattr(payload, 'native_language') else "pt-BR"
    target_lang = payload.target_language if hasattr(payload, 'target_language') else "en"
    
    settings = dao.get_settings(db)
    settings.llm_provider = provider
    settings.llm_model = model_name
    settings.native_language = native_lang
    settings.target_language = target_lang
    settings.updated_at = models._now()
    db.add(settings)
    db.commit()
    
    return SettingsResponse(
        llm_provider=settings.llm_provider.value, 
        llm_model=settings.llm_model,
        native_language=settings.native_language,
        target_language=settings.target_language
    )
