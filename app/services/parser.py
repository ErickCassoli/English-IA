from __future__ import annotations

import json
from typing import TypeVar

from fastapi import HTTPException, status
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


def parse_contract(raw_text: str, model: type[T]) -> T:
    try:
        payload = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid JSON output: {exc}",
        ) from exc
    try:
        return model.model_validate(payload)
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=json.loads(exc.json()),
        ) from exc
