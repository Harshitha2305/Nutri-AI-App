# =============================================================================
# agents/health_insights_agent.py
# AGENT 3 — Health Insights Agent
# =============================================================================

from .agent_base import BaseAgent


class HealthInsightsAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            name="Health Insights Agent",
            description="Generates personalised health tips, risk alerts & projections",
            emoji="💡",
        )

    # ─────────────────────────────────────────────────────────

    def run(self, payload: dict) -> dict:

        bmi        = payload.get("bmi", 22)
        bmi_cat    = payload.get("bmi_category", "Normal Weight")
        goal       = payload.get("goal", "Maintain Weight")
        diet       = payload.get("diet_preference", "Vegetarian")

        target_cal = payload.get("target_calories", 2000)

        protein_g  = payload.get("protein_g", 120)
        carbs_g    = payload.get("carbs_g", 250)
        fat_g      = payload.get("fat_g", 60)

        water_l    = payload.get("water_litres", 2.5)
        weight_kg  = payload.get("weight_kg", 70)

        activity   = payload.get(
            "activity_level",
            "Moderately Active (3-5 days/week)"
        )

        return {

            "bmi_insight":
                self._bmi_insight(bmi, bmi_cat, goal),

            "macro_insights":
                self._macro_insights(protein_g, carbs_g, fat_g, target_cal, goal),

            "goal_tips":
                self._goal_tips(goal, diet, bmi_cat),

            "food_recommendations":
                self._food_recommendations(goal, diet),

            "foods_to_limit":
                self._foods_to_limit(goal, bmi_cat),

            "risk_alerts":
                self._risk_alerts(bmi, goal, target_cal, activity),

            "hydration_plan":
                self._hydration_plan(water_l, weight_kg),

            "lifestyle_tips":
                self._lifestyle_tips(goal, activity),

            "weekly_projections":
                self._weekly_projections(goal, target_cal, weight_kg),
        }

    # ─────────────────────────────────────────────────────────
    # BMI INSIGHT
    # ─────────────────────────────────────────────────────────

    @staticmethod
    def _bmi_insight(bmi: float, category: str, goal: str) -> str:

        insights = {

            "Underweight":
                f"Your BMI of {bmi} is below the healthy range. "
                "Focus on calorie-dense nutritious foods like nuts, dairy, and legumes.",

            "Normal Weight":
                f"Your BMI of {bmi} is within the healthy range. "
                "Maintain balanced nutrition and consistent exercise.",

            "Overweight":
                f"Your BMI of {bmi} is slightly above optimal. "
                "A moderate calorie deficit and regular activity can improve health.",

            "Obese":
                f"Your BMI of {bmi} indicates obesity. "
                "Consult a healthcare professional and start gradual lifestyle changes."
        }

        return insights.get(category, f"Your BMI is {bmi}. Aim for the healthy 18.5–24.9 range.")

    # ─────────────────────────────────────────────────────────
    # MACRO INSIGHTS
    # ─────────────────────────────────────────────────────────

    @staticmethod
    def _macro_insights(protein, carbs, fat, calories, goal):

        tips = []

        calories = max(calories, 1)

        protein_pct = (protein * 4 / calories) * 100
        carbs_pct   = (carbs * 4 / calories) * 100
        fat_pct     = (fat * 9 / calories) * 100

        if goal == "Lose Weight":

            if protein_pct < 30:
                tips.append(
                    "⬆️ Increase protein to preserve muscle during weight loss."
                )

            if carbs_pct > 50:
                tips.append(
                    "⬇️ Reduce refined carbohydrates and prioritise fibre-rich carbs."
                )

        elif goal == "Gain Muscle":

            if protein_pct < 25:
                tips.append(
                    "⬆️ Increase protein intake to support muscle repair."
                )

            if carbs_pct < 40:
                tips.append(
                    "⬆️ Increase complex carbs for workout energy."
                )

        else:

            if fat_pct > 35:
                tips.append(
                    "⬇️ Reduce saturated fats and increase healthy fats."
                )

        tips.append(
            f"📊 Macro split — Protein {protein_pct:.0f}% | Carbs {carbs_pct:.0f}% | Fat {fat_pct:.0f}%"
        )

        return tips

    # ─────────────────────────────────────────────────────────
    # GOAL TIPS
    # ─────────────────────────────────────────────────────────

    @staticmethod
    def _goal_tips(goal, diet, bmi_cat):

        tips = {

            "Lose Weight": [
                "🥗 Fill half your plate with vegetables.",
                "🚫 Avoid sugary drinks.",
                "🍽️ Control portion sizes.",
                "💪 Strength training helps preserve muscle."
            ],

            "Gain Muscle": [
                "🏋️ Train with progressive overload.",
                "🥩 Eat protein after workouts.",
                "🍚 Increase calorie intake slightly.",
                "💤 Sleep 7–9 hours for recovery."
            ],

            "Maintain Weight": [
                "⚖️ Monitor weight weekly.",
                "🌈 Eat a variety of whole foods.",
                "🚶 Stay physically active daily."
            ],
        }

        base = tips.get(goal, [])

        if diet in ["Vegetarian", "Vegan"]:
            base.append("🫘 Combine grains and legumes for complete protein.")

        if diet == "Vegan":
            base.append("💊 Consider B12 and Omega-3 supplements.")

        return base

    # ─────────────────────────────────────────────────────────
    # FOOD RECOMMENDATIONS
    # ─────────────────────────────────────────────────────────

    @staticmethod
    def _food_recommendations(goal, diet):

        foods = [

            {"emoji": "🥦", "name": "Broccoli", "reason": "High fibre and micronutrients"},
            {"emoji": "🥗", "name": "Spinach", "reason": "Low calorie nutrient density"},
            {"emoji": "🫘", "name": "Lentils", "reason": "High protein and fibre"},
            {"emoji": "🌾", "name": "Oats", "reason": "Supports cholesterol health"},
            {"emoji": "🥑", "name": "Avocado", "reason": "Healthy fats and satiety"},
        ]

        if diet not in ["Vegetarian", "Vegan"]:
            foods.append(
                {"emoji": "🍗", "name": "Chicken Breast", "reason": "Lean protein"}
            )

        if diet in ["Vegetarian", "Vegan"]:
            foods.append(
                {"emoji": "🌱", "name": "Tofu", "reason": "Plant-based complete protein"}
            )

        return foods[:5]

    # ─────────────────────────────────────────────────────────
    # FOODS TO LIMIT
    # ─────────────────────────────────────────────────────────

    @staticmethod
    def _foods_to_limit(goal, bmi_cat):

        foods = [

            {"emoji": "🥤", "name": "Sugary Drinks", "reason": "High sugar, low nutrition"},
            {"emoji": "🍟", "name": "Fried Foods", "reason": "Excess saturated fat"},
            {"emoji": "🍬", "name": "Processed Snacks", "reason": "High sodium and additives"},
        ]

        if goal == "Lose Weight":
            foods.append(
                {"emoji": "🍞", "name": "White Bread", "reason": "High glycaemic index"}
            )

        return foods

    # ─────────────────────────────────────────────────────────
    # RISK ALERTS
    # ─────────────────────────────────────────────────────────

    @staticmethod
    def _risk_alerts(bmi, goal, calories, activity):

        alerts = []

        if bmi >= 30:
            alerts.append("🔴 BMI above 30 — consult a doctor before intense exercise.")

        if calories < 1400:
            alerts.append("⚠️ Very low calorie intake may cause nutrient deficiencies.")

        if "Sedentary" in activity and goal == "Gain Muscle":
            alerts.append("💪 Muscle gain requires resistance training.")

        if not alerts:
            alerts.append("✅ No major health risk flags detected.")

        return alerts

    # ─────────────────────────────────────────────────────────
    # HYDRATION PLAN
    # ─────────────────────────────────────────────────────────

    @staticmethod
    def _hydration_plan(water_l, weight):

        glasses = int(water_l * 4)

        schedule = [

            ("🌅 Morning", "300 ml after waking"),
            ("🍳 Before breakfast", "200 ml"),
            ("☀️ Mid-morning", "300 ml"),
            ("🍛 Before lunch", "200 ml"),
            ("🌤️ Afternoon", "300 ml"),
            ("🏃 Workout", "400 ml"),
            ("🌙 Evening", "200 ml"),
        ]

        return {

            "total_litres": water_l,
            "glasses": glasses,
            "schedule": schedule[:min(glasses, 7)],
            "tip": "Pale yellow urine indicates good hydration."
        }

    # ─────────────────────────────────────────────────────────
    # LIFESTYLE
    # ─────────────────────────────────────────────────────────

    @staticmethod
    def _lifestyle_tips(goal, activity):

        tips = [

            "😴 Sleep 7-9 hours nightly.",
            "🧘 Manage stress with meditation.",
            "🚶 Increase daily movement."
        ]

        if "Sedentary" in activity:
            tips.insert(
                0,
                "🏃 Add a 20-minute walk daily."
            )

        return tips

    # ─────────────────────────────────────────────────────────
    # PROJECTIONS
    # ─────────────────────────────────────────────────────────

    @staticmethod
    def _weekly_projections(goal: str, cals: int, weight: float) -> dict:
     """Estimates weight change per week based on calorie delta."""

     goal = str(goal).lower()

     # Weight loss projection
     if "lose" in goal:
        deficit = 500
        weekly_kg = round(deficit * 7 / 7700, 2)

        return {
            "direction": "loss",
            "weekly_kg": weekly_kg,
            "monthly_kg": round(weekly_kg * 4.3, 1),
            "note": f"At ~{deficit} kcal/day deficit you may lose about {weekly_kg} kg per week."
        }

    # Muscle gain projection
     elif "gain" in goal:
        surplus = 300
        weekly_kg = round(surplus * 7 / 7700, 2)

        return {
            "direction": "gain",
            "weekly_kg": weekly_kg,
            "monthly_kg": round(weekly_kg * 4.3, 1),
            "note": f"At ~{surplus} kcal/day surplus you may gain about {weekly_kg} kg per week."
        }

    # Maintenance
     else:
        return {
            "direction": "maintain",
            "weekly_kg": 0,
            "monthly_kg": 0,
            "note": "Maintenance calories — your weight should remain stable."
        }