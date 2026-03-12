# =============================================================================
# app.py — NutriAI v4  (Authentication + Persistent Profiles + PromptEngine)
# IIT Mandi Gen AI Hackathon  |  Run: streamlit run app.py
# =============================================================================
import os
import streamlit as st # type: ignore
from dotenv import load_dotenv # type: ignore
load_dotenv()

st.set_page_config(page_title="NutriAI — Multi-Agent Nutrition System",
                   page_icon="🥗", layout="wide", initial_sidebar_state="expanded")

from ui_styles import inject_css
inject_css()

from auth     import (AuthManager, init_auth_state, is_logged_in,
                      current_user, login_user, logout)
from database import Database
from agent_orchestrator import NutriAIOrchestrator
from agents.meal_planning_agent import MealPlanningAgent
from ui_components import (
    section_header, info_strip, empty_state, metric_card,
    macro_progress, meal_card, mini_meal_card,
    render_pipeline, render_grocery_category,
    render_hydration_ring, render_hydration_schedule,
    render_sidebar_stats, insight_card,
    render_landing_page, render_auth_logo,
    render_profile_setup_progress, render_user_topbar,
    render_meal_history,
)
if "swap_result" not in st.session_state:
    st.session_state.swap_result = None

if "swap_slot" not in st.session_state:
    st.session_state.swap_slot = None
# ── Init ──────────────────────────────────────────────────────────────────────
init_auth_state()
_AUTH = AuthManager()
_DB   = Database()

if "orch" not in st.session_state:
    st.session_state.orch = NutriAIOrchestrator()
orch: NutriAIOrchestrator = st.session_state.orch

for k,v in {"ready":False,"profile":None,"daily_plan":None,"weekly_plan":None,
             "grocery_list":None,"chat_messages":[],"cuisine":"both",
             "hydration_ml":0,"swap_result":None,"swap_slot":None}.items():
    if k not in st.session_state: st.session_state[k] = v

page = "landing" if not is_logged_in() else "app"

# ══════════════════════════════════════════════════════════════════
# LANDING PAGE
# ══════════════════════════════════════════════════════════════════
if page == "landing" and st.session_state.get("auth_page","landing") == "landing":
    render_landing_page()
    st.markdown("<br>", unsafe_allow_html=True)
    _,c,_ = st.columns([1,2,1])
    with c:
        a,b = st.columns(2)
        with a:
            if st.button("🔑 Sign In",use_container_width=True):
                st.session_state.auth_page = "login";    st.rerun()
        with b:
            if st.button("🌱 Create Account", use_container_width=True):
                st.session_state.auth_page = "register"; st.rerun()
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div style="text-align:center;color:var(--text-muted);font-size:0.76rem">🥗 NutriAI · AI-Powered Nutrition Guidance · Eat Better Every Day</div>', unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════════════════
# LOGIN PAGE
# ══════════════════════════════════════════════════════════════════
if not is_logged_in() and st.session_state.get("auth_page") == "login":
    _,card,_ = st.columns([1,1.6,1])
    with card:
        render_auth_logo()
        if st.session_state.get("auth_error"):
            st.error(st.session_state.auth_error); st.session_state.auth_error = ""
        if st.session_state.get("auth_success"):
            st.success(st.session_state.auth_success); st.session_state.auth_success = ""
        with st.form("login_form"):
            st.markdown("### 🔑 Welcome Back")
            email = st.text_input("Email",  placeholder="you@example.com")
            password = st.text_input("Password", type="password")
            sub = st.form_submit_button("Sign In →", use_container_width=True)
        if sub:
            ok, msg, user = _AUTH.login(email, password)
            if ok:
                login_user(user)
                st.session_state.chat_messages = orch.get_chat_history(user["id"])
                st.rerun()
            else:
                st.session_state.auth_error = msg; st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
        a,b = st.columns(2)
        with a:
            if st.button("← Home",           use_container_width=True):
                st.session_state.auth_page = "landing"; st.rerun()
        with b:
            if st.button("Create Account",   use_container_width=True):
                st.session_state.auth_page = "register"; st.rerun()
    st.stop()

# ══════════════════════════════════════════════════════════════════
# REGISTER PAGE
# ══════════════════════════════════════════════════════════════════
if not is_logged_in() and st.session_state.get("auth_page") == "register":
    _,card,_ = st.columns([1,1.6,1])
    with card:
        render_auth_logo()
        if st.session_state.get("auth_error"):
            st.error(st.session_state.auth_error); st.session_state.auth_error = ""
        with st.form("register_form"):
            st.markdown("### 🌱 Create Account")
            name = st.text_input("Full Name",  placeholder="Your name")
            email= st.text_input("Email",   placeholder="you@example.com")
            pw   = st.text_input("Password", type="password", placeholder="Min 8 chars, 1 letter + 1 digit")
            pw2  = st.text_input("Confirm Password", type="password")
            sub  = st.form_submit_button("Create Account →", use_container_width=True)
        if sub:
            ok, msg = _AUTH.register(name, email, pw, pw2)
            if ok:
                st.session_state.auth_success = "✅ Account created! Please sign in."
                st.session_state.auth_page    = "login"
                st.session_state.auth_error   = ""
                st.rerun()
            else:
                st.session_state.auth_error = msg; st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
        a,b = st.columns(2)
        with a:
            if st.button("← Home",        use_container_width=True):
                st.session_state.auth_page = "landing"; st.rerun()
        with b:
            if st.button("Sign In Instead",use_container_width=True):
                st.session_state.auth_page = "login"; st.rerun()
    st.stop()

# ══════════════════════════════════════════════════════════════════
# AUTHENTICATED APP
# ══════════════════════════════════════════════════════════════════
if not is_logged_in():
    st.session_state.auth_page = "landing"
    st.rerun()

user    = current_user()
user_id = user["id"]

# Load persisted profile once per session
if not st.session_state.get("_profile_loaded"):
    db_p = orch.get_user_profile(user_id)
    if db_p and orch.profile_complete(user_id):
        fd = {"age":db_p.get("age"),"gender":db_p.get("gender"),
              "height_cm":db_p.get("height_cm"),"weight_kg":db_p.get("weight_kg"),
              "activity_level":db_p.get("activity_level"),"goal":db_p.get("fitness_goal"),
              "diet_preference":db_p.get("diet_preference"),"allergies":db_p.get("allergies",[]),
              "cuisine":db_p.get("cuisine_pref","both")}
        with st.spinner("Loading saved profile…"):
            prof = orch.build_and_analyse_profile(fd)
            prof["diet_preference"] = db_p.get("diet_preference","Vegetarian")
            prof["allergies"]       = db_p.get("allergies",[])
            st.session_state.profile   = prof
            st.session_state.cuisine   = db_p.get("cuisine_pref","both")
            if not st.session_state.daily_plan:
                st.session_state.daily_plan = orch.generate_daily_plan(prof, cuisine=st.session_state.cuisine)
            st.session_state.ready = True
    if not st.session_state.chat_messages:
        st.session_state.chat_messages = orch.get_chat_history(user_id)
    st.session_state["_profile_loaded"] = True

