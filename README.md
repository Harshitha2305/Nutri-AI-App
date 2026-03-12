# 🥗 NutriAI v4 — Multi-Agent Personalized Nutrition System

> **IIT Mandi Gen AI Hackathon** · Built with Claude AI (Anthropic) + Streamlit

---

## 🏗️ Project Structure

```
nutri_ai_v4/
│
├── app.py                        ← Main Streamlit app (11 tabs, auth-gated)
├── auth.py                       ← Registration, login, password hashing (PBKDF2)
├── database.py                   ← SQLite layer — users, profiles, history, chat
├── agent_orchestrator.py         ← Top-level controller (wires PromptEngine + agents + DB)
├── prompt_engine.py              ← All AI prompt templates in one place
│
├── agents/
│   ├── __init__.py
│   ├── agent_base.py             ← Abstract BaseAgent with timing/telemetry
│   ├── nutrition_agent.py        ← AGENT 1: BMI, BMR, TDEE, macros
│   ├── meal_planning_agent.py    ← AGENT 2: daily/weekly plans, swap, grocery
│   ├── health_insights_agent.py  ← AGENT 3: rule-based tips, alerts, projections
│   ├── food_image_agent.py       ← AGENT 4: Claude Vision calorie analysis
│   ├── chat_assistant_agent.py   ← AGENT 5: Claude multi-turn coaching
│   └── orchestrator.py           ← Inner agent coordinator (used by agent_orchestrator.py)
│
├── ui_styles.py                  ← All CSS (BioGreen design system)
├── ui_components.py              ← All Streamlit render functions
├── foods_dataset.csv             ← 66 foods (35 Indian + 31 International)
├── requirements.txt
├── .env.example                  ← Copy to .env and add your API key
└── README.md
```

---

## 🚀 Running Locally

### 1. Clone / download the project

```bash
cd nutri_ai_v4
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your Anthropic API key

```bash
cp .env.example .env
# Open .env and set:  ANTHROPIC_API_KEY=sk-ant-...
```

### 5. Run the app

```bash
streamlit run app.py
# Opens at http://localhost:8501
```

> **Note:** The SQLite database (`nutri_ai.db`) is auto-created on first launch.
> No migration scripts needed — schema is applied via `CREATE TABLE IF NOT EXISTS`.

---

## ☁️ Deploying to Streamlit Cloud

### 1. Push to GitHub

```bash
git init && git add . && git commit -m "NutriAI v4"
git remote add origin https://github.com/YOUR_USERNAME/nutri-ai-v4.git
git push -u origin main
```

### 2. Deploy on share.streamlit.io

1. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**
2. Connect your GitHub repo
3. Set **Main file path** to `app.py`
4. Click **Advanced settings → Secrets** and add:

```toml
ANTHROPIC_API_KEY = "sk-ant-..."
```

5. Click **Deploy**

> **SQLite on Streamlit Cloud:** The database file is written to the app's ephemeral filesystem. Data persists within a session but is reset on redeploy. For production persistence, swap `database.py` to use [Supabase](https://supabase.com) or [PlanetScale](https://planetscale.com).

---

## 🧠 Multi-Agent Architecture

### How it works

```
User Profile Form
       │
       ▼
 ┌─────────────────────────────────────┐
 │        NutriAIOrchestrator          │  ← agent_orchestrator.py
 │                                     │
 │  1. PromptEngine.nutrition_analysis()│  ← structures the prompt
 │  2. NutritionAgent.run()            │  ← BMI, BMR, TDEE, macros
 │  3. HealthInsightsAgent.run()       │  ← tips, alerts, projections
 │  4. Database.save_profile()         │  ← persists to SQLite
 └─────────────────────────────────────┘
       │
       ▼
 ┌─────────────────────────────────────┐
 │  MealPlanningAgent.run()            │  ← daily/weekly plans, scoring
 │  Database.save_meal_plan()          │  ← persists plan JSON
 └─────────────────────────────────────┘
       │
       ▼   (on-demand)
 ┌─────────────────────┐  ┌────────────────────────────┐
 │  FoodImageAgent     │  │  ChatAssistantAgent         │
 │  + Claude Vision    │  │  + PromptEngine.chat_system │
 │  (image upload tab) │  │  + DB.save_chat_message()   │
 └─────────────────────┘  └────────────────────────────┘
