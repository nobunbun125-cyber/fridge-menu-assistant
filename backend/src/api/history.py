from fastapi import APIRouter, Depends
from sqlalchemy import desc
from sqlalchemy.orm import Session

from src.api.deps import get_current_user
from src.db.session import get_db
from src.models.menu_history import MenuHistory
from src.models.user import User
from src.schemas.menu import MenuHistoryOut

router = APIRouter(prefix="/history", tags=["history"])


@router.get("", response_model=list[MenuHistoryOut])
def list_history(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[MenuHistory]:
    return (
        db.query(MenuHistory)
        .filter(MenuHistory.user_id == current_user.id)
        .order_by(desc(MenuHistory.created_at))
        .all()
    )
