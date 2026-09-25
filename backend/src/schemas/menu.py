from datetime import datetime

from pydantic import BaseModel

from src.schemas.agent_io import DraftMenuItem, MenuCondition


class MenuCreateRequest(BaseModel):
    extra_ingredients_text: str = ""
    condition: MenuCondition = MenuCondition()


class MenuResult(BaseModel):
    menu: DraftMenuItem
    validation_status: str
    retried: int = 0


class MenuHistoryOut(BaseModel):
    id: int
    condition: dict
    generated_menu: dict
    validation_status: str
    created_at: datetime

    model_config = {"from_attributes": True}
