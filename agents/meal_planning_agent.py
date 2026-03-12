# =============================================================================
# agents/meal_planning_agent.py
# AGENT 2 — Meal Planning Agent
#
# Responsibilities:
#   • Generate personalized daily meal plans
#   • Generate 7-day weekly meal plans
#   • Provide meal swap alternatives (3 options per slot)
#   • Generate grocery lists from weekly plans
#   • Attach nutrition scores to every meal (via NutritionAgent)
# =============================================================================

import os
import pandas as pd # type: ignore
import random
from .agent_base import BaseAgent

# ──────────────────────────────────────────────────────────────────────────────
MEAL_SPLIT = {
    "breakfast": 0.25,
    "lunch":     0.35,
    "dinner":    0.30,
    "snack":     0.10,
}

MEAL_META = {
    "breakfast": {"icon": "🌅", "label": "Breakfast",  "time": "7:00 – 9:00 AM"},
    "lunch":     {"icon": "☀️",  "label": "Lunch",      "time": "12:30 – 2:00 PM"},
    "dinner":    {"icon": "🌙", "label": "Dinner",     "time": "7:00 – 9:00 PM"},
    "snack":     {"icon": "🍎", "label": "Snack",      "time": "4:00 – 5:00 PM"},
}

DIET_COMPAT = {
    "Vegetarian":     ["vegetarian", "vegan"],
    "Vegan":          ["vegan"],
    "Non-Vegetarian": ["vegetarian", "vegan", "non-vegetarian"],
}

DAYS = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

# Grocery category → keywords in food category/name column
GROCERY_CATEGORIES = {
    "🌾 Grains & Cereals": [
        "rice","roti","naan","paratha","dosa","rava","biryani","bread"
    ],

    "🥩 Protein Sources": [
        "paneer","chicken","mutton","egg","dal","rajma","soya","chana"
    ],

    "🍎 Fruits": [
        "banana","apple","orange","papaya","mango"
    ],

    "🥜 Nuts & Seeds": [
        "almond","cashew","walnut","pista","makhana"
    ]
}

DISH_TO_INGREDIENTS = {
    "chicken biryani": ["rice", "chicken", "spices"],
    "vegetable biryani": ["rice", "vegetables", "spices"],
    "paneer paratha": ["wheat flour", "paneer"],
    "paneer bhurji": ["paneer", "tomato", "onion"],
    "dal makhani": ["black dal", "butter"],
    "rava dosa": ["rava", "curd"],
    "idli with sambar": ["idli batter", "toor dal"],
    "idli with chutney": ["idli batter", "coconut"],
    "vegetable uttapam": ["dosa batter", "vegetables"],
    "masala omelette": ["eggs", "onion"],
    "lassi": ["curd"],
    "soya chunks masala": ["soya chunks"]
}

