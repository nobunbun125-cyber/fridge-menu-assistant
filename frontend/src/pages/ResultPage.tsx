import { Link, useLocation } from "react-router-dom";
import { MenuDetail } from "../components/MenuDetail";
import type { MenuResult } from "../types";

export function ResultPage() {
  const location = useLocation();
  const state = location.state as { result?: MenuResult } | null;
  const result = state?.result;

  if (!result) {
    return (
      <div>
        <p>表示できる結果がありません。献立作成画面からやり直してください。</p>
        <Link to="/menu/new">献立作成へ戻る</Link>
      </div>
    );
  }

  return (
    <div>
      <h1>提案された献立</h1>
      <MenuDetail menu={result.menu} validationStatus={result.validation_status} />
      <Link to="/menu/new">別の献立を作成する</Link>
    </div>
  );
}
