# =============================================================================
# agent_orchestrator.py — NutriAI v4
# Top-level AgentOrchestrator (wraps the agents/ package orchestrator).
#
# This module is the single entry point for app.py.
# It wires together:
#   • PromptEngine     — formats all prompts before dispatch
#   • agents/          — all 5 specialised agent classes
#   • Database         — persists plans, chat, profile
#
# FULL WORKFLOW (annotated)
# ──────────────────────────────────────────────────────────────────────────
# 1. User submits profile form
#    → build_and_analyse_profile()
#      → PromptEngine.nutrition_analysis()   builds structured prompt
#      → NutritionAgent.run()               computes BMI/BMR/TDEE/macros
#      → HealthInsightsAgent.run()          builds rule-based insight pack
#      → DB.save_profile()                  persists to SQLite
#
# 2. User requests daily meal plan
#    → generate_daily_plan()
#      → MealPlanningAgent.run(mode="daily") → scored meal dict
#      → DB.save_meal_plan()                 persists plan JSON
#
# 3. User requests weekly plan
#    → generate_weekly_plan()
#      → MealPlanningAgent.run(mode="weekly") × 7 days
#      → generate_grocery_list()
#
# 4. User requests meal swap
#    → swap_meal()
#      → MealPlanningAgent.run(mode="swap") → 3 alternatives
#
# 5. User uploads food photo
#    → analyse_image()
#      → PromptEngine.food_image_analysis()  builds vision prompt
#      → FoodImageAgent.run()               calls Claude Vision API
#
# 6. User sends chat message
#    → chat()
#      → PromptEngine.chat_system()          builds system context
#      → ChatAssistantAgent.run()           calls Claude API
#      → DB.save_chat_message()             persists both turns
#
# 7. User views pipeline tab
#    → agent_status()                       returns telemetry for each agent
# =============================================================================

from agents.nutrition_agent       import NutritionAgent
from agents.meal_planning_agent   import MealPlanningAgent
from agents.health_insights_agent import HealthInsightsAgent
from agents.food_image_agent      import (FoodImageAgent,
                                          validate_image, encode_image,
                                          resize_for_display)
from agents.chat_assistant_agent  import ChatAssistantAgent
from prompt_engine                import PromptEngine
from database                     import Database


class NutriAIOrchestrator:
    """
    Top-level controller for NutriAI v4.
    Replaces the inner agents.orchestrator.AgentOrchestrator as the
    primary interface for app.py.
    """

    def __init__(self):
        # ── Agents ────────────────────────────────────────────────────────────
        self.nutrition_agent  = NutritionAgent()
        self.meal_agent       = MealPlanningAgent()
        self.insights_agent   = HealthInsightsAgent()
        self.image_agent      = FoodImageAgent()
        self.chat_agent       = ChatAssistantAgent()

        # ── Support modules ───────────────────────────────────────────────────
        self.prompt_engine = PromptEngine()
        self.db            = Database()

        # ── Image helpers ─────────────────────────────────────────────────────
        self.validate_image     = validate_image
        self.encode_image       = encode_image
        self.resize_for_display = resize_for_display

    # ══════════════════════════════════════════════════════════════════════════
    # STEP 1 — Profile Analysis
    # ══════════════════════════════════════════════════════════════════════════

    def build_and_analyse_profile(self, form_data: dict,
                                  user_id: int = None) -> dict:
        """
        Run NutritionAgent + HealthInsightsAgent.
        Optionally persist profile to DB if user_id supplied.

        Returns merged profile dict with nested 'insights' key.
        """
        # Agent 1 — core metrics
        nutrition_result = self.nutrition_agent._timed_run(form_data)
        nutrition = nutrition_result.get("result", {})
        # Ensure required nutrition fields exist
        nutrition.setdefault("target_calories", nutrition.get("tdee", 2000))
        nutrition.setdefault("protein_g", 100)
        nutrition.setdefault("carbs_g", 250)
        nutrition.setdefault("fat_g", 70)
        nutrition.setdefault("water_litres", 2)
        nutrition.setdefault("bmi_emoji", "⚖️")
        nutrition.setdefault("bmi_category", "Unknown")

        # Agent 3 — insights
        insights_result  = self.insights_agent._timed_run(nutrition)
        insights = insights_result.get("result", {})

        profile = {**nutrition, "insights": insights}

