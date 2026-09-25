import json
from typing import Any

import anthropic

from src.core.config import settings

_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)


def call_llm_json(
    system_prompt: str,
    user_prompt: str,
    model: str | None = None,
    max_tokens: int = 2048,
) -> dict[str, Any]:
    """LLMを呼び出し、応答をJSONとしてパースして返す。

    Claudeにはsystem_prompt側で「JSONのみを出力すること」を明示させる想定。
    """
    response = _client.messages.create(
        model=model or settings.anthropic_model_planning,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    text = "".join(block.text for block in response.content if block.type == "text")
    return _extract_json(text)


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"LLM応答からJSONを抽出できませんでした: {text!r}")
    return json.loads(text[start : end + 1])