p = st.session_state.get("profile")
ready = st.session_state.get("ready", False)
db_p  = orch.get_user_profile(user_id) or {}
def sanitize_profile(p):
    if not p:
        return {}

    defaults = {
        "bmi": 0,
        "bmi_category": "Unknown",
        "bmi_emoji": "⚖️",
        "bmr": 0,
        "tdee": 2000,
        "target_calories": 2000,
        "protein_g": 100,
        "carbs_g": 250,
        "fat_g": 70,
        "water_litres": 2,
        "weight_kg": 70,
        "diet_preference": "Vegetarian",
        "goal": "Maintain Weight",
        "insights": {}
    }

    for k,v in defaults.items():
        p.setdefault(k,v)

    return p


p = sanitize_profile(p)
# Ensure insights dictionary exists
ins = p.setdefault("insights", {})

# Prevent missing-key errors
ins.setdefault("macro_insights", [])
ins.setdefault("risk_alerts", [])
ins.setdefault("goal_tips", [])
ins.setdefault("lifestyle_tips", [])
ins.setdefault("food_recommendations", [])
ins.setdefault("foods_to_limit", [])
ins.setdefault("weekly_projections", {})
ins.setdefault("hydration_plan", {})

# ──────────────────── SIDEBAR ────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-logo"><div class="logo-icon">🥗</div><div class="logo-name">NutriAI</div><div class="logo-tag"> Multi-Agent System</div></div>', unsafe_allow_html=True)
    initials = "".join(w[0].upper() for w in user.get("name","U").split()[:2])
    st.markdown(f'<div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.8rem"><div class="user-avatar">{initials}</div><div><div style="font-size:0.88rem;font-weight:700;color:#E8F5EE">{user.get("name","")}</div><div style="font-size:0.68rem;color:#6EE7B7">{user.get("email","")}</div></div></div>', unsafe_allow_html=True)

    st.markdown('<div class="sb-section">👤 Profile</div>', unsafe_allow_html=True)
    def _idx(lst, val, default=0):
        try: return lst.index(val)
        except: return default

    age      = st.number_input("Age",         10,100, int(db_p.get("age") or 25), 1)
    gender   = st.selectbox("Gender", ["Male","Female"], index=_idx(["Male","Female"], db_p.get("gender","Male")))
    h_cm     = st.number_input("Height (cm)", 100.0,250.0, float(db_p.get("height_cm") or 170.0), 0.5)
    w_kg     = st.number_input("Weight (kg)", 30.0, 300.0, float(db_p.get("weight_kg") or 70.0),  0.5)
    ACT_OPTS = ["Sedentary (little/no exercise)","Lightly Active (1-3 days/week)",
                "Moderately Active (3-5 days/week)","Very Active (6-7 days/week)",
                "Extra Active (athlete/physical job)"]
    activity = st.selectbox("Activity Level", ACT_OPTS, index=_idx(ACT_OPTS, db_p.get("activity_level", ACT_OPTS[2])))
    GOAL_OPT = ["Lose Weight","Maintain Weight","Gain Muscle"]
    goal     = st.selectbox("Goal", GOAL_OPT, index=_idx(GOAL_OPT, db_p.get("fitness_goal","Maintain Weight")))
    DIET_OPT = ["Vegetarian","Vegan","Non-Vegetarian"]
    diet     = st.selectbox("Diet Preference", DIET_OPT, index=_idx(DIET_OPT, db_p.get("diet_preference","Vegetarian")))
    allergy_raw = st.text_input("Allergies", value=", ".join(db_p.get("allergies",[]) or []), placeholder="nuts, dairy…")
    allergies   = [a.strip() for a in allergy_raw.split(",") if a.strip()]

    st.markdown('<div class="sb-section">🍽️ Cuisine</div>', unsafe_allow_html=True)
    CUI_OPT = ["Both","Indian","International"]
    c_idx   = _idx(CUI_OPT, db_p.get("cuisine_pref","both").title())
    clab    = st.radio("Meal style", CUI_OPT, index=c_idx, horizontal=True, label_visibility="collapsed")
    st.session_state.cuisine = clab.lower()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀 Analyse & Save Profile", use_container_width=True):
        fd = {"age":age,"gender":gender,"weight_kg":w_kg,"height_cm":h_cm,
              "activity_level":activity,"goal":goal,"diet_preference":diet,
              "allergies":allergies,"cuisine":st.session_state.cuisine}
        with st.spinner("Running AI agents…"):
            prof = orch.build_and_analyse_profile(fd, user_id=user_id)
            prof["diet_preference"] = diet
            prof["allergies"]       = allergies
            st.session_state.profile   = prof
            st.session_state.daily_plan = orch.generate_daily_plan(prof, cuisine=st.session_state.cuisine, user_id=user_id)
            st.session_state.weekly_plan = st.session_state.grocery_list = None
            st.session_state.ready = True
        st.success("✅ Profile saved!"); st.rerun()

    if ready and p:
        st.markdown('<div class="sb-section">📊 Stats</div>', unsafe_allow_html=True)
        render_sidebar_stats(p)
        st.markdown('<div class="sb-section">🤖 Agents</div>', unsafe_allow_html=True)
        for line in orch.agent_status():
            st.markdown(f'<div style="font-size:0.67rem;color:#6EE7B7;padding:0.1rem 0">{line}</div>', unsafe_allow_html=True)

    st.markdown("---", unsafe_allow_html=True)
    if st.button("🚪 Log Out", use_container_width=True):
        logout(); st.rerun()

# ──────────────────── TOPBAR ─────────────────────────────────────
render_user_topbar(user, db_p if db_p else None, ready=ready)

# ──────────────────── TABS ───────────────────────────────────────
(tab_dash,tab_pipe,tab_daily,tab_weekly,tab_grocery,tab_hydro,
 tab_indian,tab_image,tab_chat,tab_ins,tab_acct) = st.tabs([
    "📊 Dashboard","🧠 AI Engine","🍽️ Daily Plan","📅 Weekly Plan",
    "🛒 Grocery","💧 Hydration","🇮🇳 Indian Diet",
    "📸 Image Scan","💬 AI Chat","💡 Insights","⚙️ Account"])

