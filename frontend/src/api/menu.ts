import { apiRequest } from "./client";
import type { MenuCondition, MenuHistoryEntry, MenuResult } from "../types";

interface MenuGenerateResponse {
  options: MenuResult[];
}

export async function createMenu(
  extraIngredientsText: string,
  condition: MenuCondition,
  count = 3,
): Promise<MenuResult[]> {
  const response = await apiRequest<MenuGenerateResponse>("/menu", {
    method: "POST",
    body: JSON.stringify({ extra_ingredients_text: extraIngredientsText, condition, count }),
  });
  return response.options;
}

export function saveMenus(
  condition: MenuCondition,
  options: MenuResult[],
): Promise<MenuHistoryEntry[]> {
  return apiRequest<MenuHistoryEntry[]>("/menu/save", {
    method: "POST",
    body: JSON.stringify({ condition, options }),
  });
}

export function listHistory(): Promise<MenuHistoryEntry[]> {
  return apiRequest<MenuHistoryEntry[]>("/history");
}
