import type { DraftMenuItem } from "../types";

const DIFFICULTY_LABEL: Record<string, string> = {
  easy: "かんたん",
  medium: "ふつう",
  hard: "むずかしい",
};

export function MenuDetail({
  menu,
  validationStatus,
}: {
  menu: DraftMenuItem;
  validationStatus?: string;
}) {
  return (
    <div className="menu-detail">
      <h2>{menu.menu_name}</h2>
      {validationStatus === "invalid" && (
        <p className="warning-text">
          ※ AIによる検証で一部の条件を満たせていない可能性があります。内容を確認してください。
        </p>
      )}
      <dl className="menu-meta">
        <dt>人数</dt>
        <dd>{menu.servings}人分</dd>
        <dt>調理時間</dt>
        <dd>{menu.cooking_time_min}分</dd>
        <dt>難易度</dt>
        <dd>{DIFFICULTY_LABEL[menu.difficulty] ?? menu.difficulty}</dd>
        <dt>食材使用率</dt>
        <dd>{Math.round(menu.ingredient_usage_rate * 100)}%</dd>
      </dl>

      <h3>使用する食材</h3>
      <ul>
        {menu.used_ingredients.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>

      {menu.missing_ingredients.length > 0 && (
        <>
          <h3>不足している食材</h3>
          <ul>
            {menu.missing_ingredients.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </>
      )}

      <h3>作り方</h3>
      <ol>
        {menu.steps.map((step, index) => (
          <li key={index}>{step}</li>
        ))}
      </ol>

      <p className="disclaimer">
        ※ 栄養・健康効果について断定的な保証をするものではありません。参考情報としてご利用ください。
      </p>
    </div>
  );
}