# ─── DASHBOARD ───────────────────────────────────────────────────
with tab_dash:
    uname = user.get("name","").split()[0]
    if not ready or not p:
        section_header(f"👋 Welcome back, {uname}!")
        info_strip("👈 <strong>Fill your profile in the sidebar</strong> and click <strong>Analyse & Save Profile</strong>.","blue")
        st.markdown("<br>", unsafe_allow_html=True)
        lc,rc = st.columns(2)
        with lc:
            section_header("🗺️ Getting Started")
            render_profile_setup_progress(1)
        with rc:
            st.markdown("<br>", unsafe_allow_html=True)
            for em,f in [("🔬","Calculate BMI, BMR & TDEE"),("🍽️","Generate daily meal plan"),
                         ("💡","Personalised health insights"),("📊","Track macros & hydration")]:
                st.markdown(f'<div class="strip-green">{em} {f}</div>', unsafe_allow_html=True)
    else:
        section_header(f"📊 {uname}'s Health Dashboard")
        bmi_c = {"Normal Weight":"green","Underweight":"blue","Overweight":"amber","Obese":"red"}.get(p.get("bmi_category",""),"green")
        bmi_t = {"Normal Weight":"ok","Underweight":"down","Overweight":"down","Obese":"down"}.get(p.get("bmi_category",""),"ok")
        c1,c2,c3=st.columns(3); c4,c5,c6=st.columns(3)
        with c1:
            # Debug profile first

            weight = p.get("weight_kg")
            height = p.get("height_cm")

            bmi_val = None

            try:
                if weight and height:
                  weight = float(weight)
                  height = float(height)
                  bmi_val = round(weight / ((height / 100) ** 2), 1)
            except:
                bmi_val = None

            # fallback to stored bmi
            if bmi_val is None:
                bmi_val = p.get("bmi")

            if bmi_val is None:
                bmi_val = "N/A"

            bmi_cat = p.get("bmi_category", "")
            bmi_emoji = p.get("bmi_emoji", "")
            metric_card(
              "⚖️",
              "Body Mass Index",
              bmi_val,
              "",
              sub=bmi_cat,
              trend=f"{bmi_emoji} {bmi_cat}",
              trend_kind=bmi_t,
              color=bmi_c
            )
        with c2:
           calories = p.get("target_calories", p.get("tdee", "N/A"))
           tdee = p.get("tdee", "N/A")
           goal = p.get("goal", "N/A")

           metric_card(
            "🔥",
            "Daily Calories",
            calories,
            "kcal",
            sub=f"TDEE {tdee} · Goal: {goal}"
        )
        with c3:
          bmr = p.get("bmr", "N/A")
          metric_card("⚙️","Basal Metabolic Rate", bmr if bmr=="N/A" else int(bmr), "kcal", sub="At complete rest", color="purple")

        with c4:
          protein = p.get("protein_g", p.get("protein", "N/A"))
          sub_text = f"{protein*4} kcal" if isinstance(protein,(int,float)) else ""
          metric_card("💪","Protein Target", protein, "g/day", sub=sub_text, color="purple")

        with c5:
          carbs = p.get("carbs_g", p.get("carbs", "N/A"))
          sub_text = f"{carbs*4} kcal" if isinstance(carbs,(int,float)) else ""
          metric_card("🌾","Carbohydrate Target", carbs, "g/day", sub=sub_text, color="blue")

        with c6:
          water = p.get("water_litres", p.get("water", "N/A"))
          sub_text = f"{int(water*4)} glasses" if isinstance(water,(int,float)) else ""
          metric_card("💧","Daily Water Goal", water, "L", sub=sub_text, color="teal")
        goal = p.get("goal", "N/A")
        diet = p.get("diet_preference", "N/A")
        calories = p.get("target_calories", p.get("tdee", "N/A"))

        st.markdown(
          f'<div class="strip-green" style="margin-bottom:1rem">'
          f'🎯 <strong>Goal:</strong> {p.get("goal","N/A")} &nbsp;·&nbsp; '
          f'🥗 <strong>Diet:</strong> {p.get("diet_preference","N/A")} &nbsp;·&nbsp; '
          f'🔥 {p.get("target_calories", p.get("tdee","N/A"))} kcal/day'
          f'</div>',
          unsafe_allow_html=True
        )
        section_header("🥩 Macronutrient Targets")
        ml,mr=st.columns([3,2])
        with ml:
            st.markdown(
              f'<div class="strip-green" style="margin-bottom:1rem">'
              f'🎯 <strong>Goal:</strong> {p.get("goal","N/A")} &nbsp;·&nbsp; '
              f'🥗 <strong>Diet:</strong> {p.get("diet_preference","N/A")} &nbsp;·&nbsp; '
              f'🔥 {p.get("target_calories", p.get("tdee","N/A"))} kcal/day'
              f'</div>',
              unsafe_allow_html=True
            )
            macro_progress("💪","Protein",      p.get("protein_g",0), p.get("protein_g",0),"protein")
            macro_progress("🌾","Carbohydrates",p.get("carbs_g",0),   p.get("carbs_g",0),  "carbs")
            macro_progress("🥑","Healthy Fats", p.get("fat_g",0),     p.get("fat_g",0),    "fat")
        with mr:
            fat = p.get("fat_g",0)
            metric_card("🥑","Fat Target", fat, "g/day", sub=f"{fat*9} kcal", color="amber")
            st.markdown("<br>", unsafe_allow_html=True)
            cals = p.get("target_calories", p.get("tdee", 1))
            tbl='<table style="width:100%;border-collapse:collapse;font-size:0.8rem"><tr style="border-bottom:1px solid var(--border)"><th style="text-align:left;padding:0.3rem 0.4rem;font-size:0.68rem;color:var(--text-muted)">Macro</th><th style="padding:0.3rem;font-size:0.68rem;color:var(--text-muted)">g</th><th style="padding:0.3rem;font-size:0.68rem;color:var(--text-muted)">kcal</th><th style="padding:0.3rem;font-size:0.68rem;color:var(--text-muted)">%</th></tr>'
            for lb,g,f in [
              ("💪 Protein", p.get("protein_g",0),4),
              ("🌾 Carbs", p.get("carbs_g",0),4),
              ("🥑 Fat", p.get("fat_g",0),9)
            ]:
                tbl+=f'<tr style="border-bottom:1px solid var(--border)"><td style="padding:0.3rem 0.4rem;font-weight:600">{lb}</td><td style="padding:0.3rem;text-align:center">{g}g</td><td style="padding:0.3rem;text-align:center">{g*f}</td><td style="padding:0.3rem;text-align:center">{round(g*f/cals*100)}%</td></tr>'
            tbl+='</table>'
            st.markdown(f'<div class="meal-wrap"><div class="meal-body">{tbl}</div></div>',unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        a1,a2=st.columns(2)
        with a1:
         bmi_emoji = p.get("bmi_emoji", "⚖️")
         bmi_advice = p.get("bmi_advice", "Maintain a balanced diet and regular exercise.")
         insight_card(f"{bmi_emoji} <strong>BMI:</strong> {bmi_advice}")
        with a2:
          projection_note = (
           p.get("insights", {})
            .get("weekly_projections", {})
            .get("note", "Follow your plan consistently to see progress.")
        )
        insight_card(f"📈 <strong>Projection:</strong> {projection_note}", "purple")
        if st.session_state.daily_plan:
            st.markdown("<br>", unsafe_allow_html=True)
            section_header("🍽️ Today at a Glance",subtitle="Daily Plan tab for full details")
            plan=st.session_state.daily_plan; snap=st.columns(4)
            for col,slot in zip(snap,["breakfast","lunch","dinner","snack"]):
                meals = plan.get("meals", {})
                m = meals.get(slot, {})
                sc_ = "#16A34A" if m.get("score",5) >= 8 else "#D97706" if m.get("score",5) >= 6 else "#DC2626"
                with col:
                    st.markdown(
                     f'<div class="meal-wrap"><div class="meal-header" style="padding:0.8rem 1rem">'
                     f'<div style="display:flex;align-items:center;gap:0.5rem">'
                     f'<span style="font-size:1.5rem">{m.get("icon","🍽️")}</span>'
                     f'<div>'
                     f'<div style="font-size:0.63rem;font-weight:800;text-transform:uppercase;color:var(--green-700)">{m.get("label","Meal")}</div>'
                     f'<div style="font-size:0.85rem;font-weight:600;color:var(--text-dark)">{m.get("food_name","Food Item")}</div>'
                     f'</div></div></div>'
                     f'<div class="meal-body" style="padding:0.6rem 1rem">'
                     f'<div style="font-size:0.74rem;color:var(--text-muted)">🔥 {m.get("calories","–")} cal · 💪 {m.get("protein","–")}g</div>'
                     f'<div style="font-size:0.7rem;color:{sc_};font-weight:700;margin-top:0.2rem">⭐ {m.get("score","–")}/10</div>'
                     f'</div></div>',
                     unsafe_allow_html=True
                    )
# ─── AI ENGINE ────────────────────────────────────────────────────
with tab_pipe:
    section_header("🧠 AI Decision Engine",subtitle="Multi-agent pipeline · PromptEngine · Live telemetry")
    render_pipeline(profile=p if ready else None, agent_status=orch.agent_status() if ready else None)
    st.markdown("<br>", unsafe_allow_html=True)
    section_header("📋 Step-by-Step Request Flow")
    steps=[
        ("1","👤 User Submits Profile","Age, weight, height, activity, goal, diet, allergies.","Input"),
        ("2","📝 PromptEngine","PromptEngine.nutrition_analysis() formats structured prompt with exact user metrics.","PromptEngine"),
        ("3","🔬 NutritionAgent","BMI · BMR · TDEE · Target Calories · Macros · Hydration.","Agent 1"),
        ("4","💡 HealthInsightsAgent","BMI insight · macro tips · food recs · risk alerts · weekly projection.","Agent 3"),
        ("5","📝 PromptEngine","PromptEngine.meal_planning() prepares meal planning prompt.","PromptEngine"),
        ("6","🍽️ MealPlanningAgent","CSV filter → meal scoring → daily plan dict.","Agent 2"),
        ("7","💾 Database","DB.save_profile() + DB.save_meal_plan() persist results to SQLite.","SQLite"),
        ("8","📊 Dashboard","All outputs merged in session_state and rendered across 11 tabs.","Output"),
        ("9","💬/📸 On-Demand","Chat → PromptEngine.chat_system() → ChatAgent. Image → PromptEngine.food_image_analysis() → ImageAgent.","On-demand"),
    ]
    for num,title,desc,tag in steps:
        tc={"Input":"#2563EB","Output":"#7C3AED","On-demand":"#D97706","PromptEngine":"#0891B2","SQLite":"#059669"}.get(tag,"#16A34A")
        st.markdown(f'<div style="display:flex;gap:1rem;background:var(--card);border:1px solid var(--border);border-radius:var(--radius-sm);padding:0.9rem 1.1rem;margin-bottom:0.5rem;box-shadow:var(--shadow-sm)"><div style="min-width:1.8rem;height:1.8rem;background:var(--green-900);color:#86EFAC;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:0.8rem;flex-shrink:0">{num}</div><div style="flex:1"><div style="font-weight:700;color:var(--text-dark);font-size:0.86rem;margin-bottom:0.15rem">{title} <span style="font-size:0.6rem;font-weight:800;background:{tc}22;color:{tc};padding:0.1rem 0.4rem;border-radius:20px;margin-left:0.4rem;border:1px solid {tc}44">{tag}</span></div><div style="font-size:0.78rem;color:var(--text-muted);line-height:1.5">{desc}</div></div></div>',unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    section_header("🛠️ Tech Stack")
    stack=[("🐍","Python 3.10+","Runtime"),("🖥️","Streamlit","UI"),("🤖","Gemini API","LLM+Vision"),("🐼","Pandas","Dataset"),("🔐","SQLite","Auth+DB"),("📝","PromptEngine","Prompt Factory")]
    tc2=st.columns(6)
    for i,(em,nm,rl) in enumerate(stack):
        with tc2[i]: st.markdown(f'<div class="agent-detail"><div class="ad-icon">{em}</div><div class="ad-name">{nm}</div><div class="ad-role">{rl}</div></div>',unsafe_allow_html=True)

# ─── DAILY PLAN ───────────────────────────────────────────────────
with tab_daily:

    if not ready or not p:
        empty_state("🍽️","No meal plan yet","Analyse your profile in the sidebar first.")

    else:

        hc, bc = st.columns([5,1])

        with hc:

            calories = p.get("target_calories", p.get("tdee", "N/A"))
            diet = p.get("diet_preference", "N/A")
            cuisine = st.session_state.cuisine.title()

            section_header(
                "🍽️ Today's Personalised Meal Plan",
                subtitle=f"Targeting {calories} kcal · {diet} · {cuisine}"
            )

        with bc:

            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("🔄 Regenerate", key="regen"):

                with st.spinner("Generating new meal plan…"):

                    st.session_state.daily_plan = orch.generate_daily_plan(
                        p,
                        cuisine=st.session_state.cuisine,
                        user_id=user_id
                    )

                    st.session_state.swap_result = None

                st.rerun()


        plan = st.session_state.daily_plan

        mc1, mc2 = st.columns(2)
        mc3, mc4 = st.columns(2)

        for col, slot in zip([mc1, mc2, mc3, mc4], ["breakfast","lunch","dinner","snack"]):

            with col:

                meal_card(st.session_state.daily_plan["meals"][slot])

                if st.button(
                    f"🔄 Swap {st.session_state.daily_plan['meals'][slot]['label']}",
                    key=f"swap_{slot}",
                ):

                    with st.spinner("Finding alternatives…"):
                        st.session_state.swap_slot = slot
                        st.write("MEAL DATA: ", st.session_state.daily_plan["meals"][slot])
                        meal = st.session_state.daily_plan["meals"][slot]
                        exclude_name= meal.get("food_name") or meal.get("name") or meal.get("title") or ""

                        st.session_state.swap_result = orch.swap_meal(
                            p,
                            slot=slot,
                            exclude_name= exclude_name,
                            cuisine=st.session_state.cuisine
                        )
                        print("UI RECEIVED SWAP:", st.session_state.swap_result)
                    st.rerun()


        # Swap Alternatives UI
        if "swap_result" in st.session_state and st.session_state.swap_result:

            st.markdown("<br>", unsafe_allow_html=True)

            section_header(
                f"🔄 Swap Alternatives for {(st.session_state.swap_slot or 'meal').title()}"
            )

            alts = st.session_state.get("swap_result", [])

            if alts and len(alts) > 0:
                cols = st.columns(len(alts))

                for i, (col , alt) in enumerate(zip(cols, alts)):

                    with col:

                        meal_card(alt)

                        if st.button("✅ Use This",key=f"use_alt_{i}"):
                            sl = st.session_state.swap_slot
                            meta = {
                                "breakfast":{"icon":"🌅","label":"Breakfast","time":"7:00–9:00 AM"},
                                "lunch":{"icon":"☀️","label":"Lunch","time":"12:30–2:00 PM"},
                                "dinner":{"icon":"🌙","label":"Dinner","time":"7:00–9:00 PM"},
                                "snack":{"icon":"🍎","label":"Snack","time":"4:00–5:00 PM"}
                            }.get(sl, {})

                            alt.update(meta)

                            # update meal
                            st.session_state.daily_plan["meals"][sl] = alt
                            st.session_state.swap_result = None

                            # recompute totals
                            meals = st.session_state.daily_plan["meals"]

                            st.session_state.daily_plan["daily_totals"] = {
                                "calories": sum(m["calories"] for m in meals.values()),
                                "protein": sum(m["protein"] for m in meals.values()),
                                "carbs": sum(m["carbs"] for m in meals.values()),
                                "fat": sum(m["fat"] for m in meals.values()),
                                "fiber": sum(m.get("fiber",0) for m in meals.values()),
                            }

                            st.session_state.swap_result = None

                            st.success("Meal swapped successfully!")

                            st.rerun()

            else:
                info_strip("No alternatives found.", "amber")


        # Daily Nutrition Summary
        st.markdown("<br>", unsafe_allow_html=True)
        section_header("📊 Daily Nutrition Summary")

        plan = st.session_state.daily_plan
        t = plan["daily_totals"]

        d1,d2,d3,d4,d5 = st.columns(5)

        target_cal = p.get("target_calories", p.get("tdee", 0))
        delta_val = t.get("calories",0) - target_cal if isinstance(target_cal,(int,float)) else 0

        d1.metric(
            "🔥 Calories",
            t.get("calories","N/A"),
            delta=f"{delta_val:+} vs target"
        )

        d2.metric(
            "💪 Protein",
            f"{t.get('protein',0)}g",
            delta=f"Target {p.get('protein_g',0)}g"
        )

        d3.metric(
            "🌾 Carbs",
            f"{t.get('carbs',0)}g",
            delta=f"Target {p.get('carbs_g',0)}g"
        )

        d4.metric(
            "🥑 Fat",
            f"{t.get('fat',0)}g",
            delta=f"Target {p.get('fat_g',0)}g"
        )

        d5.metric(
            "🌿 Fibre",
            f"{t.get('fiber',0)}g",
            delta="Goal: 25–30g"
        )


        # Calorie progress bar
        consumed = t.get("calories",0)
        target_cal = p.get("target_calories", p.get("tdee",2000))

        if isinstance(consumed,(int,float)) and isinstance(target_cal,(int,float)) and target_cal>0:

            progress = min(consumed/target_cal,1.0)

            st.markdown("<br>", unsafe_allow_html=True)

            st.progress(progress)

            st.caption(f"🔥 {consumed} / {target_cal} kcal consumed today")

# ─── WEEKLY PLAN ──────────────────────────────────────────────────
with tab_weekly:
    if not ready or not p: empty_state("📅","No weekly plan yet","Analyse your profile first.")
    else:
        section_header("📅 7-Day Meal Planner",subtitle="Each day generated independently for variety")
        if st.button("🗓️ Generate Weekly Plan",key="gen_weekly"):
            with st.spinner("Building 7-day plan…"):
                st.session_state.weekly_plan=orch.generate_weekly_plan(p,cuisine=st.session_state.cuisine,user_id=user_id)
                st.session_state.grocery_list=orch.generate_grocery_list(st.session_state.weekly_plan)
            st.success("✅ Weekly plan ready! Grocery List auto-generated 🛒")
        if st.session_state.weekly_plan:
            for day,dp in st.session_state.weekly_plan.items():
                if not isinstance(dp, dict):
                 continue
                dp.setdefault("daily_totals", {
                 "calories":0,
                 "protein":0,
                 "carbs":0,
                 "fat":0
                })
                t = dp.get("daily_totals", {"calories":0,"protein":0,"carbs":0,"fat":0})
                with st.expander(
                 f"📅 {day}  ·  {t.get('calories',0)} kcal  ·  "
                 f"P:{t.get('protein',0)}g  "
                 f"C:{t.get('carbs',0)}g  "
                 f"F:{t.get('fat',0)}g"
                ):
                    wc=st.columns(4)
                    for col,slot in zip(wc,["breakfast","lunch","dinner","snack"]):
                        with col:
                            meals = dp.get("meals", {})
                            if slot in meals:
                             mini_meal_card(meals[slot])
                            else:
                                st.info("No meal")
        else: info_strip("Click <strong>Generate Weekly Plan</strong> above.","blue")

# ─── GROCERY ──────────────────────────────────────────────────────
with tab_grocery:
    section_header("🛒 Smart Grocery List","Auto-generated from your 7-day meal plan")
    if not ready: empty_state("🛒","No grocery list","Generate your Weekly Plan first.")
    elif not st.session_state.grocery_list: info_strip("Go to <strong>Weekly Plan</strong> tab first.","amber")
    else:
        gl=st.session_state.grocery_list; total=sum(len(v) for v in gl.values())
        info_strip(f"🛒 <strong>{total} unique ingredients</strong> from your 7-day plan.","green")
        st.markdown("<br>",unsafe_allow_html=True)
        keys=list(gl.keys()); half=len(keys)//2+len(keys)%2
        gc1,gc2=st.columns(2)
        for col,ks in [(gc1,keys[:half]),(gc2,keys[half:])]:
            with col:
                for cat in ks: render_grocery_category(cat,gl[cat])
        st.markdown("<br>",unsafe_allow_html=True)
        txt="\n".join(f"\n{c}\n"+"".join(f"  □ {i}\n" for i in v) for c,v in gl.items())
        st.download_button("📥 Download (.txt)",data=txt,file_name="nutri_ai_grocery.txt",mime="text/plain")

# ─── HYDRATION ────────────────────────────────────────────────────
with tab_hydro:
    section_header("💧 Hydration Tracker","Glass-by-glass daily water tracking")
    if not ready or not p: empty_state("💧","Set up profile first","Water goal needs your body weight.")
    else:
        hydro = p.get("insights", {}).get("hydration_plan", {})
        goal_ml = int(hydro.get("total_litres", 2) * 1000)  # default 2L
        drunk = st.session_state.hydration_ml
        rc,sc=st.columns([1,2])
        with rc:
            render_hydration_ring(drunk,goal_ml); st.markdown("<br>",unsafe_allow_html=True)
            b1,b2=st.columns(2)
            with b1:
                if st.button("➕ +250ml",use_container_width=True,key="h250"): st.session_state.hydration_ml=min(drunk+250,goal_ml+1000); st.rerun()
                if st.button("➕ +500ml",use_container_width=True,key="h500"): st.session_state.hydration_ml=min(drunk+500,goal_ml+1000); st.rerun()
            with b2:
                if st.button("➕ +1L",use_container_width=True,key="h1l"): st.session_state.hydration_ml=min(drunk+1000,goal_ml+1000); st.rerun()
                if st.button("🔄 Reset",use_container_width=True,key="hreset"): st.session_state.hydration_ml=0; st.rerun()
            st.markdown("<br>",unsafe_allow_html=True)
            weight = p.get("weight_kg", "N/A")
            metric_card(
                "🔬",
                "Formula",
                f"{weight}kg × 35ml",
                "",
                sub=f"= {goal_ml} ml/day",
                color="teal"
            )
        with sc:
            section_header("📅 Drinking Schedule")
            render_hydration_schedule(hydro.get("schedule", []))
            st.markdown("<br>", unsafe_allow_html=True)
            tip = hydro.get("tip", "Stay hydrated throughout the day and drink water regularly.")
            insight_card(f"💡 {tip}", "teal")
        hm1,hm2,hm3,hm4=st.columns(4)
        hm1.metric("🎯 Goal",f"{goal_ml} ml"); hm2.metric("🥤 Consumed",f"{drunk} ml",f"{drunk//250} glasses")
        hm3.metric("📉 Remaining",f"{max(goal_ml-drunk,0)} ml"); hm4.metric("✅ Progress",f"{min(int(drunk/max(goal_ml,1)*100),100)}%")

# ─── INDIAN DIET ──────────────────────────────────────────────────
with tab_indian:
    section_header("🇮🇳 Indian Diet Recommendations",subtitle="Plant protein · fibre · bioactive spices")
    info_strip("🌿 Fermented foods (idli, dosa) + legumes (dal, rajma) + spices (turmeric, cumin) = unbeatable nutrition.","green")
    indian_foods=[("🍚","Idli","150/2pcs","4g","Fermented · gut-friendly"),("🥣","Poha","280","6g","Iron-rich · light"),
                  ("🫘","Dal","180/bowl","12g","Protein+fibre"),("🫓","Chapati","100/roti","3g","Complex carbs"),
                  ("🧀","Paneer","265/100g","18g","Casein protein"),("🍚","Brown Rice","215/cup","5g","Lower GI"),
                  ("🫘","Rajma","220/bowl","14g","Protein powerhouse"),("🌱","Sprouts","80/bowl","8g","Enzyme-rich"),
                  ("🟤","Makhana","160/bowl","5g","Low-cal snack"),("🥛","Curd","60/100g","3g","Probiotic"),
                  ("🟡","Moong Dal","347/100g","24g","Easy to digest"),("🥬","Palak","23/100g","3g","Iron+folate")]
    for i in range(0,len(indian_foods),4):
        cols=st.columns(4)
        for j,f in enumerate(indian_foods[i:i+4]):
            em,nm,cal,pro,note=f
            with cols[j]: st.markdown(f'<div class="food-showcase"><div class="fs-icon">{em}</div><div class="fs-name">{nm}</div><span class="fs-cal">🔥{cal}</span> <span class="fs-pro">💪{pro}</span><div class="fs-note">{note}</div></div>',unsafe_allow_html=True)
    st.markdown("<br>",unsafe_allow_html=True); section_header("🍛 Generate Indian Meal Plan")
    if not ready or not p: info_strip("Complete your profile first.","amber")
    else:
        if st.button("🍛 Generate Indian Day Plan"):
            with st.spinner("Curating…"):
                ip=orch.generate_daily_plan(p,cuisine="indian",user_id=user_id)
            ic1,ic2=st.columns(2); ic3,ic4=st.columns(2)
            for col,slot in zip([ic1,ic2,ic3,ic4],["breakfast","lunch","dinner","snack"]):
                with col: meal_card(ip["meals"][slot])

# ─── IMAGE SCAN ───────────────────────────────────────────────────
with tab_image:
    section_header("📸 Food Image Calorie Scanner",
                   subtitle="FoodImageAgent + PromptEngine + Gemini")

    info_strip(
        "📷 PromptEngine formats a structured vision prompt. "
        "FoodImageAgent sends it to Gemini API.",
        "blue"
    )

    uc, rc = st.columns([1, 2])
    valid = False

    with uc:
        uploaded = st.file_uploader(
            "JPG/PNG/WEBP · max 5MB",
            type=["jpg", "jpeg", "png", "webp"]
        )

        if uploaded:
            valid, err = orch.validate_image(uploaded)

            if not valid:
                st.error(err)

            else:
                st.image(
                    orch.resize_for_display(uploaded),
                    width = "stretch"
                )
                st.caption(f"📁 {uploaded.name} · {uploaded.size//1024} KB")

    with rc:
        if uploaded and valid:

            if st.button("🔍 Analyse with Gemini",
                         use_container_width=True):

                with st.spinner("Analysing…"):

                    b64, mime = orch.encode_image(uploaded)

                    result = orch.analyse_image(
                        b64,
                        mime,
                        user_profile=p
                    )
                    print("RESULT OBJECT :", result)
                if result.get("result", {}).get("success",False):

                    insight_card(result.get("result", {}).get("analysis",""))

                    info_strip(
                        "⚠️ Visual estimates — actual values vary.",
                        "amber"
                    )

                else:
                    st.error(result.get("error",{}).get("error", "Image analysis failed."))

        else:
            empty_state(
                "📷",
                "Upload a food photo",
                "Supported: JPG, PNG, WEBP · Max 5 MB"
            )
# ─── AI CHAT ──────────────────────────────────────────────────────
with tab_chat:
    section_header(
        "💬 AI Nutrition Coach",
        subtitle="ChatAssistantAgent · PromptEngine.chat_system() · Chat persists per user"
    )

    st.markdown(
        '<div class="chat-wrap"><div class="chat-header">'
        '<span class="chat-header-icon">🤖</span>'
        '<div><div class="chat-header-title">NutriAI Chat Assistant</div>'
        '<div class="chat-header-status"></div></div></div></div>',
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    sugs = [
        "💪 What to eat after gym?",
        "🥗 High-protein vegetarian breakfast?",
        "🏃 Reduce belly fat?",
        "🇮🇳 Best Indian foods for weight loss?"
    ]

    sc2 = st.columns(4)

    for i, sug in enumerate(sugs):
        if sc2[i].button(sug, key=f"sug_{i}", use_container_width=True):

            st.session_state.chat_messages.append({
                "role": "user",
                "content": sug
            })

            with st.spinner("Thinking…"):

                summary = (
                    MealPlanningAgent.get_plan_summary(st.session_state.daily_plan)
                    if st.session_state.daily_plan else ""
                )

                r = orch.chat(
                    st.session_state.chat_messages,
                    p,
                    summary,
                    user_id=user_id
                )

                res = r.get("result", {})

                success = res.get("success", False)
                reply = res.get("reply", "")
                error = res.get("error", "Chat failed")

                msg = reply if success else f"⚠️ {error}"

                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": msg
                })

            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    for msg in st.session_state.chat_messages:
        css = "chat-msg-user" if msg["role"] == "user" else "chat-msg-ai"
        pre = "👤" if msg["role"] == "user" else "🤖"

        st.markdown(
            f'<div class="{css}">{pre}&nbsp; {msg["content"]}</div>',
            unsafe_allow_html=True
        )

    user_input = st.chat_input(
        "Ask anything about nutrition, food, or your goals…"
    )

    if user_input:

        st.session_state.chat_messages.append({
            "role": "user",
            "content": user_input
        })

        with st.spinner("Thinking…"):

            summary = (
                MealPlanningAgent.get_plan_summary(st.session_state.daily_plan)
                if st.session_state.daily_plan else ""
            )

            r = orch.chat(
                st.session_state.chat_messages,
                p,
                summary,
                user_id=user_id
            )

            res = r.get("result", {})

            success = res.get("success", False)
            reply = res.get("reply", "")
            error = res.get("error", "Chat failed")

            msg = reply if success else f"⚠️ {error}"

            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": msg
            })

        st.rerun()

    if st.session_state.chat_messages:
        if st.button("🗑️ Clear Chat", key="clr"):

            orch.clear_chat_history(user_id)

            st.session_state.chat_messages = []

            st.rerun()

