export interface Ingredient {
  id: number;
  name: string;
  category: string;
}

export interface MenuCondition {
  servings: number;
  max_cooking_time_min: number;
  use_up_ingredients: boolean;
  liked_categories: string[];
  disliked_categories: string[];
  allergies: string[];
  desired_courses: string[];
}

export const COURSE_OPTIONS = ["主食", "主菜", "副菜", "汁物"] as const;

export interface DraftMenuItem {
  recipe_id: string;
  menu_name: string;
  course: string;
  used_ingredients: string[];
  missing_ingredients: string[];
  steps: string[];
  cooking_time_min: number;
  difficulty: string;
  servings: number;
  ingredient_usage_rate: number;
}

export interface MenuResult {
  menu: DraftMenuItem;
  validation_status: string;
  retried: number;
}

export interface MenuHistoryEntry {
  id: number;
  condition: MenuCondition;
  generated_menu: DraftMenuItem;
  validation_status: string;
  created_at: string;
}

export const DEFAULT_CONDITION: MenuCondition = {
  servings: 2,
  max_cooking_time_min: 30,
  use_up_ingredients: true,
  liked_categories: [],
  disliked_categories: [],
  allergies: [],
  desired_courses: [],
};
