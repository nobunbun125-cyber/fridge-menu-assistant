import { useState } from "react";
import type { FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { createMenu } from "../api/menu";
import { ApiError } from "../api/client";
import { DEFAULT_CONDITION } from "../types";
import type { MenuCondition } from "../types";

export function MenuCreatePage() {
  const [extraText, setExtraText] = useState("");
  const [condition, setCondition] = useState<MenuCondition>(DEFAULT_CONDITION);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const result = await createMenu(extraText, condition);
      navigate("/menu/result", { state: { result } });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "献立の生成に失敗しました");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div>
      <h1>献立作成</h1>
      <form onSubmit={handleSubmit} className="form">
        <label>
          追加で伝えたい食材（任意）
          <input
            type="text"
            value={extraText}
            onChange={(e) => setExtraText(e.target.value)}
            placeholder="例: あと味噌もあります"
          />
        </label>
        <label>
          人数
          <input
            type="number"
            min={1}
            max={10}
            value={condition.servings}
            onChange={(e) => setCondition({ ...condition, servings: Number(e.target.value) })}
          />
        </label>
        <label>
          調理時間の上限（分）
          <input
            type="number"
            min={5}
            max={180}
            value={condition.max_cooking_time_min}
            onChange={(e) =>
              setCondition({ ...condition, max_cooking_time_min: Number(e.target.value) })
            }
          />
        </label>
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={condition.use_up_ingredients}
            onChange={(e) => setCondition({ ...condition, use_up_ingredients: e.target.checked })}
          />
          できるだけ食材を使い切りたい
        </label>
        {error && <p className="error-text">{error}</p>}
        <button type="submit" disabled={submitting}>
          {submitting ? "AIが考え中..." : "提案してもらう"}
        </button>
      </form>
    </div>
  );
}
