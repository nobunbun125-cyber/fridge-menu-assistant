from datetime import datetime

from pydantic import BaseModel, Field

from src.schemas.agent_io import DraftMenuItem, MenuCondition


class MenuCreateRequest(BaseModel):
    extra_ingredients_text: str = ""
    condition: MenuCondition = MenuCondition()
    count: int = Field(default=3, ge=1, le=5)


class MenuResult(BaseModel):
    menu: DraftMenuItem
    validation_status: str
    retried: int = 0


class MenuGenerateResponse(BaseModel):
    options: list[MenuResult]


class MenuSaveRequest(BaseModel):
    condition: MenuCondition
    options: list[MenuResult] = Field(min_length=1)


class MenuHistoryOut(BaseModel):
    id: int
    condition: dict
    generated_menu: dict
    validation_status: str
    created_at: datetime

    model_config = {"from_attributes": True}
