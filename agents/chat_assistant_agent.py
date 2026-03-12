# =============================================================================

# agents/chat_assistant_agent.py

# AGENT 5 — Nutrition Chat Assistant Agent (Gemini Version)

# Responsibilities:

# • Maintain multi-turn conversation with full user context

# • Generate contextual responses using Gemini API

# • Provide suggested questions for the UI

# • Fall back gracefully if the API key is unavailable

# =============================================================================

import os
import google.generativeai as genai
from .agent_base import BaseAgent

QUICK_SUGGESTIONS = [
"💪 What should I eat after a gym workout?",
"🥗 Suggest a high-protein vegetarian breakfast",
"🏃 How can I reduce belly fat through diet?",
"🇮🇳 What Indian foods are best for weight loss?",
"💧 How much water should I drink daily?",
"🌙 Healthy late-night snack options?",
"🌾 Explain good carbs vs bad carbs",
"📉 How do I break a weight loss plateau?",
]

class ChatAssistantAgent(BaseAgent):
 """
 Agent 5 — Nutrition Chat Assistant Agent.

 Input payload keys:
     messages     (list)  — [{"role": "user"/"assistant", "content": str}, …]
     user_profile (dict)  — nutrition profile from NutritionAgent
     meal_summary (str)   — from MealPlanningAgent.get_plan_summary()

 Output dict keys:
     reply   (str)   — assistant's response
     success (bool)
     error   (str)
 """

 def __init__(self):
    super().__init__(
        name="Nutrition Chat Assistant Agent",
        description="Conversational AI coach powered by Gemini",
        emoji="💬",
    )

    print("CHAT ASSISTANT AGENT LOADED")

    # Configure Gemini API
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("⚠ GOOGLE_API_KEY not found in environment variables")

    genai.configure(api_key=api_key)

    # Load Gemini model
    self.model = genai.GenerativeModel("gemini-2.5-flash")


 def run(self, payload: dict) -> dict:

    messages     = payload.get("messages", [])
    user_profile = payload.get("user_profile", {})
    meal_summary = payload.get("meal_summary", "")

    if not messages:
        return {"success": False, "reply": "", "error": "No messages provided."}

    try:

        # Use PromptEngine-built system if provided
        system = payload.get("system_override") or \
                 self._build_system_prompt(user_profile, meal_summary)

        # Convert message history into a single prompt
        conversation = ""
        for m in messages:
            role = m.get("role", "user")
            content = m.get("content", "")
            conversation += f"{role.upper()}: {content}\n"

        prompt = f"""
        {system}
        Conversation so far:
        {conversation}
        Assistant:
        """

        response = self.model.generate_content(prompt)

        return {
            "success": True,
            "reply": response.text,
            "error": ""
        }

    except Exception as e:

        print("CHAT ERROR:", e)

        return {
            "success": False,
            "reply": "",
            "error": str(e)
        }


# ── System prompt ─────────────────────────────────────────────────────────

@staticmethod
def _build_system_prompt(profile: dict, meal_summary: str) -> str:

    prompt = (
        "You are NutriAI, a warm, knowledgeable AI nutrition coach. "
        "Your advice is evidence-based, practical, and encouraging. "
        "Keep responses concise (under 300 words) and use bullet points for lists. "
        "Always recommend consulting a registered dietitian for medical conditions. "
        "When asked for meal suggestions, consider the user's diet preference and allergies."
    )

    if profile:
        prompt += f"""
        User Profile:
        • BMI: {profile.get('bmi','N/A')} ({profile.get('bmi_category','N/A')})
        • Goal: {profile.get('goal','N/A')}
        • Diet: {profile.get('diet_preference','N/A')}
        • Daily Calories: {profile.get('target_calories','N/A')} kcal
        • Protein / Carbs / Fat: {profile.get('protein_g','?')}g / {profile.get('carbs_g','?')}g / {profile.get('fat_g','?')}g
        • Water Goal: {profile.get('water_litres','?')} L/day
        • Allergies: {profile.get('allergies','None')}"""

    if meal_summary:
        prompt += f"\n\nToday's meal plan context:\n{meal_summary}"

    return prompt


@staticmethod
def get_suggestions() -> list:
    return QUICK_SUGGESTIONS