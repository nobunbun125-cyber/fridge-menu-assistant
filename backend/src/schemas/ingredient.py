from pydantic import BaseModel


class IngredientTextInput(BaseModel):
    text: str


class IngredientCreate(BaseModel):
    name: str
    category: str


class IngredientOut(BaseModel):
    id: int
    name: str
    category: str

    model_config = {"from_attributes": True}
