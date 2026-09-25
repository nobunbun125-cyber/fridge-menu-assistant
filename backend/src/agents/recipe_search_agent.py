"""レシピ検索Agent（RAGの検索部分）。LLMは使わず、recipe_storeのスコアリングのみで候補を返す。"""

from src.rag.recipe_store import search
from src.schemas.agent_io import MenuCondition, RecipeSearchAgentOutput


def run(ingredient_names: list[str], condition: MenuCondition, top_k: int = 5) -> RecipeSearchAgentOutput:
    candidates = search(ingredient_names, condition, top_k=top_k)
    return RecipeSearchAgentOutput(candidates=candidates)
