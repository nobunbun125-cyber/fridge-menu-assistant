import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { createMenu } from "../api/menu";
import { listIngredients } from "../api/ingredients";
import { ApiError } from "../api/client";
import { COURSE_OPTIONS, DEFAULT_CONDITION } from "../types";
import type { MenuCondition } from "../types";

function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max);
}

export function MenuCreatePage() {
  const [extraText, setExtraText] = useState("");
  const [useUpIngredients, setUseUpIngredients] = useState(DEFAULT_CONDITION.use_up_ingredients);
  // number inputへ数値stateを直接bindすると、桁を消して打ち直す際に値が0へ戻ってしまい
  // 入力できないように見えるため、入力中は文字列として保持し送信時にのみ数値化する。
  const [servingsText, setServingsText] = useState(String(DEFAULT_CONDITION.servings));
  const [timeText, setTimeText] = useState(String(DEFAULT_CONDITION.max_cooking_time_min));
  const [count, setCount] = useState(3);
  const [desiredCourses, setDesiredCourses] = useState<string[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasFridgeIngredients, setHasFridgeIngredients] = useState<boolean | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    listIngredients()
      .then((list) => setHasFridgeIngredients(list.length > 0))
      .catch(() => setHasFridgeIngredients(null));
  }, []);

  const toggleCourse = (course: string) => {
    setDesiredCourses((prev) =>
      prev.includes(course) ? prev.filter((c) => c !== course) : [...prev, course],
    );
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setSubmitting(true);
    setError(null);

    const condition: MenuCondition = {
      ...DEFAULT_CONDITION,
      use_up_ingredients: useUpIngredients,
      servings: clamp(Number(servingsText) || DEFAULT_CONDITION.servings, 1, 10),
      max_cooking_time_min: clamp(
        Number(timeText) || DEFAULT_CONDITION.max_cooking_time_min,
        5,
        180,
      ),
      desired_courses: desiredCourses,
    };

    try {
      const options = await createMenu(extraText, condition, count);
      navigate("/menu/result", { state: { options, condition } });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "献立の生成に失敗しました");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div>
      <h1>献立作成</h1>
      {hasFridgeIngredients === false && (
        <p className="warning-text">
          冷蔵庫に食材が登録されていません。先に<Link to="/fridge">冷蔵庫ページ</Link>
          で食材を登録するか、下の「追加で伝えたい食材」に使いたい食材を入力してください。
        </p>
      )}
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
            value={servingsText}
            onChange={(e) => setServingsText(e.target.value)}
          />
        </label>
        <label>
          調理時間の上限（分）
          <input
            type="number"
            min={5}
            max={180}
            value={timeText}
            onChange={(e) => setTimeText(e.target.value)}
          />
        </label>
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={useUpIngredients}
            onChange={(e) => setUseUpIngredients(e.target.checked)}
          />
          できるだけ食材を使い切りたい
        </label>
        <div>
          <span className="form-group-label">含めたい料理の種類（未選択なら指定なし）</span>
          <div className="course-options">
            {COURSE_OPTIONS.map((course) => (
              <label key={course} className="checkbox-label course-checkbox">
                <input
                  type="checkbox"
                  checked={desiredCourses.includes(course)}
                  onChange={() => toggleCourse(course)}
                />
                {course}
              </label>
            ))}
          </div>
        </div>
        <label>
          提案してほしい件数
          <select value={count} onChange={(e) => setCount(Number(e.target.value))}>
            <option value={1}>1件（一番のおすすめだけ）</option>
            <option value={2}>2件</option>
            <option value={3}>3件</option>
          </select>
        </label>
        {error && <p className="error-text">{error}</p>}
        <button type="submit" disabled={submitting}>
          {submitting ? "AIが考え中..." : "提案してもらう"}
        </button>
      </form>
    </div>
  );
}