# ─── HEALTH INSIGHTS ─────────────────────────────────────────────
with tab_ins:
    section_header("💡 Personalised Health Insights",
                   subtitle="HealthInsightsAgent — rule-based, works without API key")

    if not ready or not p:
        empty_state("💡", "No insights yet", "Analyse your profile first.")

        section_header("🌿 Universal Tips")

        tips = [
            ("🥗", "Eat the Rainbow", "5 coloured veg daily."),
            ("💧", "Hydrate First", "Water before meals."),
            ("🌾", "Whole Grains", "Brown rice > white rice."),
            ("😴", "Sleep", "7–9h regulates hunger hormones."),
        ]

        for tip in tips:
            insight_card(f"<strong>{tip[0]} {tip[1]}</strong><br>{tip[2]}")

    else:

        ins = p.get("insights", {})

        # ---- Metrics Row ----
        sm1, sm2, sm3, sm4 = st.columns(4)
        # Get BMI safely
        bmi_value = p.get("bmi")

       # If BMI is missing or zero, compute it
        if not bmi_value or bmi_value == 0:
          weight = p.get("weight_kg")
          height = p.get("height_cm")
          if weight and height:
              bmi_value = round(weight / ((height/100)**2), 1)
          else:
              bmi_value = "N/A"

        sm1.metric("BMI", bmi_value, p.get("bmi_category",""))

        sm2.metric(
            "Calories",
            p.get("target_calories", p.get("tdee", "N/A")),
            "kcal/day",
        )

        sm3.metric(
            "Protein",
            f"{p.get('protein_g',0)}g",
            "daily",
        )

        sm4.metric(
            "Water",
            f"{p.get('water_litres',0)}L",
            "per day",
        )

        st.markdown("<br>", unsafe_allow_html=True)

        il, ir = st.columns(2)

        # ---------------- LEFT COLUMN ----------------
        with il:

            section_header("🔬 BMI Analysis")

            emoji = p.get("bmi_emoji", "⚖️")

            bmi_text = ins.get(
                "bmi_insight",
                "Your BMI suggests focusing on balanced nutrition, regular exercise, and adequate hydration."
            )

            insight_card(f"{emoji} {bmi_text}")

            # ---- Risk Alerts ----
            section_header("🚨 Risk Alerts")

            alerts = ins.get("risk_alerts", [])

            if not alerts:
                st.markdown('<div class="strip-green">✅ No major health risks detected.</div>', unsafe_allow_html=True)

            for a in alerts:
                color = "red" if ("🔴" in a or "⚠️" in a) else "green"
                st.markdown(
                    f'<div class="strip-{color}">{a}</div>',
                    unsafe_allow_html=True,
                )

            # ---- Macro Insights ----
            section_header("📊 Macro Insights")

            macros = ins.get("macro_insights", [])

            if not macros:
                insight_card("Maintain balanced protein, carbs, and healthy fats.", "amber")

            for t in macros:
                insight_card(t, "amber")

            # ---- Projection ----
            section_header("📈 Projection")

            proj = ins.get("weekly_projections", {})

            direction = proj.get("direction", "maintain")

            di = "📉" if direction == "loss" else "📈" if direction == "gain" else "⚖️"

            goal_label = (
                "Weight Loss"
                if direction == "loss"
                else "Muscle Gain"
                if direction == "gain"
                else "Maintenance"
            )

            insight_card(
                f"{di} <strong>{goal_label}</strong><br>{proj.get('note','Projection data unavailable')}",
                "purple",
            )

        # ---------------- RIGHT COLUMN ----------------
        with ir:

            section_header(f"🎯 Tips: {p.get('goal','Health')}")

            tips = ins.get("goal_tips", [])

            if not tips:
                tips = [
                    "Maintain a calorie balance aligned with your goal.",
                    "Exercise regularly (3–5 times per week).",
                    "Focus on whole foods and high protein intake.",
                ]

            for t in tips:
                st.markdown(
                    f'<div class="strip-green">{t}</div>',
                    unsafe_allow_html=True,
                )

            # ---- Best Foods ----
            section_header("🥗 Best Foods")

            foods = ins.get("food_recommendations", [])

            if foods:
                cols = st.columns(min(5, len(foods)))

                for i, food in enumerate(foods):
                    with cols[i % len(cols)]:
                        st.markdown(
                            f'''
                            <div class="food-showcase">
                                <div class="fs-icon">{food.get("emoji","🥗")}</div>
                                <div class="fs-name">{food.get("name","Healthy Food")}</div>
                                <div class="fs-note">{food.get("reason","Nutritious choice")}</div>
                            </div>
                            ''',
                            unsafe_allow_html=True,
                        )
            else:
                insight_card("Vegetables, fruits, lentils, nuts, eggs, whole grains.", "green")

            # ---- Limit Foods ----
            section_header("🚫 Limit")

            limits = ins.get("foods_to_limit", [])

            if not limits:
                limits = [
                    {"emoji": "🍟", "name": "Fried Foods", "reason": "High calories and unhealthy fats"},
                    {"emoji": "🥤", "name": "Sugary Drinks", "reason": "Adds excess sugar and calories"},
                ]

            for f in limits:
                st.markdown(
                    f'<div class="strip-amber">{f.get("emoji","⚠️")} <strong>{f.get("name","Food")}</strong> — {f.get("reason","Limit consumption")}</div>',
                    unsafe_allow_html=True,
                )

            # ---- Lifestyle ----
            section_header("🧘 Lifestyle")

            life = ins.get("lifestyle_tips", [])

            if not life:
                life = [
                    "Sleep 7–9 hours daily.",
                    "Stay physically active.",
                    "Drink sufficient water.",
                ]

            for t in life:
                st.markdown(
                    f'<div class="strip-green">{t}</div>',
                    unsafe_allow_html=True,
                )
