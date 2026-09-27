import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { Link } from "react-router-dom";
import { createIngredientsFromText, deleteIngredient, listIngredients } from "../api/ingredients";
import { ApiError } from "../api/client";
import type { Ingredient } from "../types";

export function FridgePage() {
  const [ingredients, setIngredients] = useState<Ingredient[]>([]);
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    try {
      setIngredients(await listIngredients());
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "食材の取得に失敗しました");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load();
  }, []);

  const handleAdd = async (event: FormEvent) => {
    event.preventDefault();
    if (!text.trim()) return;
    setSubmitting(true);
    setError(null);
    try {
      await createIngredientsFromText(text);
      setText("");
      await load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "食材の追加に失敗しました");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await deleteIngredient(id);
      setIngredients((prev) => prev.filter((i) => i.id !== id));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "削除に失敗しました");
    }
  };

  return (
    <div>
      <h1>冷蔵庫</h1>
      <p className="step-hint">
        ① ここで手持ちの食材を登録 → ② 「献立作成」で条件を指定 → ③ AIが献立を提案します
      </p>
      <form onSubmit={handleAdd} className="form-inline">
        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="例: 鶏もも肉とキャベツと卵があります"
        />
        <button type="submit" disabled={submitting}>
          追加
        </button>
      </form>
      {error && <p className="error-text">{error}</p>}
      {loading ? (
        <p>読み込み中...</p>
      ) : (
        <>
          <ul className="ingredient-list">
            {ingredients.map((ingredient) => (
              <li key={ingredient.id} className="ingredient-tag">
                <span>{ingredient.name}</span>
                <span className="category">{ingredient.category}</span>
                <button type="button" onClick={() => handleDelete(ingredient.id)} aria-label="削除">
                  ×
                </button>
              </li>
            ))}
          </ul>
          {ingredients.length === 0 ? (
            <p>
              まだ食材が登録されていません。上の欄に「鶏もも肉とキャベツと卵があります」のように
              文章で入力して「追加」を押してください。AIが自動で食材ごとに分けて登録します。
            </p>
          ) : (
            <p className="next-step">
              食材の登録ができたら
              <Link to="/menu/new">献立作成へ進む →</Link>
            </p>
          )}
        </>
      )}
    </div>
  );
}