```

### Agent Responsibilities

| Agent | File | Purpose |
|-------|------|---------|
| 🔬 NutritionAgent | `agents/nutrition_agent.py` | BMI (WHO), BMR (Mifflin-St Jeor), TDEE, calorie target, macro split, meal scoring 1–10 |
| 🍽️ MealPlanningAgent | `agents/meal_planning_agent.py` | Daily plans, 7-day weekly plans, meal swap (3 alternatives), grocery list generation |
| 💡 HealthInsightsAgent | `agents/health_insights_agent.py` | Rule-based: BMI insight, macro tips, food recs, risk alerts, hydration schedule, weekly projection |
| 📸 FoodImageAgent | `agents/food_image_agent.py` | Claude Vision API: identify foods in photo, estimate calories/macros, health score |
| 💬 ChatAssistantAgent | `agents/chat_assistant_agent.py` | Multi-turn Claude chat with full user profile + meal plan injected as context |

### PromptEngine

`prompt_engine.py` is the **single source of truth** for all AI prompts.

```python
PromptEngine.nutrition_analysis(profile)   # structured nutritionist prompt
PromptEngine.meal_planning(profile)        # meal plan request with constraints
PromptEngine.health_insights(profile)      # personalised health coach prompt
PromptEngine.food_image_analysis(profile)  # vision analysis with user context
PromptEngine.chat_system(profile, meals)   # full system prompt for chat agent
PromptEngine.grocery_narration(list, p)    # shopping list AI summary
```

Separating prompts from agent code means:
- **One file to edit** when tuning AI behaviour
- **Easy A/B testing** — swap prompts without touching agent logic
- **Clear auditing** — all prompts visible in one place

---

## 🔐 Authentication & Security

| Feature | Implementation |
|---------|---------------|
| Password storage | PBKDF2-HMAC-SHA256 with random 16-byte salt (260,000 iterations) |
| Password comparison | `hmac.compare_digest()` (timing-safe) |
| Session management | Streamlit `session_state` only — no cookies |
| Email normalisation | Always `.lower().strip()` before storage and lookup |
| Cascade deletes | SQLite `ON DELETE CASCADE` — deleting a user removes all their data |

### SQLite Tables

```sql
users             -- id, name, email, password_hash, created_at, last_login
user_profiles     -- user_id, age, gender, height_cm, weight_kg,
                  -- activity_level, fitness_goal, diet_preference,
                  -- allergies, cuisine_pref, updated_at
meal_history      -- user_id, plan_date, plan_type, plan_json (JSON), calories
chat_sessions     -- user_id, role, content, created_at
```

---

## 🎨 UI — 11 Tabs

| Tab | Content |
|-----|---------|
| 📊 Dashboard | Health metrics cards, macro progress bars, today's meal snapshot |
| 🧠 AI Engine | Pipeline visualization, step-by-step flow, tech stack |
| 🍽️ Daily Plan | 4 meal cards with scores + swap feature |
| 📅 Weekly Plan | 7-day expandable planner |
| 🛒 Grocery | Auto-generated categorised shopping list + download |
| 💧 Hydration | Glass tracker with schedule |
| 🇮🇳 Indian Diet | 12 food showcase + Indian plan generator |
| 📸 Image Scan | Claude Vision food photo analysis |
| 💬 AI Chat | Multi-turn coaching with persistent history |
| 💡 Insights | Personalised health insights + risk alerts |
| ⚙️ Account | Edit profile, change password, meal history, delete account |

---

## 🌿 Login Flow

```
Landing Page (marketing + CTA)
       │
  ┌────┴────┐
  ▼         ▼
Login    Register
  │         │
  └────┬────┘
       ▼
 Authenticated App
  • Profile auto-loaded from SQLite
  • Chat history restored
  • All 11 tabs unlocked
```

---

## ⚠️ Disclaimer

NutriAI is for educational and demonstrative purposes only. It is not a substitute for advice from a registered dietitian or medical professional.