# ─── ACCOUNT SETTINGS ────────────────────────────────────────────
with tab_acct:
    stats=orch.user_stats(user_id)
    section_header("⚙️ Account Settings",subtitle=f"Member since {stats.get('member_since','–')}")
    as1,as2,as3=st.columns(3)
    as1.metric("📅 Plans Generated",stats.get("plans_generated",0))
    as2.metric("💬 Chat Messages",  stats.get("chat_messages",0))
    as3.metric("🗓️ Member Since",   stats.get("member_since","–"))
    st.markdown("<br>",unsafe_allow_html=True)
    al,ar=st.columns(2)
    with al:
        st.markdown('<div class="account-card"><h3>👤 Profile Info</h3>',unsafe_allow_html=True)
        with st.form("edit_name_form"):
            new_name=st.text_input("Display Name",value=user.get("name",""))
            if st.form_submit_button("Save Name",use_container_width=True):
                if new_name.strip():
                    _DB.update_user_name(user_id,new_name.strip())
                    st.session_state.auth_user["name"]=new_name.strip()
                    st.success("✅ Name updated!"); st.rerun()
                else: st.error("Name cannot be empty.")
        st.markdown(f'<div style="font-size:0.8rem;color:var(--text-muted);margin-top:0.5rem">📧 {user.get("email","")}</div>',unsafe_allow_html=True)
        st.markdown("</div>",unsafe_allow_html=True)
        st.markdown('<div class="account-card"><h3>🔐 Change Password</h3>',unsafe_allow_html=True)
        with st.form("change_pw_form"):
            old_pw=st.text_input("Current Password",type="password")
            new_pw=st.text_input("New Password",type="password")
            new_pw2=st.text_input("Confirm New",type="password")
            if st.form_submit_button("Update Password",use_container_width=True):
                ok,msg=_AUTH.change_password(user_id,old_pw,new_pw,new_pw2)
                st.success(msg) if ok else st.error(msg)
        st.markdown("</div>",unsafe_allow_html=True)
    with ar:
        st.markdown('<div class="account-card"><h3>📅 Recent Meal Plans</h3>',unsafe_allow_html=True)
        render_meal_history(orch.get_recent_plans(user_id,limit=7))
        st.markdown("</div>",unsafe_allow_html=True)
        st.markdown('<div class="account-card" style="border-color:#FECACA"><h3>⚠️ Danger Zone</h3>',unsafe_allow_html=True)
        with st.expander("🗑️ Delete Account (permanent)"):
            st.warning("Permanently deletes your account, profile, history, and chat.")
            confirm_del=st.text_input("Type your email to confirm:",key="del_confirm")
            if st.button("Delete My Account",key="del_acct"):
                if confirm_del.strip().lower()==user.get("email","").lower():
                    _DB.delete_user(user_id); logout(); st.success("Account deleted."); st.rerun()
                else: st.error("Email does not match.")
        st.markdown("</div>",unsafe_allow_html=True)

# ─── FOOTER ───────────────────────────────────────────────────────
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(
    '<div style="text-align:center;color:#6B7280;font-size:0.75rem;padding:0.6rem 0">'
    '🥗 NutriAI · AI-Powered Nutrition Guidance · Eat Better Every Day'
    '</div>',
    unsafe_allow_html=True
)
