# =============================================================================
# agents/food_image_agent.py
# AGENT 4 — Food Image Analysis Agent (Gemini Vision)
# =============================================================================

import base64
import io
import os

from PIL import Image
from google import genai

from .agent_base import BaseAgent


class FoodImageAgent(BaseAgent):

    def __init__(self):

        super().__init__(
            name="Food Image Analysis Agent",
            description="Identifies food in photos and estimates calories via Gemini Vision",
            emoji="📸",
        )

        print("ANALYSE IMAGE FUNCTION LOADED")

        # Create Gemini client
        self.client = genai.Client(
            api_key=os.getenv("GOOGLE_API_KEY")
        )

        # Use stable multimodal model
        self.model = "gemini-2.5-flash"


    def run(self, payload: dict) -> dict:
        image_b64 = payload.get("image_base64", "")
        profile   = payload.get("user_profile", {})

        if not image_b64:
            return {"success": False, "error": "No image provided.", "analysis": ""}

        try:

            # Build prompt
            if payload.get("custom_prompt"):
                prompt = payload["custom_prompt"]

            else:

                goal = profile.get("goal", "general health")
                diet = profile.get("diet_preference", "")

                prompt = (
                    "You are a professional nutritionist analysing a food image.\n\n"
                    "Identify all food items and estimate:\n"
                    "- Calories\n"
                    "- Protein\n"
                    "- Carbohydrates\n"
                    "- Fat\n"
                    "- Fibre\n\n"
                    "Also provide:\n"
                    "• Healthiness score (1-10)\n"
                    "• Suggestions to improve the meal\n\n"
                    f"User goal: {goal}. Diet preference: {diet}."
                )

            # Decode image
            image_bytes = base64.b64decode(image_b64)

            image = Image.open(io.BytesIO(image_bytes))
            
            # Gemini call
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[prompt, image]
            )
            print("Gemini text:", response.text)
            return {
                "success": True,
                "analysis": response.text,
                "error": ""
            }
        except Exception as e:

            print("VISION ERROR:", e)

            return {
                "success": False,
                "error": str(e),
                "analysis": ""
            }


# ── Image utility functions ────────────────────────────────────────────────────

SUPPORTED = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "webp": "image/webp"
}


def validate_image(uploaded_file) -> tuple:

    ext = uploaded_file.name.rsplit(".", 1)[-1].lower() if "." in uploaded_file.name else ""

    if ext not in SUPPORTED:
        return False, f"Unsupported format '.{ext}'. Use JPG, PNG or WEBP."

    if uploaded_file.size > 5 * 1024 * 1024:
        return False, f"File too large ({uploaded_file.size/(1024*1024):.1f} MB). Max 5 MB."

    return True, ""


def encode_image(uploaded_file) -> tuple:

    data = uploaded_file.read()
    uploaded_file.seek(0)

    b64 = base64.b64encode(data).decode("utf-8")

    mime = SUPPORTED.get(
        uploaded_file.name.rsplit(".", 1)[-1].lower(),
        "image/jpeg"
    )

    return b64, mime


def resize_for_display(uploaded_file, max_w: int = 400):

    uploaded_file.seek(0)

    img = Image.open(io.BytesIO(uploaded_file.read()))

    uploaded_file.seek(0)

    if img.width > max_w:
        ratio = max_w / img.width
        img = img.resize((max_w, int(img.height * ratio)))

    return img