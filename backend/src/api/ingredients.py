from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.agents import ingredient_agent
from src.api.deps import get_current_user
from src.db.session import get_db
from src.models.ingredient import Ingredient
from src.models.user import User
from src.schemas.ingredient import IngredientCreate, IngredientOut, IngredientTextInput

router = APIRouter(prefix="/ingredients", tags=["ingredients"])


@router.get("", response_model=list[IngredientOut])
def list_ingredients(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[Ingredient]:
    return db.query(Ingredient).filter(Ingredient.user_id == current_user.id).all()


@router.post("", response_model=IngredientOut, status_code=status.HTTP_201_CREATED)
def create_ingredient(
    payload: IngredientCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Ingredient:
    ingredient = Ingredient(user_id=current_user.id, name=payload.name, category=payload.category)
    db.add(ingredient)
    db.commit()
    db.refresh(ingredient)
    return ingredient


@router.post("/from-text", response_model=list[IngredientOut], status_code=status.HTTP_201_CREATED)
def create_ingredients_from_text(
    payload: IngredientTextInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Ingredient]:
    parsed = ingredient_agent.run(payload.text)
    created: list[Ingredient] = []
    for item in parsed.ingredients:
        ingredient = Ingredient(user_id=current_user.id, name=item.name, category=item.category)
        db.add(ingredient)
        created.append(ingredient)
    db.commit()
    for ingredient in created:
        db.refresh(ingredient)
    return created


@router.delete("/{ingredient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ingredient(
    ingredient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    ingredient = (
        db.query(Ingredient)
        .filter(Ingredient.id == ingredient_id, Ingredient.user_id == current_user.id)
        .first()
    )
    if ingredient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="食材が見つかりません")
    db.delete(ingredient)
    db.commit()
