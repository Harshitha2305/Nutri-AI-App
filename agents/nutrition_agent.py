# =============================================================================
# agents/nutrition_agent.py
# AGENT 1 — Nutrition Analysis Agent
#
# Responsibilities:
#   • Calculate BMI, BMR, TDEE, target calories, macros, hydration goal
#   • Compute a Nutrition Score for any meal (0–10)
#   • Apply smart goal-based diet adjustments
#   • Produce a machine-readable profile dict for all other agents to use
# =============================================================================

from .agent_base import BaseAgent

# ──────────────────────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────────────────────
ACTIVITY_MULTIPLIERS = {
    "Sedentary (little/no exercise)":      1.2,
    "Lightly Active (1-3 days/week)":      1.375,
    "Moderately Active (3-5 days/week)":   1.55,
    "Very Active (6-7 days/week)":         1.725,
    "Extra Active (athlete/physical job)": 1.9,
}

GOAL_ADJUSTMENTS = {
    "Lose Weight":     -500,
    "Maintain Weight":  0,
    "Gain Muscle":     +300,
}

# Macro ratios (protein%, carbs%, fat%) by goal
MACRO_RATIOS = {
    "Lose Weight":     {"protein": 0.35, "carbs": 0.40, "fat": 0.25},
    "Maintain Weight": {"protein": 0.30, "carbs": 0.45, "fat": 0.25},
    "Gain Muscle":     {"protein": 0.30, "carbs": 0.50, "fat": 0.20},
}

BMI_CATEGORIES = [
    (18.5, "Underweight", "#3B82F6", "📉",
     "Focus on nutrient-dense foods and strength training to build healthy mass."),
    (25.0, "Normal Weight", "#22C55E", "✅",
     "Great! Maintain your weight with balanced nutrition and regular exercise."),
    (30.0, "Overweight", "#F59E0B", "⚠️",
     "A moderate calorie deficit with cardio can help reach your healthy range."),
    (99.0, "Obese", "#EF4444", "🔴",
     "Consult a healthcare provider. Start with small dietary changes and gentle exercise."),
]


