"""Agent間で受け渡しするデータの型定義。

Orchestratorはこれらの型だけを介してAgent同士を接続する。
Agentの実装が変わっても、この契約が変わらない限り他のAgentに影響しない。
"""

from pydantic import BaseModel, Field


class StructuredIngredient(BaseModel):
    name: str
    category: str  # meat / vegetable / egg / seasoning / dairy / other


class IngredientAgentOutput(BaseModel):
    ingredients: list[StructuredIngredient]


class MenuCondition(BaseModel):
    servings: int = Field(default=2, ge=1, le=10)
    max_cooking_time_min: int = Field(default=30, ge=5, le=180)
    use_up_ingredients: bool = True
    liked_categories: list[str] = Field(default_factory=list)
    disliked_categories: list[str] = Field(default_factory=list)
    allergies: list[str] = Field(default_factory=list)
    # 主食/主菜/副菜/汁物。空リストなら絞り込みなし（全種類が対象）。
    desired_courses: list[str] = Field(default_factory=list)


class CandidateRecipe(BaseModel):
    id: str
    name: str
    category: str
    course: str  # 主食 / 主菜 / 副菜 / 汁物
    ingredients: list[str]
    steps: list[str]
    cooking_time_min: int
    difficulty: str  # easy / medium / hard
    servings: int
    match_score: float


class RecipeSearchAgentOutput(BaseModel):
    candidates: list[CandidateRecipe]


class DraftMenuItem(BaseModel):
    recipe_id: str
    menu_name: str
    course: str = ""  # LLMには出力させず、orchestratorが元レシピの値で確定させる
    used_ingredients: list[str]
    missing_ingredients: list[str]
    steps: list[str]
    cooking_time_min: int
    difficulty: str
    servings: int
    ingredient_usage_rate: float = Field(ge=0, le=1)


class MenuPlanningAgentOutput(BaseModel):
    menu: DraftMenuItem
    note: str = ""


class ValidationIssue(BaseModel):
    code: str  # unknown_ingredient / time_exceeded / servings_mismatch / fabricated_step
    detail: str


class ValidationAgentOutput(BaseModel):
    is_valid: bool
    issues: list[ValidationIssue] = Field(default_factory=list)