# Ensure profile keeps original form inputs
        profile["weight_kg"] = form_data.get("weight_kg")
        profile["height_cm"] = form_data.get("height_cm")
        profile["age"] = form_data.get("age")
        profile["gender"] = form_data.get("gender")
        profile["activity_level"] = form_data.get("activity_level")
        profile["diet_preference"] = form_data.get("diet_preference", "Vegetarian")
        profile["allergies"]       = form_data.get("allergies", [])
        profile["goal"]            = form_data.get("goal", "Maintain Weight")

        # Persist to DB if logged in
        if user_id:
            self.db.save_profile(user_id, {
                "age":            form_data.get("age"),
                "gender":         form_data.get("gender"),
                "height_cm":      form_data.get("height_cm"),
                "weight_kg":      form_data.get("weight_kg"),
                "activity_level": form_data.get("activity_level"),
                "fitness_goal":   form_data.get("goal"),
                "diet_preference":form_data.get("diet_preference"),
                "allergies":      form_data.get("allergies", []),
                "cuisine_pref":   form_data.get("cuisine", "both"),
            })

        return profile

    # backward-compat alias used by old app.py code
    def analyse_profile(self, form_data: dict) -> dict:
        return self.build_and_analyse_profile(form_data)

    # ══════════════════════════════════════════════════════════════════════════
    # STEP 2 — Daily Meal Plan
    # ══════════════════════════════════════════════════════════════════════════

    def generate_daily_plan(self, profile: dict, cuisine: str = "both",
                        user_id: int = None) -> dict:
     """
     Run MealPlanningAgent in daily mode.
     Optionally persist plan to DB.
     """
     payload = {**profile, "mode": "daily", "cuisine": cuisine}
     plan = self.meal_agent._timed_run(payload)

     # Extract real plan
     plan = plan.get("result", plan)

     # Ensure meals exist
     if "meals" not in plan:
        plan["meals"] = {}

     default_meal = {
        "icon": "🍽️",
        "label": "Meal",
        "food_name": "Food Item",
        "calories": 0,
        "protein": 0,
        "carbs": 0,
        "fat": 0,
        "score": 5
     }

     for slot in ["breakfast", "lunch", "dinner", "snack"]:
        meal = plan["meals"].get(slot, {})
        for k, v in default_meal.items():
            meal.setdefault(k, v)
        plan["meals"][slot] = meal

     if user_id:
        self.db.save_meal_plan(user_id, plan, plan_type="daily")

     return plan

    # ══════════════════════════════════════════════════════════════════════════
    # STEP 3 — Weekly Meal Plan
    # ══════════════════════════════════════════════════════════════════════════

    def generate_weekly_plan(self, profile: dict, cuisine: str = "both",
                             user_id: int = None) -> dict:
        """
        Run MealPlanningAgent in weekly mode.
        Returns {Monday: daily_plan, …, Sunday: daily_plan}.
        """
        payload = {**profile, "mode": "weekly", "cuisine": cuisine}
        result = self.meal_agent._timed_run(payload)
        weekly = result.get("result", {}).get("weekly", {})
        # ensure valid weekly structure
        if not isinstance(weekly, dict) or not weekly:
            weekly = {}

        if user_id:
            self.db.save_meal_plan(user_id, result, plan_type="weekly")

        return weekly

    # ══════════════════════════════════════════════════════════════════════════
    # STEP 4 — Meal Swap
    # ══════════════════════════════════════════════════════════════════════════

    def swap_meal(self, profile: dict, slot: str,
                  exclude_name: str = "", cuisine: str = "both") -> list:
        payload = {
            **profile,
            "mode":         "swap",
            "cuisine":      cuisine,
            "swap_slot":    slot,
            "swap_exclude": exclude_name,
        }
        result = self.meal_agent._timed_run(payload)

        if not result:
         return []

        # handle different structures
        if "alternatives" in result:
         return result["alternatives"]

        if "result" in result and isinstance(result["result"], dict):
         return result["result"].get("alternatives", [])

        return []

    # ══════════════════════════════════════════════════════════════════════════
    # Grocery List
    # ══════════════════════════════════════════════════════════════════════════

    def generate_grocery_list(self, weekly_plan: dict) -> dict:
        return self.meal_agent.generate_grocery_list(weekly_plan)

    # ══════════════════════════════════════════════════════════════════════════
    # STEP 5 — Food Image Analysis
    # ══════════════════════════════════════════════════════════════════════════

    def analyse_image(self, image_b64: str, mime : str,
                      user_profile: dict = None) -> dict:
        """
        Build vision prompt via PromptEngine, then dispatch to FoodImageAgent.
        """
        prompt  = self.prompt_engine.food_image_analysis(user_profile)
        payload = {
            "image_base64": image_b64,
            "media_type":   mime,
            "user_profile": user_profile or {},
            "custom_prompt": prompt,
        }
        print("analyse_image called with:", mime)
        return self.image_agent._timed_run(payload)

    # ══════════════════════════════════════════════════════════════════════════
    # STEP 6 — Chat
    # ══════════════════════════════════════════════════════════════════════════

    def chat(self, messages: list, user_profile: dict = None,
             meal_summary: str = "", user_id: int = None) -> dict:
        """
        Build system prompt via PromptEngine → ChatAssistantAgent.
        Optionally persist both turns to DB.
        """
        system = self.prompt_engine.chat_system(user_profile, meal_summary)
        payload = {
            "messages":     messages,
            "user_profile": user_profile or {},
            "meal_summary": meal_summary,
            "system_override": system,
        }
        result = self.chat_agent._timed_run(payload)

        # Persist last user + assistant turn
        if user_id and result.get("success") and messages:
            last_user = next(
                (m["content"] for m in reversed(messages) if m["role"] == "user"),
                None
            )
            if last_user:
                self.db.save_chat_message(user_id, "user",      last_user)
                self.db.save_chat_message(user_id, "assistant", result["reply"])

        return result

    # ══════════════════════════════════════════════════════════════════════════
    # STEP 7 — Agent Status (pipeline tab)
    # ══════════════════════════════════════════════════════════════════════════

    def agent_status(self) -> list[str]:
        return [
            self.nutrition_agent.status_line(),
            self.meal_agent.status_line(),
            self.insights_agent.status_line(),
            self.image_agent.status_line(),
            self.chat_agent.status_line(),
        ]

    # ══════════════════════════════════════════════════════════════════════════
    # DB passthrough helpers (used by app.py)
    # ══════════════════════════════════════════════════════════════════════════

    def get_user_profile(self, user_id: int) -> dict | None:
        return self.db.get_profile(user_id)

    def profile_complete(self, user_id: int) -> bool:
        return self.db.profile_complete(user_id)

    def get_recent_plans(self, user_id: int, limit: int = 7) -> list:
        return self.db.get_recent_plans(user_id, limit)

    def get_chat_history(self, user_id: int) -> list[dict]:
        return self.db.get_chat_history(user_id)

    def clear_chat_history(self, user_id: int):
        self.db.clear_chat_history(user_id)

    def user_stats(self, user_id: int) -> dict:
        return self.db.user_stats(user_id)