class MealPlanningAgent(BaseAgent):
    """
    Agent 2 — Meal Planning Agent.

    Expected payload keys (from NutritionAgent output + extras):
        target_calories (int)
        diet_preference (str)
        allergies       (list[str])
        goal            (str)
        cuisine         (str)  — "both" | "indian" | "international"
        mode            (str)  — "daily" | "weekly" | "swap"
        swap_slot       (str)  — required if mode=="swap"  e.g. "lunch"
        swap_exclude    (str)  — food name to exclude from swap suggestions

    Output dict keys (varies by mode):
        daily:   { meals, daily_totals, target_calories }
        weekly:  { Monday: daily_plan, …, Sunday: daily_plan }
        swap:    { alternatives: [meal, meal, meal] }
    """

    def __init__(self):
        super().__init__(
            name="Meal Planning Agent",
            description="Generates daily/weekly plans, swaps & grocery lists",
            emoji="🍽️",
        )
        self._df: pd.DataFrame | None = None  # cache dataframe

    # ── Public entry point ────────────────────────────────────────────────────

    def run(self, payload: dict) -> dict:
        self._ensure_data_loaded()
        mode = payload.get("mode", "daily")

        if mode == "daily":
            return self._daily(payload)
        elif mode == "weekly":
            return self._weekly(payload)
        elif mode == "swap":
            return self._swap(payload)
        elif mode == "grocery":
            return self._grocery(payload)
        else:
            raise ValueError(f"Unknown mode: {mode!r}. Use 'daily', 'weekly', 'swap', or 'grocery'.")

    # ── Daily plan ────────────────────────────────────────────────────────────

    def _daily(self, payload: dict) -> dict:
        filtered = self._filter(payload)
        target = payload.get("target_calories", payload.get("calories", 2000))
        goal     = payload.get("goal", "Maintain Weight")

        meals  = {}
        totals = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0, "fiber": 0}

        for slot, frac in MEAL_SPLIT.items():
            meal = self._pick(filtered, slot, target * frac)
            meal.update(MEAL_META[slot])
            # Attach score — import here to avoid circular dependency
            from .nutrition_agent import NutritionAgent
            score_info = NutritionAgent.score_meal(meal, target, goal)
            meal["score"]       = score_info["score"]
            meal["score_grade"] = score_info["grade"]
            meal["score_tip"]   = score_info["tip"]
            meal["score_breakdown"] = score_info["breakdown"]
            meals[slot] = meal

            for k in ["calories", "protein", "carbs", "fat", "fiber"]:
                totals[k] += meal.get(k, 0)

        return {"meals": meals, "daily_totals": totals, "target_calories": target}

    # ── Weekly plan ───────────────────────────────────────────────────────────

    def _weekly(self, payload: dict) -> dict:

     used_meals = set()
     used_categories = set()

     weekly_plan = {}

     for day in DAYS:

        daily = self._daily(payload)

        # filter repeated foods
        for slot, meal in daily["meals"].items():

            if meal["food_name"] in used_meals:
                continue

            if meal["category"] in used_categories:
                continue

            used_meals.add(meal["food_name"])
            used_categories.add(meal["category"])

        weekly_plan[day] = daily

     return {"weekly": weekly_plan}

    # ── Meal swap (3 alternatives) ────────────────────────────────────────────

    def _swap(self, payload: dict) -> dict:
    
     slot = payload.get("swap_slot", "lunch").lower()
     exclude = payload.get("swap_exclude", "")
     target  = payload.get("target_calories", 2000)
     goal    = payload.get("goal", "Maintain Weight")
     filtered = self._filter(payload)
     pool = filtered[filtered["meal_type"].str.lower() == slot].copy()
     # remove duplicate foods
     pool = pool.drop_duplicates(subset=["food_name"])
     print("SWAP FUNCTION RUNNING")
     print("SLOT:", slot)
     print("EXCLUDE:", exclude)
     # remove the current meal
     if exclude:
      pool = pool[
        ~pool["food_name"]
        .str.lower()
        .str.strip()
        .eq(exclude.lower().strip())
      ]
     if pool.empty:
        return {"alternatives": []}
     # calorie target for that meal
     slot_cal = target * MEAL_SPLIT.get(slot, 0.25)
     pool["diff"] = abs(pool["calories"] - slot_cal)
     # choose top closest meals
     pool = pool.nsmallest(12, "diff")
     # shuffle for variety
     pool = pool.sample(frac=1).reset_index(drop=True)

     alternatives = []

     for _, row in pool.iterrows():

      meal = self._row_to_meal(row)

      if meal["food_name"].lower() == exclude.lower():
        continue

      if meal["food_name"] not in [a["food_name"] for a in alternatives]:

        meal.update(MEAL_META.get(slot, {}))

        from .nutrition_agent import NutritionAgent
        si = NutritionAgent.score_meal(meal, target, goal)

        meal["score"] = si["score"]
        meal["score_grade"] = si["grade"]

        alternatives.append(meal)

      if len(alternatives) == 3:
        break
      print("SWAP OPTIONS:", [a["food_name"] for a in alternatives])
     return {"alternatives": alternatives}

    # ── Grocery list ──────────────────────────────────────────────────────────

    def generate_grocery_list(self, weekly_plan: dict) -> dict:
     """
     Build a categorized grocery list from a weekly plan dict.

     Returns:
         { "🌾 Grains & Cereals": [food1, food2, …], … }
     """

     # Collect all unique food items from weekly plan
     items = []

     for day_plan in weekly_plan.values():

        if not isinstance(day_plan, dict):
            continue

        meals = day_plan.get("meals", {})

        for meal in meals.values():

            food_name = meal.get("food_name", "").lower()
            category = meal.get("category", "").lower()
            ingredients = DISH_TO_INGREDIENTS.get(food_name, [food_name])

            for ing in ingredients:
                items.append({
                    "name": ing,
                    "category": category
                })

    # Remove duplicates
     seen = set()
     unique_items = []

     for item in items:
        if item["name"] not in seen:
            seen.add(item["name"])
            unique_items.append(item)

    # Grocery bins
     grocery = {cat: [] for cat in GROCERY_CATEGORIES}
     grocery["🛒 Other Items"] = []

    # Categorization
     for item in unique_items:

        name_lower = item["name"].lower()
        cat_lower = item["category"]

        placed = False

        # PRIORITY 1 → Protein
        for kw in GROCERY_CATEGORIES.get("🥩 Protein Sources", []):
            if kw in name_lower or kw in cat_lower:
                grocery["🥩 Protein Sources"].append(item["name"])
                placed = True
                break

        if placed:
            continue

        # PRIORITY 2 → Fruits
        for kw in GROCERY_CATEGORIES.get("🍎 Fruits", []):
            if kw in name_lower or kw in cat_lower:
                grocery["🍎 Fruits"].append(item["name"])
                placed = True
                break

        if placed:
            continue

        # PRIORITY 3 → Nuts & Seeds
        for kw in GROCERY_CATEGORIES.get("🥜 Nuts & Seeds", []):
            if kw in name_lower or kw in cat_lower:
                grocery["🥜 Nuts & Seeds"].append(item["name"])
                placed = True
                break

        if placed:
            continue

        # PRIORITY 4 → Grains
        for kw in GROCERY_CATEGORIES.get("🌾 Grains & Cereals", []):
            if kw in name_lower or kw in cat_lower:
                grocery["🌾 Grains & Cereals"].append(item["name"])
                placed = True
                break

        if not placed:
            grocery["🛒 Other Items"].append(item["name"])

    # Remove empty categories
     return {k: sorted(v) for k, v in grocery.items() if v}

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _ensure_data_loaded(self):
        if self._df is not None:
            return
        candidates = [
            "foods_dataset.csv",
            os.path.join(os.path.dirname(__file__), "..", "foods_dataset.csv"),
        ]
        for p in candidates:
            if os.path.exists(p):
                df = pd.read_csv(p)
                df.columns = [c.strip().lower() for c in df.columns]
                self._df = df
                return
        raise FileNotFoundError("foods_dataset.csv not found.")

    def _filter(self, payload: dict) -> pd.DataFrame:
        df       = self._df.copy()
        diet     = payload.get("diet_preference", "Non-Vegetarian")
        allergies= payload.get("allergies", [])
        cuisine  = payload.get("cuisine", "both").lower()

        allowed = DIET_COMPAT.get(diet, ["vegetarian","vegan","non-vegetarian"])
        df = df[df["diet_type"].isin(allowed)]

        for allergen in allergies:
            allergen = allergen.strip().lower()
            if not allergen:
                continue
            mask = (
                df["food_name"].str.lower().str.contains(allergen, na=False) |
                df["category"].str.lower().str.contains(allergen, na=False)
            )
            df = df[~mask]

        if cuisine == "indian":
            df = df[df["cuisine"] == "indian"]
        elif cuisine == "international":
            df = df[df["cuisine"] == "international"]

        return df.copy()

    def _pick(self, df: pd.DataFrame, meal_type: str, cal_target: float) -> dict:
     pool = df[df["meal_type"] == meal_type].copy()
     pool = pool.drop_duplicates(subset=["food_name"])
     if pool.empty:
        return {
            "food_name": f"Balanced {meal_type.title()}",
            "calories": int(cal_target),
            "protein": 20,
            "carbs": 45,
            "fat": 10,
            "fiber": 5,
            "description": "Custom meal — consult your nutritionist.",
            "category": "General",
            "cuisine": "any",
        }
     pool["diff"] = abs(pool["calories"] - cal_target)
     # choose top closest meals
     close = pool[pool["diff"] <= pool["diff"].min() + 120]
     # randomise selection for variety
     choice = close.sample(1).iloc[0]
     return self._row_to_meal(choice)

    @staticmethod
    def _row_to_meal(row) -> dict:
        return {
            "food_name":   row["food_name"],
            "calories":    int(row["calories"]),
            "protein":     int(row["protein"]),
            "carbs":       int(row["carbs"]),
            "fat":         int(row["fat"]),
            "fiber":       int(row.get("fiber", 0)),
            "description": str(row.get("description", "")),
            "category":    str(row.get("category", "")),
            "cuisine":     str(row.get("cuisine", "")),
        }

    # ── Compact text summary for AI context ──────────────────────────────────

    @staticmethod
    def get_plan_summary(daily_plan: dict) -> str:
        lines = ["Today's meal plan:"]
        for meal in daily_plan["meals"].values():
            lines.append(
                f"  {meal['label']}: {meal['food_name']} "
                f"({meal['calories']} cal, P:{meal['protein']}g, "
                f"C:{meal['carbs']}g, F:{meal['fat']}g, Score:{meal.get('score','?')}/10)"
            )
        t = daily_plan["daily_totals"]
        lines.append(
            f"  TOTAL — {t['calories']} cal | "
            f"Protein {t['protein']}g | Carbs {t['carbs']}g | Fat {t['fat']}g"
        )
        return "\n".join(lines)
