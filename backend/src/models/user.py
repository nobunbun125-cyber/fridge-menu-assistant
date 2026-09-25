from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.ingredient import Ingredient
    from src.models.menu_history import MenuHistory
    from src.models.user_preference import UserPreference


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    ingredients: Mapped[list["Ingredient"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    menu_history: Mapped[list["MenuHistory"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    preference: Mapped["UserPreference"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
