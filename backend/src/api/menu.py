from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.agents.orchestrator import MenuGenerationError, generate_menu
from src.api.deps import get_current_user
from src.db.session import get_db
from src.models.ingredient import Ingredient
from src.models.menu_history import MenuHistory
from src.models.user import User
from src.schemas.menu import MenuCreateRequest, MenuResult

router = APIRouter(prefix="/menu", tags=["menu"])


@router.post("", response_model=MenuResult)
def create_menu(
    payload: MenuCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MenuResult:
    existing = db.query(Ingredient).filter(Ingredient.user_id == current_user.id).all()
    existing_names = [i.name for i in existing]

    try:
        result = generate_menu(payload.extra_ingredients_text, existing_names, payload.condition)
    except MenuGenerationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    history = MenuHistory(
        user_id=current_user.id,
        condition=payload.condition.model_dump(),
        generated_menu=result.menu.model_dump(),
        validation_status=result.validation_status,
    )
    db.add(history)
    db.commit()

    return result
