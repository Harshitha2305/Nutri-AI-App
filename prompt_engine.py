# =============================================================================
# prompt_engine.py — NutriAI v4
# Prompt Engine: formats user data into structured prompts for every AI agent.
#
# Each method returns a ready-to-send string (system prompt or user message).
# The AgentOrchestrator calls these before dispatching to agents.
#
# Design principle: prompts are data-driven templates, not hardcoded strings.
# Changing a prompt here instantly affects the agent without touching agent code.
# =============================================================================

from datetime import datetime


class PromptEngine:
    """
    Central prompt factory.  All prompt assembly lives here so agent files
    stay clean and testable without prompt-logic noise.
    """

    # ── Shared profile context block ──────────────────────────────────────────

    @staticmethod
    def _profile_block(profile: dict) -> str:
        """Reusable XML-style profile section inserted into multiple prompts."""
        allergies = profile.get("allergies") or "None"
        if isinstance(allergies, list):
            allergies = ", ".join(allergies) if allergies else "None"
        return f"""
<user_profile>
  Name:            {profile.get('name', 'User')}
  Age:             {profile.get('age', '?')} years
  Gender:          {profile.get('gender', '?')}
  Weight:          {profile.get('weight_kg', '?')} kg
  Height:          {profile.get('height_cm', '?')} cm
  Activity Level:  {profile.get('activity_level', '?')}
  Goal:            {profile.get('goal', profile.get('fitness_goal', '?'))}
  Diet Preference: {profile.get('diet_preference', '?')}
  Allergies:       {allergies}
  BMI:             {profile.get('bmi', '?')} — {profile.get('bmi_category', '?')}
  Daily Calories:  {profile.get('target_calories', '?')} kcal
  Protein Target:  {profile.get('protein_g', '?')} g/day
  Carbs Target:    {profile.get('carbs_g', '?')} g/day
  Fat Target:      {profile.get('fat_g', '?')} g/day
  Water Goal:      {profile.get('water_litres', '?')} L/day
</user_profile>"""

    # ── Nutrition Analysis Prompt ─────────────────────────────────────────────

    @staticmethod
    def nutrition_analysis(raw_data: dict) -> str:
        """
        Prompt sent to NutritionAgent when asking Claude to validate or explain
        a computed nutrition profile.

        raw_data keys: age, gender, weight_kg, height_cm, activity_level, goal
        """
        return f"""You are a certified nutritionist AI.
Analyse the following user data and provide a brief, accurate nutritional summary.

<input_data>
  Age:            {raw_data.get('age')} years
  Gender:         {raw_data.get('gender')}
  Weight:         {raw_data.get('weight_kg')} kg
  Height:         {raw_data.get('height_cm')} cm
  Activity Level: {raw_data.get('activity_level')}
  Goal:           {raw_data.get('goal')}
  Diet:           {raw_data.get('diet_preference', 'Not specified')}
</input_data>

Calculate and explain:
1. BMI and what it means for this person
2. Basal Metabolic Rate (BMR) using Mifflin-St Jeor
3. Total Daily Energy Expenditure (TDEE)
4. Recommended daily calories for their goal
5. Macro split (protein / carbs / fat in grams) suited for their goal

Be concise, warm, and evidence-based. Format in clear sections."""

    # ── Meal Planning Prompt ──────────────────────────────────────────────────

    @staticmethod
    def meal_planning(profile: dict, cuisine: str = "both",
                      day_name: str = "") -> str:
        """
        Prompt sent to MealPlanningAgent when generating an AI-narrated
        meal plan explanation or custom suggestions.
        """
        day_ctx = f"for {day_name}" if day_name else "for today"
        return f"""You are a professional meal planner and nutritionist.
Create a personalised meal plan {day_ctx} for the following user.
{PromptEngine._profile_block(profile)}

<requirements>
  Cuisine preference: {cuisine}
  Calorie target:     {profile.get('target_calories', 2000)} kcal
  Meals:              Breakfast, Lunch, Dinner, Snack
  Each meal should include: food name, approximate calories, macros (P/C/F), brief note
</requirements>

Rules:
- Respect the diet preference and allergies strictly
- Distribute calories as: Breakfast 25%, Lunch 35%, Dinner 30%, Snack 10%
- Vary food types for nutritional diversity
- For Indian diet preference, prioritise authentic Indian dishes
- Keep suggestions practical and easy to prepare
- Format: structured table or bullet list, not prose paragraphs"""

    # ── Health Insights Prompt ────────────────────────────────────────────────

    @staticmethod
    def health_insights(profile: dict, focus: str = "general") -> str:
        """
        Prompt for HealthInsightsAgent when generating AI-enriched recommendations.
        focus: 'general' | 'weight_loss' | 'muscle_gain' | 'maintenance'
        """
        return f"""You are a preventive health coach and registered dietitian.
Provide personalised, evidence-based health insights for this user.
{PromptEngine._profile_block(profile)}

<focus_area>{focus}</focus_area>

Generate insights in these sections:
1. **BMI & Weight Assessment** — what their numbers mean, realistic targets
2. **Top 3 Nutrition Priorities** — specific, actionable, ranked by impact
3. **Foods to Embrace** — 5 specific foods ideal for their goal + why
4. **Foods to Reduce** — 3–4 foods to limit with scientific reasoning
5. **Lifestyle Recommendations** — sleep, hydration, exercise tips aligned with goal
6. **Weekly Progress Expectation** — realistic projection (be honest, not over-promising)

Tone: warm, motivating, evidence-based. Avoid medical diagnoses.
Format: use headers and bullet points for scan-ability."""

    # ── Food Image Analysis Prompt ────────────────────────────────────────────

    @staticmethod
    def food_image_analysis(profile: dict = None) -> str:
        """
        Prompt for FoodImageAgent — injected alongside the base64 image.
        """
        goal = profile.get("goal", "general health") if profile else "general health"
        diet = profile.get("diet_preference", "") if profile else ""
        return f"""You are an expert nutritionist with a speciality in visual food analysis.
Analyse this food image carefully and provide a complete nutritional breakdown.

Output in this EXACT format:

## 🍽️ Food Items Detected
List each visible food item with estimated portion size (e.g., "1 medium bowl (~200g)").

## 🔥 Calorie Breakdown
| Food Item | Portion | Calories |
|-----------|---------|----------|
(complete table for every item)
**Total Estimated Calories: X kcal**

## 📊 Macronutrient Estimate (whole meal)
- Protein: ~Xg
- Carbohydrates: ~Xg
- Fat: ~Xg
- Fibre: ~Xg

## ⭐ Health Score: X/10
Brief justification (1–2 sentences).

## 💡 Improvement Suggestions
2–3 specific, practical ways to make this meal healthier.

## ⚠️ Notes for This User
Goal: {goal}{'. Diet: '+diet if diet else ''}
Tailor 1–2 sentences to their specific context.

Important: State clearly these are visual estimates. Actual values vary with preparation method."""

    # ── Chat System Prompt ────────────────────────────────────────────────────

    @staticmethod
    def chat_system(profile: dict = None, meal_summary: str = "") -> str:
        """
        Full system prompt for ChatAssistantAgent.  Called once per conversation.
        """
        today = datetime.now().strftime("%A, %d %B %Y")
        prompt = f"""You are NutriAI, a world-class AI nutrition coach combining the expertise of a registered dietitian, sports nutritionist, and wellness coach.

Today's date: {today}

Personality:
- Warm, encouraging, and evidence-based
- Concise answers (under 250 words unless a detailed plan is requested)
- Use bullet points and emoji sparingly for readability
- Always recommend consulting a doctor for medical conditions
- Never diagnose — recommend, suggest, educate

When the user asks for meal suggestions, always respect their diet preference and allergies.
When the user asks for calorie counts, give realistic ranges.
When the user shares struggles, acknowledge them before advising."""

        if profile:
            prompt += "\n" + PromptEngine._profile_block(profile)

        if meal_summary:
            prompt += f"\n\n<todays_meals>\n{meal_summary}\n</todays_meals>"

        return prompt

    # ── Grocery List Narration Prompt ─────────────────────────────────────────

    @staticmethod
    def grocery_narration(grocery_dict: dict, profile: dict) -> str:
        """
        Prompt to generate a short AI-written intro for the grocery list.
        """
        categories = list(grocery_dict.keys())
        total      = sum(len(v) for v in grocery_dict.values())
        return f"""You are a nutritionist reviewing a weekly shopping list.
Write a 3-sentence shopping list summary for this user.
{PromptEngine._profile_block(profile)}

The grocery list has {total} items across {len(categories)} categories: {', '.join(categories)}.

Mention:
1. Which categories are best for their goal
2. One buying tip (e.g., buy seasonal, frozen vegetables are fine)
3. One ingredient to add that isn't on the list but would help their goal

Keep it under 80 words. Be specific, not generic."""

    # ── Weekly Summary Prompt ─────────────────────────────────────────────────

    @staticmethod
    def weekly_summary(weekly_stats: dict, profile: dict) -> str:
        """
        Prompt to generate a concise weekly nutrition summary.
        weekly_stats: {day: {calories, protein, carbs, fat}, …}
        """
        days_summary = "\n".join(
            f"  {day}: {v.get('calories',0)} kcal, P:{v.get('protein',0)}g, "
            f"C:{v.get('carbs',0)}g, F:{v.get('fat',0)}g"
            for day, v in weekly_stats.items()
        )
        return f"""You are a nutritionist reviewing a 7-day meal plan.
{PromptEngine._profile_block(profile)}

Weekly Nutrition Log:
{days_summary}

Provide a 5-line weekly summary:
1. Average daily calories vs target ({profile.get('target_calories','?')} kcal)
2. Best nutritional day and why
3. Day that needs improvement and why
4. One pattern you notice (good or bad)
5. One actionable recommendation for next week"""
