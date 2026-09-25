import { apiRequest } from "./client";
import type { Ingredient } from "../types";

export function listIngredients(): Promise<Ingredient[]> {
  return apiRequest<Ingredient[]>("/ingredients");
}

export function createIngredient(name: string, category: string): Promise<Ingredient> {
  return apiRequest<Ingredient>("/ingredients", {
    method: "POST",
    body: JSON.stringify({ name, category }),
  });
}

export function createIngredientsFromText(text: string): Promise<Ingredient[]> {
  return apiRequest<Ingredient[]>("/ingredients/from-text", {
    method: "POST",
    body: JSON.stringify({ text }),
  });
}

export function deleteIngredient(id: number): Promise<void> {
  return apiRequest<void>(`/ingredients/${id}`, { method: "DELETE" });
}
