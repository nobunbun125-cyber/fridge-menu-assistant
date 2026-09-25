import { apiRequest } from "./client";
import type { MenuCondition, MenuHistoryEntry, MenuResult } from "../types";

export function createMenu(
  extraIngredientsText: string,
  condition: MenuCondition,
): Promise<MenuResult> {
  return apiRequest<MenuResult>("/menu", {
    method: "POST",
    body: JSON.stringify({ extra_ingredients_text: extraIngredientsText, condition }),
  });
}

export function listHistory(): Promise<MenuHistoryEntry[]> {
  return apiRequest<MenuHistoryEntry[]>("/history");
}
