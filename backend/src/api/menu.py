from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.agents.orchestrator import MenuGenerationError, generate_menus
from src.api.deps import get_current_user
from src.db.session import get_db
from src.models.ingredient import Ingredient
from src.models.menu_history import MenuHistory
from src.models.user import User
from src.schemas.menu import (
    MenuCreateRequest,
    MenuGenerateResponse,
    MenuHistoryOut,
    MenuSaveRequest,
)

router = APIRouter(prefix="/menu", tags=["menu"])


@router.post("", response_model=MenuGenerateResponse)
def create_menu(
    payload: MenuCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MenuGenerateResponse:
    existing = db.query(Ingredient).filter(Ingredient.user_id == current_user.id).all()
    existing_names = [i.name for i in existing]

    try:
        results = generate_menus(
            payload.extra_ingredients_text, existing_names, payload.condition, count=payload.count
        )
    except MenuGenerationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    return MenuGenerateResponse(options=results)


@router.post("/save", response_model=list[MenuHistoryOut], status_code=status.HTTP_201_CREATED)
def save_menus(
    payload: MenuSaveRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[MenuHistory]:
    saved: list[MenuHistory] = []
    for option in payload.options:
        history = MenuHistory(
            user_id=current_user.id,
            condition=payload.condition.model_dump(),
            generated_menu=option.menu.model_dump(),
            validation_status=option.validation_status,
        )
        db.add(history)
        saved.append(history)

    db.commit()
    for history in saved:
        db.refresh(history)
    return saved
