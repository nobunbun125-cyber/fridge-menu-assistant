"""食材解析Agent: 自然言語の食材テキストを構造化データに変換する。"""

from src.core.llm_client import call_llm_json
from src.schemas.agent_io import IngredientAgentOutput

_SYSTEM_PROMPT = """あなたは食材解析AIです。
ユーザーが入力した自然言語のテキストから、食材名とカテゴリを抽出してください。
カテゴリは次のいずれかを使ってください: meat, vegetable, egg, seasoning, dairy, fish, other

出力は必ず次のJSON形式のみで返してください。説明文や前置きは不要です。
{
  "ingredients": [
    {"name": "食材名", "category": "カテゴリ"}
  ]
}
"""


def run(raw_text: str) -> IngredientAgentOutput:
    if not raw_text.strip():
        return IngredientAgentOutput(ingredients=[])
    data = call_llm_json(_SYSTEM_PROMPT, raw_text, max_tokens=1024)
    return IngredientAgentOutput.model_validate(data)
