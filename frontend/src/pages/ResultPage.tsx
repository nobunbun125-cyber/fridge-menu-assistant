import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { MenuDetail } from "../components/MenuDetail";
import { saveMenus } from "../api/menu";
import { ApiError } from "../api/client";
import type { MenuCondition, MenuResult } from "../types";

export function ResultPage() {
  const location = useLocation();
  const state = location.state as { options?: MenuResult[]; condition?: MenuCondition } | null;
  const options = state?.options ?? [];
  const condition = state?.condition;

  const [activeIndex, setActiveIndex] = useState(0);
  const [selected, setSelected] = useState<Set<number>>(new Set());
  // 一度保存した献立を再度チェックしても二重保存しないよう、保存済みのindexを別途覚えておく。
  const [savedIndices, setSavedIndices] = useState<Set<number>>(new Set());
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (options.length === 0 || !condition) {
    return (
      <div>
        <p>表示できる結果がありません。献立作成画面からやり直してください。</p>
        <Link to="/menu/new">献立作成へ戻る</Link>
      </div>
    );
  }

  const toggle = (index: number) => {
    if (savedIndices.has(index)) return;
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(index)) {
        next.delete(index);
      } else {
        next.add(index);
      }
      return next;
    });
  };

  const unsavedSelected = Array.from(selected).filter((index) => !savedIndices.has(index));

  const handleSave = async () => {
    if (unsavedSelected.length === 0) return;
    setSaving(true);
    setError(null);
    try {
      const chosen = unsavedSelected.map((index) => options[index]);
      await saveMenus(condition, chosen);
      setSavedIndices((prev) => new Set([...prev, ...unsavedSelected]));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "保存に失敗しました");
    } finally {
      setSaving(false);
    }
  };

  const activeOption = options[activeIndex];

  return (
    <div>
      <h1>提案された献立（{options.length}件）</h1>
      <p className="step-hint">
        料理名のタブを切り替えて内容を確認できます。気に入った献立にチェックを入れて保存してください（複数選択可）。
      </p>

      <div className="menu-tabs" role="tablist">
        {options.map((option, index) => (
          <div
            key={`${option.menu.recipe_id}-${index}`}
            className={`menu-tab ${index === activeIndex ? "active" : ""} ${
              selected.has(index) ? "checked" : ""
            }`}
          >
            <input
              type="checkbox"
              checked={selected.has(index)}
              disabled={savedIndices.has(index)}
              onChange={() => toggle(index)}
              aria-label={`${option.menu.menu_name}を履歴に保存する対象にする`}
            />
            <button
              type="button"
              role="tab"
              aria-selected={index === activeIndex}
              className="menu-tab-label"
              onClick={() => setActiveIndex(index)}
            >
              {option.menu.course && <span className="badge-inline course">{option.menu.course}</span>}
              {option.menu.menu_name}
              {index === 0 && <span className="badge-inline">おすすめ</span>}
              {savedIndices.has(index) && <span className="badge-inline saved">保存済み</span>}
            </button>
          </div>
        ))}
      </div>

      <div className="menu-tab-panel">
        <MenuDetail menu={activeOption.menu} validationStatus={activeOption.validation_status} />
      </div>

      {error && <p className="error-text">{error}</p>}

      {savedIndices.size > 0 && (
        <p className="next-step">
          これまでに{savedIndices.size}件を履歴に保存しました。<Link to="/history">履歴を見る</Link>
        </p>
      )}

      <button type="button" onClick={handleSave} disabled={saving || unsavedSelected.length === 0}>
        {saving ? "保存中..." : `選択した${unsavedSelected.length}件を履歴に保存`}
      </button>

      <p className="next-step">
        <Link to="/menu/new">別の条件でもう一度提案してもらう</Link>
      </p>
    </div>
  );
}