class NutritionAgent(BaseAgent):
    """
    Agent 1 — Nutrition Analysis Agent.

    Input payload keys (all required):
        age, gender, weight_kg, height_cm, activity_level, goal,
        diet_preference, allergies (list[str])

    Output dict keys:
        bmi, bmi_category, bmi_color, bmi_emoji, bmi_advice,
        bmr, tdee, target_calories,
        protein_g, carbs_g, fat_g,
        water_litres,
        goal, diet_preference, allergies  ← passed through for other agents
    """

    def __init__(self):
        super().__init__(
            name="Nutrition Analysis Agent",
            description="Calculates BMI, BMR, TDEE, macros & hydration",
            emoji="🔬",
        )

    # ── Core entry point ──────────────────────────────────────────────────────

    def run(self, payload: dict) -> dict:
        age            = payload["age"]
        gender         = payload["gender"]
        weight_kg      = float(payload["weight_kg"])
        height_cm      = float(payload["height_cm"])
        activity_level = payload["activity_level"]
        goal           = payload["goal"]
        diet_pref      = payload.get("diet_preference", "Vegetarian")
        allergies      = payload.get("allergies", [])

        bmi        = self._bmi(weight_kg, height_cm)
        bmi_info   = self._bmi_category(bmi)
        bmr        = self._bmr(weight_kg, height_cm, age, gender)
        tdee       = self._tdee(bmr, activity_level)
        target     = self._target_calories(tdee, goal)
        macros     = self._macros(target, goal)
        water      = self._water(weight_kg, activity_level)

        return {
            "bmi":             bmi,
            "bmi_category":    bmi_info["category"],
            "bmi_color":       bmi_info["color"],
            "bmi_emoji":       bmi_info["emoji"],
            "bmi_advice":      bmi_info["advice"],
            "bmr":             bmr,
            "tdee":            tdee,
            "target_calories": target,
            "protein_g":       macros["protein"],
            "carbs_g":         macros["carbs"],
            "fat_g":           macros["fat"],
            "water_litres":    water,
            # Pass-through fields other agents need:
            "goal":            goal,
            "diet_preference": diet_pref,
            "allergies":       allergies,
            "age":             age,
            "gender":          gender,
            "weight_kg":       weight_kg,
            "height_cm":       height_cm,
            "activity_level":  activity_level,
        }

    # ── Nutrition score for a meal ─────────────────────────────────────────────

    @staticmethod
    def score_meal(meal: dict, target_calories: int, goal: str) -> dict:
        """
        Compute a 1–10 health score for a single meal dict.

        Scoring factors:
          - Calorie balance  (40%): how close meal calories are to expected slot cal
          - Protein quality  (25%): protein-to-calorie ratio vs goal
          - Fibre content    (20%): fibre grams (aim ≥ 5g/meal)
          - Fat proportion   (15%): healthy fat range check

        Returns:
            { score: int(1-10), grade: str, breakdown: dict, tip: str }
        """
        cal   = meal.get("calories", 0)
        pro   = meal.get("protein",  0)
        fiber = meal.get("fiber",    0)
        fat   = meal.get("fat",      0)
        slot  = meal.get("label", "meal").lower()

        # Expected calories for this slot
        slot_fractions = {"breakfast": 0.25, "lunch": 0.35, "dinner": 0.30, "snack": 0.10}
        frac    = slot_fractions.get(slot, 0.25)
        expected_cal = target_calories * frac

        # ── Calorie balance score (0–4) ────────────────────────────────────────
        diff_pct = abs(cal - expected_cal) / max(expected_cal, 1)
        cal_score = max(0, 4 - int(diff_pct * 10))

        # ── Protein score (0–2.5) ───────────────────────────────────────────────
        protein_pct = (pro * 4) / max(cal, 1)
        target_prot_pct = {"Lose Weight": 0.35, "Maintain Weight": 0.30, "Gain Muscle": 0.30}.get(goal, 0.30)
        pro_score = min(2.5, (protein_pct / max(target_prot_pct, 0.01)) * 2.5)

        # ── Fibre score (0–2) ──────────────────────────────────────────────────
        fiber_score = min(2.0, fiber / 5 * 2)

        # ── Fat balance score (0–1.5) ──────────────────────────────────────────
        fat_pct = (fat * 9) / max(cal, 1)
        fat_score = 1.5 if 0.15 <= fat_pct <= 0.35 else 0.5

        raw        = cal_score + pro_score + fiber_score + fat_score  # 0–10
        final      = max(1, min(10, round(raw)))

        grades = {10: "A+", 9: "A", 8: "B+", 7: "B", 6: "C+", 5: "C", 4: "D", 3: "D-"}
        grade  = grades.get(final, "F")

        tips = {
            range(1, 4): "Very poor balance — consider a whole different meal.",
            range(4, 6): "Below average — add more protein and vegetables.",
            range(6, 8): "Decent meal — small tweaks can push it higher.",
            range(8, 11): "Excellent choice for your goal! 🎉",
        }
        tip = next((v for k, v in tips.items() if final in k), "Keep it balanced.")

        return {
            "score": final,
            "grade": grade,
            "breakdown": {
                "calorie_balance": round(cal_score, 1),
                "protein_quality": round(pro_score, 1),
                "fibre_content":   round(fiber_score, 1),
                "fat_balance":     round(fat_score, 1),
            },
            "tip": tip,
        }

    # ── Private calculation helpers ───────────────────────────────────────────

    @staticmethod
    def _bmi(w: float, h: float) -> float:
        return round(w / (h / 100) ** 2, 1)

    @staticmethod
    def _bmi_category(bmi: float) -> dict:
        for threshold, cat, color, emoji, advice in BMI_CATEGORIES:
            if bmi < threshold:
                return {"category": cat, "color": color, "emoji": emoji, "advice": advice}
        return {"category": "Obese", "color": "#EF4444", "emoji": "🔴", "advice": "Consult a doctor."}

    @staticmethod
    def _bmr(w: float, h: float, age: int, gender: str) -> float:
        base = (10 * w) + (6.25 * h) - (5 * age)
        return round(base + 5 if gender == "Male" else base - 161, 1)

    @staticmethod
    def _tdee(bmr: float, activity: str) -> float:
        return round(bmr * ACTIVITY_MULTIPLIERS.get(activity, 1.2), 1)

    @staticmethod
    def _target_calories(tdee: float, goal: str) -> int:
        return int(max(tdee + GOAL_ADJUSTMENTS.get(goal, 0), 1200))

    @staticmethod
    def _macros(cals: int, goal: str) -> dict:
        r = MACRO_RATIOS.get(goal, MACRO_RATIOS["Maintain Weight"])
        return {
            "protein": int((cals * r["protein"]) / 4),
            "carbs":   int((cals * r["carbs"])   / 4),
            "fat":     int((cals * r["fat"])     / 9),
        }

    @staticmethod
    def _water(w: float, activity: str) -> float:
        ml = w * 35
        if "Active" in activity or "athlete" in activity.lower():
            ml += 500
        return round(ml / 1000, 1)
