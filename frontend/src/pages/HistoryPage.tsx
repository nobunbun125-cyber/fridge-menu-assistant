import { useEffect, useState } from "react";
import { listHistory } from "../api/menu";
import { ApiError } from "../api/client";
import { MenuDetail } from "../components/MenuDetail";
import type { MenuHistoryEntry } from "../types";

export function HistoryPage() {
  const [entries, setEntries] = useState<MenuHistoryEntry[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        setEntries(await listHistory());
      } catch (err) {
        setError(err instanceof ApiError ? err.message : "履歴の取得に失敗しました");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const selected = entries.find((e) => e.id === selectedId);

  return (
    <div>
      <h1>履歴</h1>
      {error && <p className="error-text">{error}</p>}
      {loading ? (
        <p>読み込み中...</p>
      ) : entries.length === 0 ? (
        <p>まだ履歴がありません。</p>
      ) : (
        <div className="history-layout">
          <ul className="history-list">
            {entries.map((entry) => (
              <li key={entry.id}>
                <button
                  type="button"
                  className={`link-button ${selectedId === entry.id ? "active" : ""}`}
                  onClick={() => setSelectedId(entry.id)}
                >
                  {new Date(entry.created_at).toLocaleString()} — {entry.generated_menu.menu_name}
                </button>
              </li>
            ))}
          </ul>
          <div className="history-detail">
            {selected ? (
              <MenuDetail menu={selected.generated_menu} validationStatus={selected.validation_status} />
            ) : (
              <p>履歴を選択すると詳細が表示されます。</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
