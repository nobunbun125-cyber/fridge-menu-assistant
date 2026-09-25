from typing import TYPE_CHECKING

from sqlalchemy import JSON, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.user import User


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    liked_categories: Mapped[list] = mapped_column(JSON, default=list)
    disliked_categories: Mapped[list] = mapped_column(JSON, default=list)
    allergies: Mapped[list] = mapped_column(JSON, default=list)
    default_servings: Mapped[int] = mapped_column(Integer, default=2)
    default_time_limit_min: Mapped[int] = mapped_column(Integer, default=30)

    user: Mapped["User"] = relationship(back_populates="preference")
